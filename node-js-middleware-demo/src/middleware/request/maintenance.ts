import type { RequestHandler } from 'express';
import { env } from '../../config/env';
import { AppError } from '../../utils/AppError';

const BYPASS = new Set(['/api/health', '/api/ready']);

/**
 * Global kill-switch for deploys/incidents. Health probes stay available
 * so orchestrators can still inspect liveness.
 */
export const maintenanceMiddleware: RequestHandler = (req, _res, next) => {
  if (!env.MAINTENANCE_MODE) return next();
  if (BYPASS.has(req.path)) return next();
  next(
    new AppError(
      'Service is in maintenance mode',
      503,
      'MAINTENANCE_MODE',
    ),
  );
};
