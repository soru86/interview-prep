"use client";

import { useOptimistic, useTransition } from "react";
import { useRouter } from "next/navigation";
import { createTask, toggleTask } from "@/lib/actions/tasks";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { ActionState, Task } from "@/lib/types";

const initialFormState: ActionState = { success: false };

type OptimisticAction =
  | { type: "toggle"; id: number }
  | { type: "add"; task: Task };

export function TaskList({ initialTasks }: { initialTasks: Task[] }) {
  const router = useRouter();
  const [optimisticTasks, updateOptimistic] = useOptimistic(
    initialTasks,
    (state, action: OptimisticAction) => {
      if (action.type === "toggle") {
        return state.map((task) =>
          task.id === action.id
            ? { ...task, completed: !task.completed }
            : task
        );
      }
      return [action.task, ...state];
    }
  );
  const [isPending, startTransition] = useTransition();

  function handleToggle(task: Task) {
    startTransition(async () => {
      updateOptimistic({ type: "toggle", id: task.id });
      const result = await toggleTask(task.id);
      if (result.success) {
        router.refresh();
      }
    });
  }

  function handleAdd(formData: FormData) {
    const title = String(formData.get("title") ?? "").trim();
    if (!title) return;

    const tempTask: Task = {
      id: -Date.now(),
      user_id: 0,
      title,
      completed: false,
      created_at: new Date().toISOString(),
    };

    startTransition(async () => {
      updateOptimistic({ type: "add", task: tempTask });
      const result = await createTask(initialFormState, formData);
      if (result.success) {
        router.refresh();
      }
    });
  }

  return (
    <section className="space-y-6">
      <form action={handleAdd} className="flex gap-2">
        <Input name="title" placeholder="New task…" required />
        <Button type="submit" disabled={isPending}>
          Add
        </Button>
      </form>
      <ul className="space-y-2">
        {optimisticTasks.map((task) => (
          <li
            key={task.id}
            className="flex items-center gap-3 rounded-lg border border-zinc-200 px-4 py-3 dark:border-zinc-800"
          >
            <input
              type="checkbox"
              checked={task.completed}
              onChange={() => handleToggle(task)}
              className="h-4 w-4 cursor-pointer rounded border-zinc-300 text-indigo-600"
            />
            <span
              className={
                task.completed
                  ? "text-zinc-400 line-through"
                  : "text-zinc-900 dark:text-zinc-100"
              }
            >
              {task.title}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
