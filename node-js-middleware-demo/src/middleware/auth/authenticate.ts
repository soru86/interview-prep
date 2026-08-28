import type { RequestHandler } from 'express';
import { passport } from './passport';
import { toAuthError } from '../errors/errorHandler';

/**
 * Accepts either an established session OR a valid Bearer JWT.
 * Mirrors how many BFF + API products support both cookie and token clients.
 */
export const authenticate: RequestHandler = (req, res, next) => {
  if (req.isAuthenticated?.() && req.user) return next();

  passport.authenticate('jwt', { session: false }, (err: unknown, user: Express.User | false) => {
    if (err) return next(err);
    if (!user) return next(toAuthError());
    req.user = user;
    return next();
  })(req, res, next);
};

/** Strict JWT-only (no session) — useful for pure API routes. */
export const authenticateJwt: RequestHandler = (req, res, next) => {
  passport.authenticate('jwt', { session: false }, (err: unknown, user: Express.User | false) => {
    if (err) return next(err);
    if (!user) return next(toAuthError());
    req.user = user;
    return next();
  })(req, res, next);
};

/** Local strategy used by the login route. */
export const authenticateLocal: RequestHandler = (req, res, next) => {
  passport.authenticate(
    'local',
    { session: true },
    (err: unknown, user: Express.User | false, info?: { message?: string }) => {
      if (err) return next(err);
      if (!user) return next(toAuthError(info?.message ?? 'Invalid credentials'));
      req.logIn(user, (loginErr) => {
        if (loginErr) return next(loginErr);
        return next();
      });
    },
  )(req, res, next);
};
