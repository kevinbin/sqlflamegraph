#!/usr/bin/env python3

import sys
import re
import os
import argparse
import subprocess
import asyncio
from typing import List, Tuple, Optional

from fastapi import FastAPI, Form, Request
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates
import uvicorn

# Import database module
import database


# ===== MySQL Flamegraph Parser =====

class Node:
    def __init__(self, id: int, level: int, description: str, time: float):
        self.id = id
        self.level = level
        self.description = description
        self.time = time
        self.parent: Optional['Node'] = None
        self.children: List['Node'] = []


def clean_mysql_output(line: str) -> str:
    """清理MySQL输出中的表头和其他无关信息"""
    # 移除MySQL表头
    line = re.sub(r'\*+\s*\d+\.\s*row\s*\*+', '', line)

    # 移除EXPLAIN前缀
    line = re.sub(r'^EXPLAIN:\s*', '', line)

    # 移除所有 '->' 符号
    line = line.replace('->', '')

    return line


def extract_time(line: str) -> float:
    """从行中提取执行时间"""
    # 尝试匹配 actual time=X..Y 格式
    time_match = re.search(r'actual time=([0-9.]+)\.\.([0-9.]+)', line)
    if time_match:
        end_time = float(time_match.group(2))
        # 查找 loops
        loops_match = re.search(r'loops=(\d+)', line)
        loops = int(loops_match.group(1)) if loops_match else 1
        return end_time * loops * 1000  # 转换为毫秒
    return 0.0


