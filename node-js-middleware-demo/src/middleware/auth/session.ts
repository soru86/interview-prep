import session from 'express-session';
import { env } from '../../config/env';

/**
 * Server-side session store middleware.
 * Demo uses MemoryStore; production should swap in Redis/Memcached/connect-pg-simple.
 */
export const sessionMiddleware = session({
  name: 'connect.sid',
  secret: env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,
    sameSite: 'lax',
    secure: env.cookieSecure,
    maxAge: 1000 * 60 * 60 * 8,
  },
});
