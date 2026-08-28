import type { RequestHandler } from 'express';
import { env } from '../../config/env';
import { AppError } from '../../utils/AppError';

/**
 * HTTP Basic Auth — still common for internal metrics/admin scrape endpoints.
 */
export const metricsBasicAuth: RequestHandler = (req, res, next) => {
  const header = req.header('authorization');
  if (!header?.startsWith('Basic ')) {
    res.setHeader('WWW-Authenticate', 'Basic realm="metrics"');
    return next(new AppError('Basic authentication required', 401, 'BASIC_AUTH_REQUIRED'));
  }

  const decoded = Buffer.from(header.slice(6), 'base64').toString('utf8');
  const [user, pass] = decoded.split(':');
  if (user !== env.METRICS_USER || pass !== env.METRICS_PASSWORD) {
    return next(new AppError('Invalid basic credentials', 401, 'BASIC_AUTH_INVALID'));
  }
  return next();
};
