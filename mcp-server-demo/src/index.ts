#!/usr/bin/env node
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { loadConfig } from "./config.js";
import { createPool } from "./db/pool.js";
import { createServer } from "./server.js";

async function main(): Promise<void> {
  const config = await loadConfig();
  const pool = createPool(config);
  const server = createServer(pool, config);
  const transport = new StdioServerTransport();

  const shutdown = async (code = 0) => {
    try {
      await server.close();
    } catch {
      // ignore
    }
    try {
      await pool.end();
    } catch {
      // ignore
    }
    process.exit(code);
  };

  process.on("SIGINT", () => void shutdown(0));
  process.on("SIGTERM", () => void shutdown(0));

  await server.connect(transport);
}

main().catch((err) => {
  const message = err instanceof Error ? err.message : String(err);
  // stderr only — stdout is reserved for MCP stdio framing
  console.error(`[mcp-postgres] fatal: ${message}`);
  process.exit(1);
});
