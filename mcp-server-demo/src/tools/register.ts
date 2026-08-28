import { z } from "zod";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type pg from "pg";
import type { AppConfig } from "../config.js";
import { runQuery } from "../db/query.js";
import {
  assertSafeIdentifier,
  assertSchemaAllowed,
  assertSingleStatement,
} from "../db/guards.js";

function textResult(payload: unknown) {
  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify(payload, null, 2),
      },
    ],
  };
}

function errorResult(err: unknown) {
  const message = err instanceof Error ? err.message : String(err);
  return {
    content: [{ type: "text" as const, text: message }],
    isError: true as const,
  };
}

export function registerTools(
  server: McpServer,
  pool: pg.Pool,
  config: AppConfig,
): void {
  server.registerTool(
    "ping",
    {
      title: "Ping",
      description: "Check PostgreSQL connectivity and return server version.",
      annotations: { readOnlyHint: true, destructiveHint: false },
    },
    async () => {
      try {
        const result = await pool.query(
          "SELECT current_database() AS database, current_user AS user, version() AS version, now() AS now",
        );
        return textResult(result.rows[0]);
      } catch (err) {
        return errorResult(err);
      }
    },
  );

  server.registerTool(
    "query",
    {
      title: "Query",
      description:
        "Execute a SQL statement. Read-only by default (SELECT/WITH/EXPLAIN/SHOW). " +
        "Optional positional parameters use $1, $2, ... Placeholders. Results are capped by POSTGRES_MAX_ROWS.",
      inputSchema: {
        sql: z.string().min(1).describe("SQL statement to execute"),
        params: z
          .array(z.unknown())
          .optional()
          .describe("Optional positional query parameters ($1, $2, ...)"),
      },
      annotations: {
        readOnlyHint: config.readonly,
        destructiveHint: !config.readonly,
      },
    },
    async ({ sql, params }) => {
      try {
        const result = await runQuery(pool, config, sql, params ?? []);
        return textResult(result);
      } catch (err) {
        return errorResult(err);
      }
    },
  );

  server.registerTool(
    "list_schemas",
    {
      title: "List schemas",
      description:
        "List non-system schemas visible to the current user. Honors POSTGRES_ALLOWED_SCHEMAS when set.",
      annotations: { readOnlyHint: true, destructiveHint: false },
    },
    async () => {
      try {
        const result = await pool.query(`
          SELECT nspname AS schema_name,
                 pg_catalog.pg_get_userbyid(nspowner) AS owner
          FROM pg_catalog.pg_namespace
          WHERE nspname NOT LIKE 'pg_%'
            AND nspname <> 'information_schema'
          ORDER BY nspname
        `);
        let schemas = result.rows as Array<{ schema_name: string; owner: string }>;
        if (config.allowedSchemas.length > 0) {
          const allow = new Set(config.allowedSchemas);
          schemas = schemas.filter((s) => allow.has(s.schema_name));
        }
        return textResult({ schemas });
      } catch (err) {
        return errorResult(err);
      }
    },
  );

  server.registerTool(
    "list_tables",
    {
      title: "List tables",
      description: "List tables and views in a schema (default: public).",
      inputSchema: {
        schema: z
          .string()
          .optional()
          .describe("Schema name (default: public)"),
      },
      annotations: { readOnlyHint: true, destructiveHint: false },
    },
    async ({ schema }) => {
      try {
        const schemaName = schema ?? "public";
        assertSafeIdentifier(schemaName, "schema");
        assertSchemaAllowed(schemaName, config.allowedSchemas);

        const result = await pool.query(
          `
          SELECT table_schema,
                 table_name,
                 table_type
          FROM information_schema.tables
          WHERE table_schema = $1
          ORDER BY table_type, table_name
          `,
          [schemaName],
        );
        return textResult({ schema: schemaName, tables: result.rows });
      } catch (err) {
        return errorResult(err);
      }
    },
  );

  server.registerTool(
    "describe_table",
    {
      title: "Describe table",
      description:
        "Describe columns, primary keys, and foreign keys for a table.",
      inputSchema: {
        table: z.string().min(1).describe("Table name"),
        schema: z
          .string()
          .optional()
          .describe("Schema name (default: public)"),
      },
      annotations: { readOnlyHint: true, destructiveHint: false },
    },
    async ({ table, schema }) => {
      try {
        const schemaName = schema ?? "public";
        assertSafeIdentifier(schemaName, "schema");
        assertSafeIdentifier(table, "table");
        assertSchemaAllowed(schemaName, config.allowedSchemas);

        const columns = await pool.query(
          `
          SELECT column_name,
                 data_type,
                 udt_name,
                 is_nullable,
                 column_default,
                 character_maximum_length,
                 numeric_precision,
                 numeric_scale,
                 ordinal_position
          FROM information_schema.columns
          WHERE table_schema = $1 AND table_name = $2
          ORDER BY ordinal_position
          `,
          [schemaName, table],
        );

        if (columns.rows.length === 0) {
          throw new Error(
            `Table "${schemaName}.${table}" not found or not visible.`,
          );
        }

        const primaryKeys = await pool.query(
          `
          SELECT kcu.column_name, kcu.ordinal_position
          FROM information_schema.table_constraints tc
          JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
           AND tc.table_schema = kcu.table_schema
          WHERE tc.constraint_type = 'PRIMARY KEY'
            AND tc.table_schema = $1
            AND tc.table_name = $2
          ORDER BY kcu.ordinal_position
          `,
          [schemaName, table],
        );

        const foreignKeys = await pool.query(
          `
          SELECT
            tc.constraint_name,
            kcu.column_name,
            ccu.table_schema AS foreign_table_schema,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
          FROM information_schema.table_constraints tc
          JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
           AND tc.table_schema = kcu.table_schema
          JOIN information_schema.constraint_column_usage ccu
            ON ccu.constraint_name = tc.constraint_name
           AND ccu.table_schema = tc.table_schema
          WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = $1
            AND tc.table_name = $2
          ORDER BY tc.constraint_name, kcu.ordinal_position
          `,
          [schemaName, table],
        );

        return textResult({
          schema: schemaName,
          table,
          columns: columns.rows,
          primary_keys: primaryKeys.rows.map((r) => r.column_name),
          foreign_keys: foreignKeys.rows,
        });
      } catch (err) {
        return errorResult(err);
      }
    },
  );

  server.registerTool(
    "list_indexes",
    {
      title: "List indexes",
      description: "List indexes for a table.",
      inputSchema: {
        table: z.string().min(1).describe("Table name"),
        schema: z
          .string()
          .optional()
          .describe("Schema name (default: public)"),
      },
      annotations: { readOnlyHint: true, destructiveHint: false },
    },
    async ({ table, schema }) => {
      try {
        const schemaName = schema ?? "public";
        assertSafeIdentifier(schemaName, "schema");
        assertSafeIdentifier(table, "table");
        assertSchemaAllowed(schemaName, config.allowedSchemas);

        const result = await pool.query(
          `
          SELECT
            i.relname AS index_name,
            am.amname AS index_type,
            ix.indisunique AS is_unique,
            ix.indisprimary AS is_primary,
            pg_get_indexdef(ix.indexrelid) AS definition
          FROM pg_class t
          JOIN pg_namespace n ON n.oid = t.relnamespace
          JOIN pg_index ix ON t.oid = ix.indrelid
          JOIN pg_class i ON i.oid = ix.indexrelid
          JOIN pg_am am ON i.relam = am.oid
          WHERE n.nspname = $1
            AND t.relname = $2
          ORDER BY i.relname
          `,
          [schemaName, table],
        );

        return textResult({
          schema: schemaName,
          table,
          indexes: result.rows,
        });
      } catch (err) {
        return errorResult(err);
      }
    },
  );

  server.registerTool(
    "explain_query",
    {
      title: "Explain query",
      description:
        "Run EXPLAIN on a SQL statement. ANALYZE is optional and disabled when read-only mode is on.",
      inputSchema: {
        sql: z.string().min(1).describe("SQL to explain"),
        analyze: z
          .boolean()
          .optional()
          .describe("If true, run EXPLAIN ANALYZE (requires write mode)"),
        format: z
          .enum(["text", "json"])
          .optional()
          .describe("Explain output format (default: json)"),
      },
      annotations: { readOnlyHint: true, destructiveHint: false },
    },
    async ({ sql, analyze, format }) => {
      try {
        assertSingleStatement(sql);

        const useAnalyze = analyze === true;
        if (useAnalyze && config.readonly) {
          throw new Error(
            "EXPLAIN ANALYZE is disabled in read-only mode. Set POSTGRES_READONLY=false or omit analyze.",
          );
        }

        const fmt = format ?? "json";
        const options = [
          useAnalyze ? "ANALYZE" : null,
          `FORMAT ${fmt.toUpperCase()}`,
        ]
          .filter(Boolean)
          .join(", ");

        const explainSql = `EXPLAIN (${options}) ${sql}`;
        // Bypass read-only classifier for EXPLAIN wrapper; ANALYZE already gated above.
        const client = await pool.connect();
        try {
          await client.query(`SET statement_timeout = ${config.queryTimeoutMs}`);
          const result = await client.query(explainSql);
          return textResult({
            analyze: useAnalyze,
            format: fmt,
            plan: result.rows,
          });
        } finally {
          client.release();
        }
      } catch (err) {
        return errorResult(err);
      }
    },
  );
}
