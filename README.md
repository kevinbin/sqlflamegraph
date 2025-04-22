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
git clone https://github.com/kevinbin/sqlflamegraph.git
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
pip install -r requirements.txt
```

4. Set up MySQL:
```bash
mysql -u your_username -p < init.sql
```

### Method 2: Using Docker Compose

1. Clone the repository:
```bash
git clone https://github.com/kevinbin/sqlflamegraph.git
cd sqlflamegraph
```

2. Create a `.env` file (optional):
```bash
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
```

3. Start the services:
```bash
docker-compose up -d
```

The application will be available at http://localhost:8000

To stop the services:
```bash
docker-compose down
```

To stop the services and remove all data:
```bash
docker-compose down -v
```

## Usage

1. Start the service:
```bash
python mysqlflamegraph.py  # for direct installation
# or
docker-compose up -d  # for docker installation
```

2. Access the web interface:
Open your browser and visit http://localhost:8000

3. Get query execution plan from MySQL:
```sql
EXPLAIN ANALYZE SELECT * FROM your_table WHERE ...;
```

4. Paste the execution plan output into the web interface to generate the flame graph

## API Usage

### Generate Flame Graph

```bash
curl -X POST http://localhost:8000/api/sqlflamegraph \
     -H "Content-Type: application/json" \
     -d '{"explain": "your EXPLAIN ANALYZE output here"}'
```

### Response

Returns an SVG flame graph that can be viewed in any modern web browser.

## Environment Variables

- `MYSQL_HOST`: MySQL server hostname (default: localhost)
- `MYSQL_USER`: MySQL username
- `MYSQL_PASSWORD`: MySQL password
- `MYSQL_DATABASE`: MySQL database name (default: sqlflamegraph)
- `MYSQL_PORT`: MySQL port (default: 3306)
- `MYSQL_ROOT_PASSWORD`: MySQL root password (Docker only)

## Contributing

Pull requests and issues are welcome!

## License

MIT License

## Acknowledgments

- [Brendan Gregg's FlameGraph](https://github.com/brendangregg/FlameGraph) - Flame graph generation tool
- FastAPI - Web framework 