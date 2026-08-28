import { unstable_cache } from "next/cache";
import { getAllPosts, getPostBySlug, getPostCount } from "./db";
import type { Post } from "./types";

export type CachedPostsResult = {
  posts: Post[];
  cachedAt: string;
};

export const getCachedPosts = unstable_cache(
  async (): Promise<CachedPostsResult> => {
    const posts = getAllPosts();
    return { posts, cachedAt: new Date().toISOString() };
  },
  ["posts-list"],
  { tags: ["posts"], revalidate: 60 }
);

export async function getCachedPostBySlug(slug: string): Promise<Post | undefined> {
  return unstable_cache(
    async () => getPostBySlug(slug),
    [`post-by-slug`, slug],
    { tags: ["posts"], revalidate: 60 }
  )();
}

export const getCachedPostCount = unstable_cache(
  async (): Promise<number> => {
    return getPostCount();
  },
  ["post-count"],
  { tags: ["posts"], revalidate: 60 }
);
