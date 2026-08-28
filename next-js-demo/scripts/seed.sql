-- Password hashes are inserted by init-db.ts (bcrypt for "password123")

INSERT OR IGNORE INTO posts (slug, title, excerpt, body, cover_image, author_id, published_at) VALUES
  ('getting-started-with-nextjs', 'Getting Started with Next.js 16', 'App Router fundamentals for modern React apps.', 'Next.js 16 combines the App Router with React 19 features like Server Components, Server Actions, and the stable React Compiler. This post walks through project structure, routing conventions, and when to reach for client components.', 'https://picsum.photos/seed/post1/1200/630', 1, '2026-01-10T10:00:00Z'),
  ('parallel-routes-deep-dive', 'Parallel Routes Deep Dive', 'Render multiple pages in the same layout simultaneously.', 'Parallel routes use @folder slots in your file system. Each slot gets its own loading and error boundaries, enabling dashboards with independent streaming regions.', 'https://picsum.photos/seed/post2/1200/630', 1, '2026-02-05T14:30:00Z'),
  ('server-actions-guide', 'Server Actions Guide', 'Mutate data without client-side fetch.', 'Server Actions run on the server and pair naturally with forms. Validate with Zod, revalidate caches, and keep secrets off the client.', 'https://picsum.photos/seed/post3/1200/630', 1, '2026-03-12T09:15:00Z'),
  ('react-compiler-intro', 'React Compiler Intro', 'Automatic memoization without useMemo noise.', 'The React Compiler analyzes component purity and inserts memoization. Next.js 16 enables it via reactCompiler in next.config.ts.', 'https://picsum.photos/seed/post4/1200/630', 2, '2026-04-01T16:45:00Z'),
  ('streaming-and-suspense', 'Streaming and Suspense', 'Progressive rendering with nested boundaries.', 'Suspense boundaries let you stream slow regions independently. Combine with parallel routes for slot-level skeletons in layout.tsx.', 'https://picsum.photos/seed/post5/1200/630', 2, '2026-05-01T11:00:00Z');

INSERT OR IGNORE INTO photos (title, src, alt, width, height) VALUES
  ('Mountain Dawn', 'https://picsum.photos/seed/g1/800/600', 'Sunrise over mountain peaks', 800, 600),
  ('Urban Geometry', 'https://picsum.photos/seed/g2/800/600', 'Modern building facade', 800, 600),
  ('Forest Path', 'https://picsum.photos/seed/g3/800/600', 'Trail through tall trees', 800, 600),
  ('Ocean Horizon', 'https://picsum.photos/seed/g4/800/600', 'Calm sea at sunset', 800, 600),
  ('Desert Dunes', 'https://picsum.photos/seed/g5/800/600', 'Sand dunes under blue sky', 800, 600),
  ('City Lights', 'https://picsum.photos/seed/g6/800/600', 'Night skyline with bokeh', 800, 600),
  ('Autumn Lake', 'https://picsum.photos/seed/g7/800/600', 'Lake surrounded by fall foliage', 800, 600),
  ('Starry Night', 'https://picsum.photos/seed/g8/800/600', 'Milky way over landscape', 800, 600);