def parse_explain_line(line: str, verbose: bool) -> Optional[Tuple[int, str, float]]:
    """解析EXPLAIN ANALYZE输出行"""
    try:
        # 清理MySQL输出
        line = clean_mysql_output(line)
        # 如果行为空或不是执行计划行，跳过
        if not line.strip():
            return None

        # 计算缩进级别（通过4个空格数量）
        indent_match = re.match(r'^( {4,})', line)
        indent = (len(indent_match.group(1)) // 4 + 1) if indent_match else 1

        # 提取时间
        time = extract_time(line)

        # 清理描述文本
        description = line
        # 移除 cost 信息
        description = re.sub(r'\(cost[^)]+\)', '', description)
        # 移除 actual time 信息
        description = re.sub(r'\(actual time[^)]+\)', '', description)
        # 移除分号信息
        description = re.sub(r';', '', description)
        # 移除前导空格
        description = description.lstrip()
        # 移除多余空格
        description = re.sub(r'\s+', ' ', description)
        description = description.strip()

        # 如果描述为空，跳过
        if not description:
            return None

        # 调试输出
        if verbose:
            print(f"Parsed line: level={indent}, description='{description}', time={time}")

        return indent, description, time

    except Exception as e:
        print(f"Warning: Error parsing line: {line}", file=sys.stderr)
        print(f"Error details: {str(e)}", file=sys.stderr)
        return None


def build_tree(nodes: List[Node], verbose: bool) -> List[Node]:
    """构建节点树结构"""
    if not nodes:
        return []

    # 使用栈来跟踪当前路径
    stack = []
    root = nodes[0]
    stack.append(root)

    for node in nodes[1:]:
        while stack and stack[-1].level >= node.level:
            stack.pop()

        if stack:
            parent = stack[-1]
            node.parent = parent
            parent.children.append(node)

        stack.append(node)

    # 调试输出
    if verbose:
        print("\nTree structure built:")
        for node in nodes:
            print(f"Node {node.id}: level={node.level}, description='{node.description}', time={node.time}")

    # 返回所有叶子节点
    return [node for node in nodes if not node.children]


def get_node_path(node: Node) -> List[Node]:
    """获取从根到当前节点的路径"""
    path = []
    current = node
    while current:
        path.insert(0, current)
        current = current.parent
    return path


def format_output_line(path: List[Node]) -> str:
    """格式化输出行，使用分号分隔层级"""
    parts = []
    for node in path:
        # parts.append(f"{node.id} {node.description}")
        parts.append(f"{node.description}")

    return ";".join(parts)


def process_explain_output(lines: List[str], verbose: bool) -> List[str]:
    """处理EXPLAIN ANALYZE输出并生成火焰图格式"""
    nodes: List[Node] = []

    line_num = 0
    for line in lines:
        if not line.strip():
            continue

        parse_result = parse_explain_line(line, verbose)
        if parse_result is None:
            continue

        line_num += 1
        level, description, time = parse_result

        # 跳过空描述或无意义的行
        if not description or description.isspace():
            continue

        nodes.append(Node(line_num, level, description, time))

    # 构建树结构
    build_tree(nodes, verbose)

    # 生成输出
    result = []
    processed_paths = set()

    # 为每个节点生成从根到当前节点的路径
    for node in nodes:
        path = get_node_path(node)
        path_str = format_output_line(path)
        if path_str not in processed_paths:
            result.append(f"{path_str} {int(node.time)}")
            processed_paths.add(path_str)

    return result


def generate_svg_from_explain(explain_text: str, sql_id: str = "explain", verbose: bool = False) -> str:
    """Generate SVG from EXPLAIN ANALYZE output"""
    lines = explain_text.splitlines()
    output = process_explain_output(lines, verbose)

    # Call flamegraph.pl to generate SVG
    flamegraph_script = "./flamegraph.pl"
    if not os.path.isfile(flamegraph_script):
        raise FileNotFoundError(
            f"Not found {flamegraph_script}. Please download "
            "https://github.com/brendangregg/FlameGraph/blob/master/flamegraph.pl "
            "and grant it execution permission."
        )

    process = subprocess.run(
        [flamegraph_script, "--title", sql_id, "--countname", "milliseconds",
         "--width", "1000", "--height", "20", "--fontsize", "13",
         "--nametype", "Operator ->"],
        input='\n'.join(output), text=True, stdout=subprocess.PIPE
    )

    return process.stdout


# ===== FastAPI Web Application =====

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/sqlflamegraph")
async def generate_svg(request: Request, text: str = Form(default="")):
    if not text:
        return Response("No explain provided", status_code=400)

    try:
        # Get client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        # # Save to database

        # Generate SVG
        svg_output = generate_svg_from_explain(text)
        # Start async database save without waiting
        asyncio.create_task(database.save_explain(text, ip_address, user_agent))
        return Response(svg_output, media_type="image/svg+xml")

    except Exception as e:
        return Response(f"Error generating flamegraph: {str(e)}", status_code=500)


# Add the API endpoint for direct JSON input
@app.post("/api/sqlflamegraph")
async def api_sqlflamegraph(request: Request):
    """
    API endpoint that accepts raw MySQL EXPLAIN ANALYZE output as request body
    and returns an SVG flamegraph.

    Example usage:
    mysql -BNEe 'explain analyze sql_statement' | curl --data-binary @- http://localhost/api/sqlflamegraph > explain.svg
    """
    try:
        # 读取原始请求体数据
        data = await request.body()
        data_str = data.decode('utf-8')

        if not data_str:
            return Response("No explain data provided", status_code=400)

        # Get client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # Generate SVG
        svg_output = generate_svg_from_explain(data_str)
        # Start async database save without waiting
        asyncio.create_task(database.save_explain(data_str, ip_address, user_agent))
        return Response(svg_output, media_type="image/svg+xml")
    except Exception as e:
        return Response(f"Error generating flamegraph: {str(e)}", status_code=500)


# ===== Command-line Interface =====

def main():
    parser = argparse.ArgumentParser(
        description="Process EXPLAIN ANALYZE output and generate a flamegraph.",
        usage="""
    mysql -BNEe 'explain analyze <sql>' > explain.txt && ./mysqlflamegraph.py explain.txt
    or
    mysql -BNEe 'explain analyze <sql>' | ./mysqlflamegraph.py
    or
    Start web server: ./mysqlflamegraph.py --server

    API Usage:
    mysql -BNEe 'explain analyze <sql>' | curl -s --json @- http://localhost/api/sqlflamegraph > explain.svg
    """
    )
    parser.add_argument('explain_file', type=str, nargs='?',
                        help='The file containing EXPLAIN ANALYZE output (optional)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--sql_id', type=str, default='explain',
                        help='SQL ID for the flamegraph title and filename (optional)')
    parser.add_argument('--server', action='store_true',
                        help='Start web server')
    parser.add_argument('--host', type=str, default="0.0.0.0",
                        help='Host to bind the server to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000,
                        help='Port to bind the server to (default: 8000)')

    args = parser.parse_args()

    # Start web server if --server flag is specified
    if args.server:
        print(f"Starting web server on http://{args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)
        return

    verbose = args.verbose
    sql_id = args.sql_id

    # Process from file or stdin
    if args.explain_file:
        try:
            with open(args.explain_file, 'r') as f:
                explain_text = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.explain_file}' not found.", file=sys.stderr)
            sys.exit(1)
    else:
        # Read from standard input
        explain_text = sys.stdin.read()

    try:
        svg_output = generate_svg_from_explain(explain_text, sql_id, verbose)

        # Write SVG to file and stdout
        svg_filename = f"{sql_id}.svg"
        with open(svg_filename, 'w') as svg_file:
            svg_file.write(svg_output)

        print(svg_output)
    except Exception as e:
        print(f"{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
