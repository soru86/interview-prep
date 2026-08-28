import type { RequestHandler } from 'express';
import mongoSanitize from 'express-mongo-sanitize';
import xss from 'xss';

/**
 * Strips Mongo-style operators ($gt, $ne, ...) from user input.
 * Useful even for non-Mongo apps that later serialize into document stores.
 */
export const mongoSanitizeMiddleware = mongoSanitize({
  replaceWith: '_',
  allowDots: true,
});

function sanitizeValue(value: unknown): unknown {
  if (typeof value === 'string') return xss(value);
  if (Array.isArray(value)) return value.map(sanitizeValue);
  if (value && typeof value === 'object') {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
      out[k] = sanitizeValue(v);
    }
    return out;
  }
  return value;
}

/**
 * XSS sanitization for string fields in body/query/params.
 * Complements output encoding and CSP from Helmet.
 */
export const xssSanitizeMiddleware: RequestHandler = (req, _res, next) => {
  if (req.body) req.body = sanitizeValue(req.body);
  if (req.query) {
    const cleaned = sanitizeValue(req.query);
    // Express 4 query is a getter; mutate keys in place when possible
    if (cleaned && typeof cleaned === 'object') {
      for (const key of Object.keys(req.query)) {
        delete (req.query as Record<string, unknown>)[key];
      }
      Object.assign(req.query, cleaned as object);
    }
  }
  if (req.params) req.params = sanitizeValue(req.params) as typeof req.params;
  next();
};
