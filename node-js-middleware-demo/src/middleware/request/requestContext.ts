import { AsyncLocalStorage } from 'node:async_hooks';
import { randomUUID } from 'node:crypto';
import type { RequestHandler } from 'express';

export interface RequestContextStore {
  requestId: string;
  userId?: string;
  path?: string;
  method?: string;
}

export const requestContext = new AsyncLocalStorage<RequestContextStore>();

/**
 * Correlation ID + AsyncLocalStorage context.
 * Enables downstream services/loggers to read request-scoped metadata without
 * threading `req` through every function call.
 */
export const requestIdMiddleware: RequestHandler = (req, res, next) => {
  const incoming = req.header('x-request-id');
  const requestId = incoming && incoming.trim() ? incoming.trim() : randomUUID();
  req.requestId = requestId;
  req.id = requestId;
  res.setHeader('x-request-id', requestId);

  requestContext.run(
    {
      requestId,
      path: req.path,
      method: req.method,
      userId: req.user?.id,
    },
    () => next(),
  );
};

export function getRequestContext(): RequestContextStore | undefined {
  return requestContext.getStore();
}
