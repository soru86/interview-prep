import type { RequestHandler } from 'express';
import { env } from '../../config/env';
import { AppError } from '../../utils/AppError';

/**
 * Optional IP allow/deny lists used for admin planes, partner APIs,
 * or emergency blocks. Empty lists mean "no filter".
 */
export const ipFilterMiddleware: RequestHandler = (req, _res, next) => {
  const ip = req.ip ?? req.socket.remoteAddress ?? '';

  if (env.ipDenylist.length > 0 && env.ipDenylist.includes(ip)) {
    return next(new AppError('IP denied', 403, 'IP_DENIED'));
  }

  if (env.ipAllowlist.length > 0 && !env.ipAllowlist.includes(ip)) {
    return next(new AppError('IP not allowlisted', 403, 'IP_NOT_ALLOWED'));
  }

  return next();
};
