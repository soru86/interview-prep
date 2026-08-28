import type { RequestHandler } from 'express';
import { AppError } from '../../utils/AppError';

/**
 * Captures Idempotency-Key header for safe retries of mutating endpoints
 * (common for payments/orders). Persistence is handled in the order store.
 */
export const idempotencyMiddleware: RequestHandler = (req, _res, next) => {
  const key = req.header('idempotency-key') ?? req.header('Idempotency-Key');
  if (!key) {
    return next(
      new AppError(
        'Idempotency-Key header is required',
        400,
        'IDEMPOTENCY_KEY_REQUIRED',
      ),
    );
  }
  if (key.length < 8 || key.length > 128) {
    return next(
      new AppError(
        'Idempotency-Key must be 8-128 characters',
        400,
        'IDEMPOTENCY_KEY_INVALID',
      ),
    );
  }
  req.idempotencyKey = key;
  return next();
};
