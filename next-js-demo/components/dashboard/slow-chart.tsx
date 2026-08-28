import { delay } from "@/lib/utils";
import { getCachedPostCount } from "@/lib/cache";

export async function SlowChart() {
  await delay(1000);
  const postCount = await getCachedPostCount();

  return (
    <section className="rounded-xl border border-zinc-200 bg-white p-6 dark:border-zinc-800 dark:bg-zinc-900">
      <h3 className="text-sm font-medium text-zinc-500">Published posts</h3>
      <p className="mt-2 text-4xl font-bold text-indigo-600">{postCount}</p>
      <p className="mt-1 text-xs text-zinc-400">Loaded via unstable_cache</p>
    </section>
  );
}
