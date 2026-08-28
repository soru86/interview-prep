import { getSession } from "@/lib/auth";
import { delay } from "@/lib/utils";

export async function DashboardHeader() {
  await delay(400);
  const session = await getSession();

  return (
    <header>
      <h1 className="text-2xl font-bold tracking-tight">
        Welcome back{session ? `, ${session.name}` : ""}
      </h1>
      <p className="mt-1 text-zinc-500">
        Nested Suspense boundaries stream each section independently.
      </p>
    </header>
  );
}
