import type { RequestHandler } from 'express';
import { auditLog } from '../../utils/logger';

const MUTATING = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

/**
 * Emits structured audit events for sensitive mutations.
 * In industry this often ships to a SIEM / immutable audit store.
 */
export const auditMiddleware: RequestHandler = (req, res, next) => {
  if (!MUTATING.has(req.method)) return next();
  if (!req.path.startsWith('/api/')) return next();

  res.on('finish', () => {
    if (res.statusCode < 400) {
      auditLog(`${req.method} ${req.path}`, {
        requestId: req.requestId,
        userId: req.user?.id,
        statusCode: res.statusCode,
        ip: req.ip,
        bodyKeys: req.body && typeof req.body === 'object' ? Object.keys(req.body) : [],
      });
    }
  });

  next();
};
