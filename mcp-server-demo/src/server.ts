import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type pg from "pg";
import type { AppConfig } from "./config.js";
import { registerTools } from "./tools/register.js";

export function createServer(pool: pg.Pool, config: AppConfig): McpServer {
  const server = new McpServer({
    name: "mcp-postgres-server",
    version: "1.0.0",
  });

  registerTools(server, pool, config);
  return server;
}
