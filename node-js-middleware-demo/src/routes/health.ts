import { Router } from 'express';

const router = Router();
const startedAt = Date.now();

router.get('/health', (_req, res) => {
  res.status(200).json({
    status: 'ok',
    uptimeSec: Math.floor((Date.now() - startedAt) / 1000),
  });
});

router.get('/ready', (_req, res) => {
  res.status(200).json({ status: 'ready' });
});

export default router;
