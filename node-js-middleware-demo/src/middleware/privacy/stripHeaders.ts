import type { RequestHandler } from 'express';

/**
 * Removes sensitive or noisy headers from outbound responses.
 * Complements `app.disable('x-powered-by')`.
 */
export const stripSensitiveHeaders: RequestHandler = (_req, res, next) => {
  res.removeHeader('x-powered-by');
  res.removeHeader('Server');
  next();
};
