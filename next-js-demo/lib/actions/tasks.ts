"use server";

import { revalidatePath, revalidateTag } from "next/cache";
import { z } from "zod";
import { getSession } from "@/lib/auth";
import { getDb } from "@/lib/db";
import type { ActionState } from "@/lib/types";

const createTaskSchema = z.object({
  title: z.string().min(1, "Title is required").max(200, "Title is too long"),
});

const toggleTaskSchema = z.object({
  taskId: z.coerce.number().int().positive(),
});

export async function createTask(
  _prev: ActionState,
  formData: FormData
): Promise<ActionState> {
  const session = await getSession();
  if (!session) {
    return { success: false, message: "Unauthorized" };
  }

  const parsed = createTaskSchema.safeParse({
    title: formData.get("title"),
  });

  if (!parsed.success) {
    return {
      success: false,
      errors: parsed.error.flatten().fieldErrors as Record<string, string[]>,
    };
  }

  getDb()
    .prepare("INSERT INTO tasks (user_id, title, completed) VALUES (?, ?, 0)")
    .run(session.userId, parsed.data.title);

  revalidateTag("tasks", "max");
  revalidateTag("posts", "max");
  revalidatePath("/tasks");

  return { success: true };
}

export async function toggleTask(taskId: number): Promise<ActionState> {
  const session = await getSession();
  if (!session) {
    return { success: false, message: "Unauthorized" };
  }

  const parsed = toggleTaskSchema.safeParse({ taskId });
  if (!parsed.success) {
    return { success: false, message: "Invalid task" };
  }

  getDb()
    .prepare(
      `UPDATE tasks SET completed = CASE WHEN completed = 1 THEN 0 ELSE 1 END
       WHERE id = ? AND user_id = ?`
    )
    .run(parsed.data.taskId, session.userId);

  revalidateTag("tasks", "max");
  revalidateTag("posts", "max");
  revalidatePath("/tasks");

  return { success: true };
}
