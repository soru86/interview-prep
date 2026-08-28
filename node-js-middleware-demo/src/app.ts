import path from 'node:path';
import express from 'express';
import compression from 'compression';
import cookieParser from 'cookie-parser';
import methodOverride from 'method-override';
import responseTime from 'response-time';

import { env } from './config/env';
import { helmetMiddleware } from './middleware/security/helmet';
import { corsMiddleware } from './middleware/security/cors';
import { hppMiddleware } from './middleware/security/hpp';
import { rateLimitMiddleware, slowDownMiddleware } from './middleware/security/rateLimit';
import { ipFilterMiddleware } from './middleware/security/ipFilter';
import { contentTypeMiddleware } from './middleware/security/contentType';
import {
  mongoSanitizeMiddleware,
  xssSanitizeMiddleware,
} from './middleware/security/sanitize';
import { csrfProtection, csrfTokenIssuer } from './middleware/security/csrf';
import { sessionMiddleware } from './middleware/auth/session';
import {
  passportInitialize,
  passportSession,
} from './middleware/auth/passport';
import {
  requestIdMiddleware,
} from './middleware/request/requestContext';
import { requestTimeoutMiddleware } from './middleware/request/timeout';
import { maintenanceMiddleware } from './middleware/request/maintenance';
import {
  httpLoggerMiddleware,
  metricsMiddleware,
} from './middleware/logging/httpLogger';
import { auditMiddleware } from './middleware/logging/audit';
import { stripSensitiveHeaders } from './middleware/privacy/stripHeaders';
import { notFoundHandler } from './middleware/errors/notFound';
import { errorHandler } from './middleware/errors/errorHandler';

import authRoutes from './routes/auth';
import customerRoutes from './routes/customers';
import orderRoutes from './routes/orders';
import uploadRoutes from './routes/uploads';
import healthRoutes from './routes/health';
import metricsRoutes from './routes/metrics';
import demoErrorRoutes from './routes/demoErrors';

/**
 * Middleware composition order matters. Rough industry pipeline:
 * trust proxy → correlation → security headers → CORS → parsers →
 * sanitize → session → passport → logging → rate limits → routes → errors
 */
export function createApp(): express.Application {
  const app = express();

  // Critical behind Docker / load balancers for correct req.ip and secure cookies
  app.set('trust proxy', env.trustProxy ? 1 : false);
  app.disable('x-powered-by');

  app.use(requestIdMiddleware);
  app.use(requestTimeoutMiddleware());
  app.use(maintenanceMiddleware);
  app.use(stripSensitiveHeaders);
  app.use(helmetMiddleware);
  app.use(corsMiddleware);
  app.use(compression());
  app.use(responseTime());
  app.use(ipFilterMiddleware);
  app.use(slowDownMiddleware);
  app.use(rateLimitMiddleware);

  app.use(express.json({ limit: env.BODY_LIMIT }));
  app.use(express.urlencoded({ extended: true, limit: env.BODY_LIMIT }));
  app.use(cookieParser(env.SESSION_SECRET));
  app.use(methodOverride('_method'));
  app.use(hppMiddleware);
  app.use(mongoSanitizeMiddleware);
  app.use(xssSanitizeMiddleware);
  app.use(contentTypeMiddleware);

  app.use(sessionMiddleware);
  app.use(passportInitialize);
  app.use(passportSession);
  app.use(csrfTokenIssuer);
  app.use(csrfProtection);

  app.use(httpLoggerMiddleware);
  app.use(metricsMiddleware);
  app.use(auditMiddleware);

  app.use(express.static(path.join(process.cwd(), 'public')));
  app.use('/uploads', express.static(env.UPLOAD_DIR));

  app.use('/api', healthRoutes);
  app.use('/api/auth', authRoutes);
  app.use('/api/customers', customerRoutes);
  app.use('/api/orders', orderRoutes);
  app.use('/api/uploads', uploadRoutes);
  app.use('/api/metrics', metricsRoutes);
  app.use('/api/demo-errors', demoErrorRoutes);

  app.use(notFoundHandler);
  app.use(errorHandler);

  return app;
}
