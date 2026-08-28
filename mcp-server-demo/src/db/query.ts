import type pg from "pg";
import type { AppConfig } from "../config.js";
import {
  assertReadOnly,
  assertSingleStatement,
} from "./guards.js";

export interface QueryResultPayload {
  columns: string[];
  rows: Record<string, unknown>[];
  rowCount: number;
  truncated: boolean;
  command: string;
}

export async function runQuery(
  pool: pg.Pool,
  config: AppConfig,
  sql: string,
  params: unknown[] = [],
): Promise<QueryResultPayload> {
  assertSingleStatement(sql);
  if (config.readonly) {
    assertReadOnly(sql);
  }

  const client = await pool.connect();
  try {
    await client.query(`SET statement_timeout = ${config.queryTimeoutMs}`);
    const result = await client.query(sql, params);

    const columns = result.fields.map((f) => f.name);
    const truncated = result.rows.length > config.maxRows;
    const limitedRows = truncated
      ? result.rows.slice(0, config.maxRows)
      : result.rows;

    const rows = limitedRows.map((row) => {
      const out: Record<string, unknown> = {};
      for (const col of columns) {
        out[col] = serializeValue(row[col]);
      }
      return out;
    });

    return {
      columns,
      rows,
      rowCount: result.rowCount ?? rows.length,
      truncated,
      command: result.command,
    };
  } finally {
    client.release();
  }
}

function serializeValue(value: unknown): unknown {
  if (value === null || value === undefined) return value;
  if (typeof value === "bigint") return value.toString();
  if (Buffer.isBuffer(value)) {
    return { type: "buffer", base64: value.toString("base64"), length: value.length };
  }
  if (value instanceof Date) return value.toISOString();
  if (typeof value === "object") {
    // pg may return arrays / JSON already parsed
    try {
      return JSON.parse(JSON.stringify(value));
    } catch {
      return String(value);
    }
  }
  return value;
}
