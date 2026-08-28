export type User = {
  id: number;
  email: string;
  name: string;
  created_at: string;
};

export type Post = {
  id: number;
  slug: string;
  title: string;
  excerpt: string;
  body: string;
  cover_image: string;
  author_id: number;
  author_name?: string;
  published_at: string;
};

export type Photo = {
  id: number;
  title: string;
  src: string;
  alt: string;
  width: number;
  height: number;
};

export type Task = {
  id: number;
  user_id: number;
  title: string;
  completed: boolean;
  created_at: string;
};

export type SessionPayload = {
  userId: number;
  email: string;
  name: string;
};

export type ActionState = {
  success: boolean;
  errors?: Record<string, string[]>;
  message?: string;
};
