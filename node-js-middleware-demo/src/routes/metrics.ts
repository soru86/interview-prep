import { Router } from 'express';
import { metricsBasicAuth } from '../middleware/auth/basicAuth';
import { apiKeyMiddleware } from '../middleware/auth/apiKey';
import { asyncHandler } from '../middleware/errors/asyncHandler';
import { snapshot, toPrometheus } from '../services/metricsStore';

const router = Router();

/** Prometheus-style scrape endpoint protected by HTTP Basic Auth. */
router.get(
  '/',
  metricsBasicAuth,
  asyncHandler(async (_req, res) => {
    res.setHeader('Content-Type', 'text/plain; version=0.0.4');
    res.send(toPrometheus() + '\n');
  }),
);

/** Machine-to-machine JSON metrics via API key. */
router.get(
  '/json',
  apiKeyMiddleware,
  asyncHandler(async (_req, res) => {
    res.json({ data: snapshot() });
  }),
);

export default router;
