import type { RequestHandler } from 'express';
import { env } from '../../config/env';
import { AppError } from '../../utils/AppError';

/**
 * Shared-secret API key for machine-to-machine routes.
 * Industry apps often combine this with mTLS or short-lived service JWTs.
 */
export const apiKeyMiddleware: RequestHandler = (req, _res, next) => {
  const key = req.header('x-api-key');
  if (!key || key !== env.API_KEY) {
    return next(new AppError('Invalid API key', 401, 'INVALID_API_KEY'));
  }
  return next();
};
