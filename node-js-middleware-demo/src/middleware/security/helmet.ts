import helmet from 'helmet';

/**
 * Sets industry-standard HTTP security headers (CSP, HSTS-ready, X-Frame-Options, etc.).
 * Almost every production Express app enables Helmet near the top of the stack.
 */
export const helmetMiddleware = helmet({
  contentSecurityPolicy: {
    useDefaults: true,
    directives: {
      "default-src": ["'self'"],
      "script-src": ["'self'"],
      "style-src": ["'self'", "'unsafe-inline'"],
      "img-src": ["'self'", 'data:'],
    },
  },
  crossOriginResourcePolicy: { policy: 'cross-origin' },
});
