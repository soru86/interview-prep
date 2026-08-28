import rateLimit from 'express-rate-limit';
import slowDown from 'express-slow-down';
import { env } from '../../config/env';

/**
 * Hard rate limit — returns 429 after the configured request budget.
 * Behind proxies, `trust proxy` must be set so `req.ip` is the real client.
 */
export const rateLimitMiddleware = rateLimit({
  windowMs: env.RATE_LIMIT_WINDOW_MS,
  max: env.RATE_LIMIT_MAX,
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    error: {
      code: 'RATE_LIMITED',
      message: 'Too many requests, please try again later',
    },
  },
});

/**
 * Progressive delay before hard limiting — absorbs abusive bursts without
 * immediately rejecting legitimate traffic spikes.
 */
export const slowDownMiddleware = slowDown({
  windowMs: env.RATE_LIMIT_WINDOW_MS,
  delayAfter: Math.max(1, Math.floor(env.RATE_LIMIT_MAX / 2)),
  delayMs: () => env.SLOW_DOWN_DELAY_MS,
  validate: { delayMs: false },
});

/** Stricter bucket for login to slow credential stuffing. */
export const loginRateLimitMiddleware = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 20,
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    error: {
      code: 'LOGIN_RATE_LIMITED',
      message: 'Too many login attempts',
    },
  },
});
