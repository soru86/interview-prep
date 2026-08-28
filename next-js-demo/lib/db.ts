import Database from "better-sqlite3";
import path from "path";
import type { Photo, Post, Task, User } from "./types";

const dbPath = path.join(process.cwd(), "data", "demo.db");

let db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (!db) {
    db = new Database(dbPath, { readonly: false });
    db.pragma("journal_mode = WAL");
    db.pragma("foreign_keys = ON");
  }
  return db;
}

export function getUserByEmail(email: string): (User & { password_hash: string }) | undefined {
  return getDb()
    .prepare("SELECT id, email, password_hash, name, created_at FROM users WHERE email = ?")
    .get(email) as (User & { password_hash: string }) | undefined;
}

export function getUserById(id: number): User | undefined {
  return getDb()
    .prepare("SELECT id, email, name, created_at FROM users WHERE id = ?")
    .get(id) as User | undefined;
}

export function getAllPosts(): Post[] {
  return getDb()
    .prepare(
      `SELECT p.id, p.slug, p.title, p.excerpt, p.body, p.cover_image, p.author_id,
              p.published_at, u.name as author_name
       FROM posts p
       JOIN users u ON u.id = p.author_id
       ORDER BY p.published_at DESC`
    )
    .all() as Post[];
}

export function getPostBySlug(slug: string): Post | undefined {
  return getDb()
    .prepare(
      `SELECT p.id, p.slug, p.title, p.excerpt, p.body, p.cover_image, p.author_id,
              p.published_at, u.name as author_name
       FROM posts p
       JOIN users u ON u.id = p.author_id
       WHERE p.slug = ?`
    )
    .get(slug) as Post | undefined;
}

export function getRecentPosts(limit: number): Post[] {
  return getDb()
    .prepare(
      `SELECT p.id, p.slug, p.title, p.excerpt, p.body, p.cover_image, p.author_id,
              p.published_at, u.name as author_name
       FROM posts p
       JOIN users u ON u.id = p.author_id
       ORDER BY p.published_at DESC
       LIMIT ?`
    )
    .all(limit) as Post[];
}

export function getAllPhotos(): Photo[] {
  return getDb()
    .prepare("SELECT id, title, src, alt, width, height FROM photos ORDER BY id")
    .all() as Photo[];
}

export function getPhotoById(id: number): Photo | undefined {
  return getDb()
    .prepare("SELECT id, title, src, alt, width, height FROM photos WHERE id = ?")
    .get(id) as Photo | undefined;
}

export function getTasksByUserId(userId: number): Task[] {
  const rows = getDb()
    .prepare(
      "SELECT id, user_id, title, completed, created_at FROM tasks WHERE user_id = ? ORDER BY created_at DESC"
    )
    .all(userId) as Array<Omit<Task, "completed"> & { completed: number }>;

  return rows.map((row) => ({
    ...row,
    completed: Boolean(row.completed),
  }));
}

export function getTaskCountByUser(userId: number): { total: number; completed: number } {
  const row = getDb()
    .prepare(
      `SELECT COUNT(*) as total,
              SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed
       FROM tasks WHERE user_id = ?`
    )
    .get(userId) as { total: number; completed: number | null };

  return { total: row.total, completed: row.completed ?? 0 };
}

export function getPostCount(): number {
  const row = getDb().prepare("SELECT COUNT(*) as count FROM posts").get() as {
    count: number;
  };
  return row.count;
}
