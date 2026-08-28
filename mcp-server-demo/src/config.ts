export type SslMode = boolean | "require";

export interface AppConfig {
  /** Prefer connection string when set; otherwise use discrete fields. */
  connectionString?: string;
  host: string;
  port: number;
  user: string;
  password: string;
  database: string;
  ssl: SslMode;
  poolMax: number;
  /** When true, only allow read-only SQL (SELECT/WITH/EXPLAIN/SHOW). */
  readonly: boolean;
  /** Empty = all schemas allowed. */
  allowedSchemas: string[];
  queryTimeoutMs: number;
  maxRows: number;
}

function parseBoolean(value: string | undefined, fallback: boolean): boolean {
  if (value === undefined || value === "") return fallback;
  const normalized = value.trim().toLowerCase();
  if (["1", "true", "yes", "on"].includes(normalized)) return true;
  if (["0", "false", "no", "off"].includes(normalized)) return false;
  return fallback;
}

function parseSsl(value: string | undefined): SslMode {
  if (value === undefined || value === "") return false;
  const normalized = value.trim().toLowerCase();
  if (normalized === "require") return "require";
  return parseBoolean(value, false);
}

function parseCsv(value: string | undefined): string[] {
  if (!value?.trim()) return [];
  return value
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

function parsePositiveInt(
  value: string | undefined,
  fallback: number,
  label: string,
): number {
  if (value === undefined || value === "") return fallback;
  const n = Number(value);
  if (!Number.isFinite(n) || n <= 0 || !Number.isInteger(n)) {
    throw new Error(`Invalid ${label}: expected positive integer, got "${value}"`);
  }
  return n;
}

type FileConfig = Partial<{
  connectionString: string;
  host: string;
  port: number;
  user: string;
  password: string;
  database: string;
  ssl: boolean | "require";
  poolMax: number;
  readonly: boolean;
  allowedSchemas: string[] | string;
  queryTimeoutMs: number;
  maxRows: number;
}>;

async function loadConfigFile(path: string): Promise<FileConfig> {
  const { readFile } = await import("node:fs/promises");
  const raw = await readFile(path, "utf8");
  const data = JSON.parse(raw) as unknown;
  if (data === null || typeof data !== "object" || Array.isArray(data)) {
    throw new Error(`Config file must be a JSON object: ${path}`);
  }
  return data as FileConfig;
}

function normalizeAllowedSchemas(
  value: string[] | string | undefined,
): string[] | undefined {
  if (value === undefined) return undefined;
  if (Array.isArray(value)) return value.map(String).map((s) => s.trim()).filter(Boolean);
  return parseCsv(value);
}

/**
 * Load config from optional JSON file, then overlay environment variables.
 * Env wins over file for any set variable.
 */
export async function loadConfig(): Promise<AppConfig> {
  const configPath = process.env.POSTGRES_CONFIG_PATH?.trim();
  const file: FileConfig = configPath ? await loadConfigFile(configPath) : {};

  const allowedFromFile = normalizeAllowedSchemas(file.allowedSchemas);

  const config: AppConfig = {
    connectionString:
      process.env.POSTGRES_CONNECTION_STRING?.trim() ||
      file.connectionString ||
      undefined,
    host:
      process.env.POSTGRES_HOST?.trim() ||
      file.host ||
      "localhost",
    port: process.env.POSTGRES_PORT
      ? parsePositiveInt(process.env.POSTGRES_PORT, 5432, "POSTGRES_PORT")
      : typeof file.port === "number"
        ? file.port
        : 5432,
    user: process.env.POSTGRES_USER?.trim() || file.user || "postgres",
    password:
      process.env.POSTGRES_PASSWORD !== undefined
        ? process.env.POSTGRES_PASSWORD
        : file.password ?? "",
    database:
      process.env.POSTGRES_DATABASE?.trim() ||
      file.database ||
      "postgres",
    ssl:
      process.env.POSTGRES_SSL !== undefined
        ? parseSsl(process.env.POSTGRES_SSL)
        : file.ssl ?? false,
    poolMax: process.env.POSTGRES_POOL_MAX
      ? parsePositiveInt(process.env.POSTGRES_POOL_MAX, 5, "POSTGRES_POOL_MAX")
      : typeof file.poolMax === "number"
        ? file.poolMax
        : 5,
    readonly:
      process.env.POSTGRES_READONLY !== undefined
        ? parseBoolean(process.env.POSTGRES_READONLY, true)
        : file.readonly ?? true,
    allowedSchemas:
      process.env.POSTGRES_ALLOWED_SCHEMAS !== undefined
        ? parseCsv(process.env.POSTGRES_ALLOWED_SCHEMAS)
        : allowedFromFile ?? [],
    queryTimeoutMs: process.env.POSTGRES_QUERY_TIMEOUT_MS
      ? parsePositiveInt(
          process.env.POSTGRES_QUERY_TIMEOUT_MS,
          30_000,
          "POSTGRES_QUERY_TIMEOUT_MS",
        )
      : typeof file.queryTimeoutMs === "number"
        ? file.queryTimeoutMs
        : 30_000,
    maxRows: process.env.POSTGRES_MAX_ROWS
      ? parsePositiveInt(process.env.POSTGRES_MAX_ROWS, 1000, "POSTGRES_MAX_ROWS")
      : typeof file.maxRows === "number"
        ? file.maxRows
        : 1000,
  };

  if (!config.connectionString) {
    if (!config.user) {
      throw new Error(
        "Database credentials required: set POSTGRES_CONNECTION_STRING or POSTGRES_USER (+ host/database).",
      );
    }
  }

  return config;
}
