# MCP PostgreSQL Server

Generic, configurable [Model Context Protocol](https://modelcontextprotocol.io) server for interacting with PostgreSQL.

## Features

| Tool | Description |
|------|-------------|
| `ping` | Connectivity check + server version |
| `query` | Run SQL (`$1`, `$2`, … params supported) |
| `list_schemas` | List non-system schemas |
| `list_tables` | List tables/views in a schema |
| `describe_table` | Columns, PKs, FKs |
| `list_indexes` | Indexes for a table |
| `explain_query` | `EXPLAIN` / optional `EXPLAIN ANALYZE` |

**Safety defaults:** read-only mode, single-statement only, statement timeout, max row cap, optional schema allowlist.

## Requirements

- Node.js 18+
- A reachable PostgreSQL instance

## Setup

```bash
npm install
npm run build
```

Copy `.env.example` to `.env` and edit credentials, or pass env vars via your MCP client config.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_CONNECTION_STRING` | — | Full URL; preferred when set |
| `POSTGRES_HOST` | `localhost` | Host |
| `POSTGRES_PORT` | `5432` | Port |
| `POSTGRES_USER` | `postgres` | User |
| `POSTGRES_PASSWORD` | `""` | Password |
| `POSTGRES_DATABASE` | `postgres` | Database |
| `POSTGRES_SSL` | `false` | `true` / `false` / `require` |
| `POSTGRES_POOL_MAX` | `5` | Pool size |
| `POSTGRES_READONLY` | `true` | Block writes / DDL / `EXPLAIN ANALYZE` |
| `POSTGRES_ALLOWED_SCHEMAS` | _(all)_ | Comma-separated allowlist |
| `POSTGRES_QUERY_TIMEOUT_MS` | `30000` | Statement timeout |
| `POSTGRES_MAX_ROWS` | `1000` | Result row cap |
| `POSTGRES_CONFIG_PATH` | — | Optional JSON config file |

Env vars override values from the config file. See `config.example.json`.

## Run

```bash
# production (compiled)
npm start

# development (tsx)
npm run dev
```

The server speaks MCP over **stdio** (stdout is reserved for protocol framing; logs go to stderr).

## Cursor / MCP client

Add to your MCP config (e.g. Cursor `mcp.json`):

```json
{
  "mcpServers": {
    "postgres": {
      "command": "node",
      "args": ["/absolute/path/to/mcp-server-demo/dist/index.js"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@localhost:5432/mydb",
        "POSTGRES_READONLY": "true",
        "POSTGRES_MAX_ROWS": "500"
      }
    }
  }
}
```

Or during development:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["tsx", "/absolute/path/to/mcp-server-demo/src/index.ts"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@localhost:5432/mydb"
      }
    }
  }
}
```

## Read-only vs writes

- Default: `POSTGRES_READONLY=true` — only `SELECT` / `WITH` / `EXPLAIN` (no `ANALYZE`) / `SHOW`.
- Set `POSTGRES_READONLY=false` to allow DML/DDL (still single-statement; use a least-privilege DB user).

## License

MIT
