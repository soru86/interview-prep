import pino from 'pino';
import { env } from '../config/env';
import { redactObject } from './mask';

export const logger = pino({
  level: env.LOG_LEVEL,
  redact: {
    paths: [
      'req.headers.authorization',
      'req.headers.cookie',
      'req.headers["x-api-key"]',
      'req.body.password',
      'req.body.ssn',
      'req.body.cardNumber',
      'req.body.cvv',
      'res.headers["set-cookie"]',
    ],
    censor: '[REDACTED]',
  },
  formatters: {
    level(label) {
      return { level: label };
    },
  },
  transport:
    env.NODE_ENV === 'development'
      ? {
          target: 'pino-pretty',
          options: { colorize: true, translateTime: 'SYS:standard' },
        }
      : undefined,
});

export function auditLog(
  action: string,
  meta: Record<string, unknown>,
): void {
  logger.info({ audit: true, action, ...redactObject(meta) }, 'audit_event');
}
