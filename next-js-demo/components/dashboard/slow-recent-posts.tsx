import Link from "next/link";
import { delay } from "@/lib/utils";
import { getRecentPosts } from "@/lib/db";

export async function SlowRecentPosts() {
  await delay(1500);
  const posts = getRecentPosts(3);

  return (
    <section className="rounded-xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="mb-4 text-sm font-medium text-zinc-500">Recent posts</h3>
      <ul className="space-y-3">
        {posts.map((post) => (
          <li key={post.id}>
            <Link
              href={`/posts/${post.slug}`}
              className="font-medium text-zinc-900 hover:text-indigo-600 dark:text-zinc-100 dark:hover:text-indigo-400"
            >
              {post.title}
            </Link>
            <p className="text-xs text-zinc-500">{post.excerpt}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
