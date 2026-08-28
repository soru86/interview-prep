import { TaskList } from "@/components/task-list";
import { getSession } from "@/lib/auth";
import { getTasksByUserId } from "@/lib/db";
import { redirect } from "next/navigation";

export const runtime = "nodejs";

export const metadata = { title: "Tasks" };

export default async function TasksPage() {
  const session = await getSession();
  if (!session) redirect("/login");

  const tasks = getTasksByUserId(session.userId);

  return (
    <section className="mx-auto max-w-xl space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Tasks</h1>
        <p className="mt-1 text-sm text-zinc-500">
          Instant UI with useOptimistic — mutations via Server Actions (no
          useEffect fetch).
        </p>
      </header>
      <TaskList initialTasks={tasks} />
    </section>
  );
}
