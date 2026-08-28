import { Router } from 'express';
import { authenticate } from '../middleware/auth/authenticate';
import { asyncHandler } from '../middleware/errors/asyncHandler';
import { avatarPublicPath, avatarUpload } from '../middleware/upload/multer';
import { AppError } from '../utils/AppError';

const router = Router();

router.post(
  '/avatar',
  authenticate,
  (req, res, next) => {
    avatarUpload(req, res, (err) => {
      if (err) return next(err);
      return next();
    });
  },
  asyncHandler(async (req, res) => {
    if (!req.file) {
      throw new AppError('avatar file is required', 400, 'FILE_REQUIRED');
    }
    res.status(201).json({
      data: {
        filename: req.file.filename,
        mimetype: req.file.mimetype,
        size: req.file.size,
        url: avatarPublicPath(req.file.filename),
        uploadedBy: req.user!.id,
      },
    });
  }),
);

export default router;
