import type { ErrorRequestHandler } from 'express';
import { MulterError } from 'multer';
import { ZodError } from 'zod';
import { env } from '../../config/env';
import { AppError, isAppError } from '../../utils/AppError';
import { logger } from '../../utils/logger';
import * as metrics from '../../services/metricsStore';

/**
 * Centralized Express error middleware (4-arg signature).
 * Maps Zod, Passport/JWT, Multer, and CSRF failures to stable API error bodies.
 */
export const errorHandler: ErrorRequestHandler = (err, req, res, _next) => {
  metrics.inc('http_errors_total');

  let status = 500;
  let code = 'INTERNAL_ERROR';
  let message = 'Internal server error';
  let details: unknown;

  if (isAppError(err)) {
    status = err.statusCode;
    code = err.code;
    message = err.message;
    details = err.details;
  } else if (err instanceof ZodError) {
    status = 400;
    code = 'VALIDATION_ERROR';
    message = 'Request validation failed';
    details = err.flatten();
  } else if (err instanceof MulterError) {
    status = 400;
    code = 'UPLOAD_ERROR';
    message = err.message;
    details = { field: err.field, multerCode: err.code };
  } else if (err?.name === 'UnauthorizedError' || err?.name === 'JsonWebTokenError') {
    status = 401;
    code = 'UNAUTHORIZED';
    message = 'Invalid or expired token';
  } else if (err?.code === 'EBADCSRFTOKEN' || err?.message === 'Invalid CSRF token') {
    status = 403;
    code = 'CSRF_INVALID';
    message = 'Invalid CSRF token';
  } else if (err instanceof Error && err.message === 'request aborted') {
    status = 408;
    code = 'REQUEST_TIMEOUT';
    message = 'Request timed out';
  }

  const payload = {
    error: {
      code,
      message,
      details,
      requestId: req.requestId,
    },
  };

  if (status >= 500) {
    logger.error({ err, requestId: req.requestId }, 'unhandled_error');
  } else {
    logger.warn({ err: { message: err?.message, code }, requestId: req.requestId }, 'handled_error');
  }

  if (!env.isProd && status >= 500 && err instanceof Error) {
    (payload.error as { stack?: string }).stack = err.stack;
  }

  if (!res.headersSent) {
    res.status(status).json(payload);
  }
};

export function toAuthError(message = 'Authentication required'): AppError {
  return new AppError(message, 401, 'UNAUTHORIZED');
}

export function toForbiddenError(message = 'Forbidden'): AppError {
  return new AppError(message, 403, 'FORBIDDEN');
}
