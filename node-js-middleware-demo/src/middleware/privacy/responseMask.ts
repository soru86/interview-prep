import type { RequestHandler } from 'express';
import { maskCard, maskEmail, maskPhone, maskSsn } from '../../utils/mask';

type CustomerLike = {
  email?: string;
  phone?: string;
  ssn?: string;
  cardNumber?: string;
  [key: string]: unknown;
};

function maskCustomer(c: CustomerLike, isAdmin: boolean): CustomerLike {
  return {
    ...c,
    email: typeof c.email === 'string' ? maskEmail(c.email) : c.email,
    phone: typeof c.phone === 'string' ? maskPhone(c.phone) : c.phone,
    ssn: typeof c.ssn === 'string' ? maskSsn(c.ssn, isAdmin) : c.ssn,
    cardNumber: typeof c.cardNumber === 'string' ? maskCard(c.cardNumber) : c.cardNumber,
  };
}

/**
 * Response field masking for PII. Admins see SSN last-4; others see fully masked SSN.
 * Demonstrates privacy middleware used in fintech/healthcare APIs.
 */
export const responseMaskMiddleware: RequestHandler = (req, res, next) => {
  // When mounted on the customers router, req.path is mount-relative ("/" / "/:id").
  // Prefer baseUrl+path / originalUrl so the guard works in both mount styles.
  const fullPath = `${req.baseUrl || ''}${req.path || ''}` || req.originalUrl || '';
  if (!fullPath.includes('/customers')) return next();

  const originalJson = res.json.bind(res);
  res.json = ((body: unknown) => {
    const isAdmin = req.user?.role === 'admin';
    if (Array.isArray(body)) {
      return originalJson(body.map((item) => maskCustomer(item as CustomerLike, isAdmin)));
    }
    if (body && typeof body === 'object' && 'email' in (body as object)) {
      return originalJson(maskCustomer(body as CustomerLike, isAdmin));
    }
    if (body && typeof body === 'object' && 'data' in (body as object)) {
      const wrapped = body as { data: unknown };
      if (Array.isArray(wrapped.data)) {
        return originalJson({
          ...wrapped,
          data: wrapped.data.map((item) => maskCustomer(item as CustomerLike, isAdmin)),
        });
      }
      if (wrapped.data && typeof wrapped.data === 'object') {
        return originalJson({
          ...wrapped,
          data: maskCustomer(wrapped.data as CustomerLike, isAdmin),
        });
      }
    }
    return originalJson(body);
  }) as typeof res.json;

  next();
};
