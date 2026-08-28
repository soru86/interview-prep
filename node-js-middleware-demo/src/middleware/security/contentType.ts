import type { RequestHandler } from 'express';
import { AppError } from '../../utils/AppError';

const MUTATING = new Set(['POST', 'PUT', 'PATCH']);

/**
 * Rejects JSON API mutations with unexpected Content-Type.
 * Multipart upload routes should skip this middleware.
 */
export const contentTypeMiddleware: RequestHandler = (req, _res, next) => {
  if (!MUTATING.has(req.method)) return next();
  if (req.path.startsWith('/api/uploads')) return next();

  const ct = req.headers['content-type'] ?? '';
  if (!ct.includes('application/json') && !ct.includes('application/x-www-form-urlencoded')) {
    return next(
      new AppError(
        'Content-Type must be application/json or application/x-www-form-urlencoded',
        415,
        'UNSUPPORTED_MEDIA_TYPE',
      ),
    );
  }
  return next();
};
