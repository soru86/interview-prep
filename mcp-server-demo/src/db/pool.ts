import pg from "pg";
import type { AppConfig } from "../config.js";

const { Pool } = pg;

export function createPool(config: AppConfig): pg.Pool {
  const ssl =
    config.ssl === false
      ? undefined
      : config.ssl === "require" || config.ssl === true
        ? { rejectUnauthorized: false }
        : undefined;

  if (config.connectionString) {
    return new Pool({
      connectionString: config.connectionString,
      max: config.poolMax,
      ssl,
      statement_timeout: config.queryTimeoutMs,
      application_name: "mcp-postgres-server",
    });
  }

  return new Pool({
    host: config.host,
    port: config.port,
    user: config.user,
    password: config.password,
    database: config.database,
    max: config.poolMax,
    ssl,
    statement_timeout: config.queryTimeoutMs,
    application_name: "mcp-postgres-server",
  });
}
