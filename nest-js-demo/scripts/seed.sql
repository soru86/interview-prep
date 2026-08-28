-- Sample data: password for all users is "password123"
-- bcrypt hash generated with cost factor 10

INSERT OR IGNORE INTO users (id, email, password_hash, role, created_at) VALUES
  ('a0000000-0000-4000-8000-000000000001', 'admin@demo.local', '$2b$10$.8UMCWYiS1qkYNAzjoD0dO5KQ/x23LKTmGjkTv.o1TP7bJ9oovqEC', 'admin', datetime('now')),
  ('a0000000-0000-4000-8000-000000000002', 'user@demo.local', '$2b$10$.8UMCWYiS1qkYNAzjoD0dO5KQ/x23LKTmGjkTv.o1TP7bJ9oovqEC', 'user', datetime('now'));

INSERT OR IGNORE INTO tasks (id, title, description, status, owner_id, created_at, updated_at) VALUES
  ('b0000000-0000-4000-8000-000000000001', 'Review NestJS docs', 'Read middleware, guards, and interceptors chapters', 'pending', 'a0000000-0000-4000-8000-000000000002', datetime('now'), datetime('now')),
  ('b0000000-0000-4000-8000-000000000002', 'Configure Kafka', 'Set up docker-compose and hybrid microservice', 'pending', 'a0000000-0000-4000-8000-000000000002', datetime('now'), datetime('now')),
  ('b0000000-0000-4000-8000-000000000003', 'Write unit tests', 'Add Jest sample for TasksService', 'done', 'a0000000-0000-4000-8000-000000000001', datetime('now'), datetime('now'));
