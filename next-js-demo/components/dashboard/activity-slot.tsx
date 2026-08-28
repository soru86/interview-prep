import { delay } from "@/lib/utils";
import { getRecentPosts } from "@/lib/db";

export async function ActivitySlot() {
  await delay(1200);
  const posts = getRecentPosts(5);

  return (
    <section className="rounded-xl border border-emerald-200 bg-emerald-50/50 p-4 dark:border-emerald-900 dark:bg-emerald-950/30">
      <h2 className="text-xs font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
        @activity slot
      </h2>
      <ul className="mt-3 space-y-2 text-sm">
        {posts.map((post) => (
          <li key={post.id} className="truncate text-zinc-700 dark:text-zinc-300">
            {post.title}
          </li>
        ))}
      </ul>
    </section>
  );
}
