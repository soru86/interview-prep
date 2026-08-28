import { randomBytes, timingSafeEqual } from 'node:crypto';
import type { RequestHandler } from 'express';
import { AppError } from '../../utils/AppError';

const SAFE = new Set(['GET', 'HEAD', 'OPTIONS']);
const CSRF_COOKIE = 'csrf_token';
const CSRF_HEADER = 'x-csrf-token';

function safeEqual(a: string, b: string): boolean {
  const ba = Buffer.from(a);
  const bb = Buffer.from(b);
  if (ba.length !== bb.length) return false;
  return timingSafeEqual(ba, bb);
}

/**
 * Double-submit cookie CSRF protection for cookie-authenticated browser flows.
 * Modern replacement for the unmaintained `csurf` package.
 *
 * Flow:
 * 1. Client calls GET /api/auth/csrf → receives token in JSON + cookie
 * 2. Client echoes token via `x-csrf-token` on mutating session requests
 */
export const csrfTokenIssuer: RequestHandler = (req, res, next) => {
  const existing = req.cookies?.[CSRF_COOKIE] as string | undefined;
  const token = existing && existing.length >= 24 ? existing : randomBytes(24).toString('hex');
  res.cookie(CSRF_COOKIE, token, {
    httpOnly: false,
    sameSite: 'lax',
    secure: false,
    path: '/',
  });
  req.csrfToken = () => token;
  res.setHeader(CSRF_HEADER, token);
  next();
};

export const csrfProtection: RequestHandler = (req, _res, next) => {
  if (SAFE.has(req.method)) return next();

  // Bearer / API-key machine clients are not CSRF-vulnerable in the classic sense
  const auth = req.header('authorization');
  if (auth?.startsWith('Bearer ')) return next();
  if (req.header('x-api-key')) return next();

  // Only enforce when a session cookie is present (browser cookie auth)
  const hasSession = Boolean(req.cookies?.['connect.sid']);
  if (!hasSession) return next();

  const cookieToken = req.cookies?.[CSRF_COOKIE] as string | undefined;
  const headerToken =
    req.header(CSRF_HEADER) ?? (req.body?.csrfToken as string | undefined);

  if (!cookieToken || !headerToken || !safeEqual(cookieToken, headerToken)) {
    return next(new AppError('Invalid CSRF token', 403, 'CSRF_INVALID'));
  }

  return next();
};
