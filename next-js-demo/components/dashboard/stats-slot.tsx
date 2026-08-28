import { delay } from "@/lib/utils";
import { getSession } from "@/lib/auth";
import { getTaskCountByUser } from "@/lib/db";
import { getCachedPostCount } from "@/lib/cache";

export async function StatsSlot() {
  await delay(800);
  const session = await getSession();
  const postCount = await getCachedPostCount();
  const taskStats = session
    ? getTaskCountByUser(session.userId)
    : { total: 0, completed: 0 };

  const externalStats = await fetch("https://jsonplaceholder.typicode.com/todos/1", {
    next: { revalidate: 3600 },
  }).then((res) => res.json() as Promise<{ id: number; title: string }>);

  return (
    <section className="rounded-xl border border-indigo-200 bg-indigo-50/50 p-4 dark:border-indigo-900 dark:bg-indigo-950/30">
      <h2 className="text-xs font-semibold uppercase tracking-wider text-indigo-600 dark:text-indigo-400">
        @stats slot
      </h2>
      <dl className="mt-3 space-y-2 text-sm">
        <div className="flex justify-between">
          <dt className="text-zinc-500">Posts (cached)</dt>
          <dd className="font-mono font-medium">{postCount}</dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-zinc-500">Tasks done</dt>
          <dd className="font-mono font-medium">
            {taskStats.completed}/{taskStats.total}
          </dd>
        </div>
        <div className="flex justify-between">
          <dt className="text-zinc-500">Fetch cache demo</dt>
          <dd className="truncate font-mono text-xs" title={externalStats.title}>
            #{externalStats.id}
          </dd>
        </div>
      </dl>
    </section>
  );
}
