import cors from 'cors';
import { env } from '../../config/env';

/**
 * Browser origin control. Credentials are enabled so session cookies work
 * for allowlisted frontends.
 */
export const corsMiddleware = cors({
  origin(origin, callback) {
    if (!origin) return callback(null, true);
    if (env.corsOrigins.includes('*') || env.corsOrigins.includes(origin)) {
      return callback(null, true);
    }
    return callback(new Error(`CORS blocked for origin: ${origin}`));
  },
  credentials: true,
  exposedHeaders: ['x-request-id', 'x-response-time', 'x-csrf-token'],
});
