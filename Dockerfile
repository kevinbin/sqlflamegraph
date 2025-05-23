# 使用官方 Python 镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    perl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件到容器中
COPY flamegraph.pl .
COPY mysqlflamegraph.py .
COPY templates/index.html ./templates/
COPY database.py .
# 暴露应用运行的端口
EXPOSE 80

# 启动 Flask 应用
CMD ["python", "mysqlflamegraph.py", "--server", "--host", "0.0.0.0", "--port", "80"]