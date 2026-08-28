import fs from 'node:fs';
import path from 'node:path';
import multer from 'multer';
import { env } from '../../config/env';
import { AppError } from '../../utils/AppError';

if (!fs.existsSync(env.UPLOAD_DIR)) {
  fs.mkdirSync(env.UPLOAD_DIR, { recursive: true });
}

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => cb(null, env.UPLOAD_DIR),
  filename: (_req, file, cb) => {
    const safe = file.originalname.replace(/[^a-zA-Z0-9._-]/g, '_');
    cb(null, `${Date.now()}-${safe}`);
  },
});

/**
 * Multipart/form-data upload middleware used for avatars, KYC docs, etc.
 * Limits size/MIME type to reduce abuse.
 */
export const avatarUpload = multer({
  storage,
  limits: { fileSize: 1_000_000, files: 1 },
  fileFilter: (_req, file, cb) => {
    const allowed = new Set(['image/png', 'image/jpeg', 'image/webp']);
    if (!allowed.has(file.mimetype)) {
      return cb(new AppError('Only PNG/JPEG/WebP images allowed', 400, 'INVALID_FILE_TYPE'));
    }
    return cb(null, true);
  },
}).single('avatar');

export function avatarPublicPath(filename: string): string {
  return path.posix.join('/uploads', filename);
}
