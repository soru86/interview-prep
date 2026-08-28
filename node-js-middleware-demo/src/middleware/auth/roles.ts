import type { RequestHandler } from 'express';
import type { Role } from '../../services/userStore';
import { toAuthError, toForbiddenError } from '../errors/errorHandler';

/**
 * Role-based access control after Passport has populated `req.user`.
 */
export function requireRoles(...roles: Role[]): RequestHandler {
  return (req, _res, next) => {
    if (!req.user) return next(toAuthError());
    if (!roles.includes(req.user.role)) {
      return next(toForbiddenError(`Requires role: ${roles.join(' | ')}`));
    }
    return next();
  };
}
