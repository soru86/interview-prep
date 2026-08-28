import type { RequestHandler } from 'express';
import { env } from '../../config/env';
import { AppError } from '../../utils/AppError';

/**
 * Aborts long-running requests so workers are not held indefinitely.
 * Production systems often also enforce upstream gateway timeouts.
 */
export function requestTimeoutMiddleware(
  ms = env.REQUEST_TIMEOUT_MS,
): RequestHandler {
  return (_req, res, next) => {
    const timer = setTimeout(() => {
      if (!res.headersSent) {
        next(new AppError('Request timed out', 408, 'REQUEST_TIMEOUT'));
      }
    }, ms);

    const clear = () => clearTimeout(timer);
    res.on('finish', clear);
    res.on('close', clear);
    next();
  };
}
