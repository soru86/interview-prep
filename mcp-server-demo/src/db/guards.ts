/**
 * SQL safety helpers: read-only classification, multi-statement detection,
 * and light schema allowlist checks for identifiers used in tool args.
 */

const WRITE_KEYWORDS =
  /\b(INSERT|UPDATE|DELETE|MERGE|UPSERT|TRUNCATE|DROP|CREATE|ALTER|GRANT|REVOKE|COMMENT|COPY|CALL|DO|EXECUTE|REFRESH|REINDEX|CLUSTER|VACUUM|ANALYZE|LOCK|SET|RESET|DISCARD|LOAD|LISTEN|NOTIFY|UNLISTEN|SECURITY\s+LABEL)\b/i;

const READ_PREFIX =
  /^\s*(WITH|SELECT|EXPLAIN|SHOW|VALUES|TABLE)\b/i;

/** Strip /* ... *\/ and -- line comments for classification. */
export function stripSqlComments(sql: string): string {
  return sql
    .replace(/\/\*[\s\S]*?\*\//g, " ")
    .replace(/--[^\n]*/g, " ");
}

/**
 * Detect multiple statements separated by `;` outside of string literals.
 * Single trailing semicolon is allowed.
 */
export function hasMultipleStatements(sql: string): boolean {
  const cleaned = stripSqlComments(sql);
  let inSingle = false;
  let inDouble = false;
  let inDollar: string | null = null;
  let i = 0;

  while (i < cleaned.length) {
    const ch = cleaned[i];
    const next = cleaned[i + 1];

    if (inDollar) {
      if (cleaned.startsWith(inDollar, i)) {
        i += inDollar.length;
        inDollar = null;
        continue;
      }
      i += 1;
      continue;
    }

    if (inSingle) {
      if (ch === "'" && next === "'") {
        i += 2;
        continue;
      }
      if (ch === "'") inSingle = false;
      i += 1;
      continue;
    }

    if (inDouble) {
      if (ch === '"' && next === '"') {
        i += 2;
        continue;
      }
      if (ch === '"') inDouble = false;
      i += 1;
      continue;
    }

    // dollar-quoted string: $tag$
    if (ch === "$") {
      const match = cleaned.slice(i).match(/^\$[A-Za-z_][A-Za-z0-9_]*\$/);
      if (match) {
        inDollar = match[0];
        i += match[0].length;
        continue;
      }
      if (cleaned.startsWith("$$", i)) {
        inDollar = "$$";
        i += 2;
        continue;
      }
    }

    if (ch === "'") {
      inSingle = true;
      i += 1;
      continue;
    }
    if (ch === '"') {
      inDouble = true;
      i += 1;
      continue;
    }

    if (ch === ";") {
      const rest = cleaned.slice(i + 1).trim();
      if (rest.length > 0) return true;
    }

    i += 1;
  }

  return false;
}

export function assertSingleStatement(sql: string): void {
  if (hasMultipleStatements(sql)) {
    throw new Error("Multiple SQL statements are not allowed.");
  }
}

export function isReadOnlySql(sql: string): boolean {
  const cleaned = stripSqlComments(sql).trim();
  if (!cleaned) return false;
  if (!READ_PREFIX.test(cleaned)) return false;
  // EXPLAIN ANALYZE still executes the plan — treat as write-capable risk.
  if (/^\s*EXPLAIN\s+ANALYZE\b/i.test(cleaned)) return false;
  // Block obvious write keywords even inside CTE wrappers.
  if (WRITE_KEYWORDS.test(cleaned)) return false;
  return true;
}

export function assertReadOnly(sql: string): void {
  if (!isReadOnlySql(sql)) {
    throw new Error(
      "Read-only mode is enabled. Only SELECT/WITH/EXPLAIN/SHOW (without ANALYZE) are allowed. Set POSTGRES_READONLY=false to allow writes.",
    );
  }
}

export function assertSchemaAllowed(
  schema: string,
  allowedSchemas: string[],
): void {
  if (allowedSchemas.length === 0) return;
  if (!allowedSchemas.includes(schema)) {
    throw new Error(
      `Schema "${schema}" is not in POSTGRES_ALLOWED_SCHEMAS (${allowedSchemas.join(", ")}).`,
    );
  }
}

/** Validate a simple SQL identifier (schema/table/column names from tool args). */
export function assertSafeIdentifier(name: string, label: string): void {
  if (!/^[A-Za-z_][A-Za-z0-9_$]*$/.test(name)) {
    throw new Error(
      `Invalid ${label} "${name}". Use unquoted identifiers: letters, digits, underscore, $.`,
    );
  }
}
