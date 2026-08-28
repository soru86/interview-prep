import type { Request } from 'express';
import pinoHttp from 'pino-http';
import { logger } from '../../utils/logger';
import { redactObject } from '../../utils/mask';
import * as metrics from '../../services/metricsStore';

/**
 * Structured HTTP access logging via pino-http.
 * Prefer this over Morgan in modern production Node services (JSON, levels, redaction).
 */
export const httpLoggerMiddleware = pinoHttp({
  logger,
  genReqId: (req) => {
    const r = req as Request;
    return r.requestId ?? (typeof r.id === 'string' ? r.id : 'unknown');
  },
  customProps: (req) => {
    const r = req as Request;
    return {
      userId: r.user?.id,
      requestId: r.requestId,
    };
  },
  customLogLevel: (_req, res, err) => {
    if (err || res.statusCode >= 500) return 'error';
    if (res.statusCode >= 400) return 'warn';
    return 'info';
  },
  serializers: {
    req(req) {
      return {
        id: req.id,
        method: req.method,
        url: req.url,
        remoteAddress: req.remoteAddress,
        headers: redactObject({
          'user-agent': req.headers['user-agent'],
          'content-type': req.headers['content-type'],
        }),
      };
    },
  },
  customSuccessMessage: (req, res) =>
    `${req.method} ${req.url} ${res.statusCode}`,
  wrapSerializers: true,
});

/** Increments simple request counters for /api/metrics. */
export const metricsMiddleware: import('express').RequestHandler = (req, res, next) => {
  metrics.inc('http_requests_total');
  metrics.inc(`http_requests_${req.method.toLowerCase()}_total`);
  res.on('finish', () => {
    metrics.inc(`http_status_${res.statusCode}_total`);
  });
  next();
};
