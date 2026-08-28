import type { RequestHandler } from 'express';
import { AppError } from '../../utils/AppError';

/** Terminal 404 middleware — must run after all routes are registered. */
export const notFoundHandler: RequestHandler = (req, _res, next) => {
  next(
    new AppError(`Route not found: ${req.method} ${req.originalUrl}`, 404, 'NOT_FOUND'),
  );
};
