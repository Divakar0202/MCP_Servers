# DB Tool OpenClaw

Read-only database access API for AI agent platforms such as OpenClaw.

All write operations (INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, etc.) are
blocked at the query-validation layer **before** they ever reach the database.

## Project Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application and endpoints
│   ├── database.py      # SQLAlchemy engine and session factory
│   ├── models.py        # ORM model placeholder
│   ├── schemas.py       # Pydantic request/response models
│   ├── db_tools.py      # Read-only database tool functions
│   ├── security.py      # Query validation and identifier sanitisation
│   └── config.py        # Environment-based configuration
│
├── .env.example         # Example environment variables
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container build file
└── README.md            # This file
```

## Prerequisites

- Python 3.11+
- A running PostgreSQL instance

## Configuration

Copy the example env file and fill in your database credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### Optional variables

| Variable          | Default              | Description                     |
|-------------------|----------------------|---------------------------------|
| `DB_POOL_SIZE`    | 5                    | SQLAlchemy connection pool size |
| `DB_MAX_OVERFLOW` | 10                   | Max overflow connections        |
| `DB_POOL_TIMEOUT` | 30                   | Pool checkout timeout (seconds) |
| `APP_TITLE`       | DB Tool OpenClaw     | Shown in OpenAPI docs           |
| `APP_VERSION`     | 1.0.0                | Shown in OpenAPI docs           |
| `LOG_LEVEL`       | INFO                 | Python logging level            |

## Running Locally

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The interactive API docs are available at `http://localhost:8000/docs`.

## Running with Docker

```bash
# Build the image
docker build -t db-tool-openclaw .

# Run the container
docker run -d \
  --name db-tool-openclaw \
  -p 8000:8000 \
  --env-file .env \
  db-tool-openclaw
```

## API Endpoints

### System

| Method | Path      | Description    |
|--------|-----------|----------------|
| GET    | `/health` | Liveness probe |

### Tables

| Method | Path                            | Description                          |
|--------|---------------------------------|--------------------------------------|
| GET    | `/tables`                       | List all table names                 |
| GET    | `/tables/{table_name}/schema`   | Column names, types, and constraints |
| GET    | `/tables/{table_name}/count`    | Row count                            |
| GET    | `/tables/{table_name}/sample`   | Sample rows (default 10)             |
| GET    | `/tables/{table_name}/data`     | Paginated rows (limit + offset)      |
| GET    | `/tables/{table_name}/search`   | Filter rows by column value (ILIKE)  |

### Query

| Method | Path     | Description                             |
|--------|----------|-----------------------------------------|
| POST   | `/query` | Execute a validated SELECT-only query   |

## Example API Requests

### List all tables

```bash
curl http://localhost:8000/tables
```

```json
{
  "tables": ["users", "orders", "products"]
}
```

### Describe a table

```bash
curl http://localhost:8000/tables/users/schema
```

```json
{
  "table_name": "users",
  "columns": [
    { "name": "id", "type": "INTEGER", "nullable": false, "default": null, "primary_key": true },
    { "name": "email", "type": "VARCHAR(255)", "nullable": false, "default": null, "primary_key": false }
  ]
}
```

### Get row count

```bash
curl http://localhost:8000/tables/users/count
```

```json
{ "table_name": "users", "count": 1542 }
```

### Get sample rows

```bash
curl "http://localhost:8000/tables/users/sample?limit=5"
```

### Paginated data

```bash
curl "http://localhost:8000/tables/orders/data?limit=20&offset=40"
```

### Search a table

```bash
curl "http://localhost:8000/tables/users/search?column=email&value=gmail"
```

### Execute a safe query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT id, email FROM users WHERE id < 10"}'
```

### Rejected (unsafe) query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "DELETE FROM users WHERE id = 1"}'
```

```json
{ "detail": "Only SELECT queries are allowed. Got: DELETE" }
```

## Security

- All queries are validated before execution
- Only `SELECT` and `WITH` (CTE) statements are permitted
- Multiple statements (`;`) are rejected
- Forbidden keywords are scanned across the entire query body
- Table and column names are sanitised to prevent SQL injection
- Connection pooling with pre-ping health checks

## License

MIT
