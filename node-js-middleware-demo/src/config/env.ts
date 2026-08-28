import path from 'node:path';
import dotenv from 'dotenv';
import { z } from 'zod';

dotenv.config();

const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
  PORT: z.coerce.number().int().positive().default(3000),
  HOST: z.string().default('0.0.0.0'),
  LOG_LEVEL: z.enum(['fatal', 'error', 'warn', 'info', 'debug', 'trace']).default('info'),
  TRUST_PROXY: z
    .string()
    .optional()
    .transform((v) => v === 'true' || v === '1'),
  CORS_ORIGINS: z.string().default('http://localhost:3000,http://127.0.0.1:3000'),
  SESSION_SECRET: z.string().min(16).default('change-me-session-secret-32b'),
  JWT_SECRET: z.string().min(16).default('change-me-jwt-secret-32bytes!!'),
  JWT_EXPIRES_IN: z.string().default('1h'),
  COOKIE_SECURE: z
    .string()
    .optional()
    .transform((v) => v === 'true' || v === '1'),
  API_KEY: z.string().min(8).default('demo-service-api-key'),
  METRICS_USER: z.string().default('metrics'),
  METRICS_PASSWORD: z.string().default('metrics-secret'),
  RATE_LIMIT_WINDOW_MS: z.coerce.number().int().positive().default(60_000),
  RATE_LIMIT_MAX: z.coerce.number().int().positive().default(100),
  SLOW_DOWN_DELAY_MS: z.coerce.number().int().nonnegative().default(250),
  REQUEST_TIMEOUT_MS: z.coerce.number().int().positive().default(15_000),
  MAINTENANCE_MODE: z
    .string()
    .optional()
    .transform((v) => v === 'true' || v === '1'),
  IP_ALLOWLIST: z.string().default(''),
  IP_DENYLIST: z.string().default(''),
  UPLOAD_DIR: z.string().default(path.join(process.cwd(), 'uploads')),
  BODY_LIMIT: z.string().default('100kb'),
});

const parsed = envSchema.safeParse(process.env);

if (!parsed.success) {
  console.error('Invalid environment configuration:', parsed.error.flatten().fieldErrors);
  process.exit(1);
}

const data = parsed.data;

export const env = {
  ...data,
  corsOrigins: data.CORS_ORIGINS.split(',')
    .map((s) => s.trim())
    .filter(Boolean),
  ipAllowlist: data.IP_ALLOWLIST.split(',')
    .map((s) => s.trim())
    .filter(Boolean),
  ipDenylist: data.IP_DENYLIST.split(',')
    .map((s) => s.trim())
    .filter(Boolean),
  isProd: data.NODE_ENV === 'production',
  cookieSecure: data.COOKIE_SECURE ?? data.NODE_ENV === 'production',
  trustProxy: data.TRUST_PROXY ?? true,
};

export type Env = typeof env;
