# SQL Flamegraph

SQL Flamegraph is a powerful visualization tool for analyzing and optimizing MySQL query execution plans. It transforms MySQL's EXPLAIN ANALYZE output into intuitive flame graphs, helping developers and database administrators better understand and optimize query performance.

## Features

- Convert MySQL EXPLAIN ANALYZE output into interactive flame graphs
- User-friendly web interface
- RESTful API support
- Automatic query history tracking
- Docker deployment support

## Installation

### Prerequisites

- Python 3.7+
- MySQL 8.0+
- Perl (for flame graph generation)

### Method 1: Direct Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sqlflamegraph.git
cd sqlflamegraph
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install fastapi uvicorn jinja2 mysql-connector-python
```

### Method 2: Using Docker

```bash
docker build -t sqlflamegraph .
docker run -p 8000:8000 sqlflamegraph
```

## Usage

1. Start the service:
```bash
python mysqlflamegraph.py
```

2. Access the web interface:
Open your browser and visit http://localhost:8000

3. Get query execution plan:
```sql
EXPLAIN ANALYZE SELECT * FROM your_table WHERE ...;
```

4. Paste the execution plan output into the web interface to generate the flame graph

## API Usage

```bash
curl -X POST http://localhost:8000/api/sqlflamegraph \
     -H "Content-Type: application/json" \
     -d '{"explain": "your EXPLAIN ANALYZE output here"}'
```

## Contributing

Pull requests and issues are welcome!

## License

MIT License

## Acknowledgments

- [Brendan Gregg's FlameGraph](https://github.com/brendangregg/FlameGraph) - Flame graph generation tool
- FastAPI - Web framework 