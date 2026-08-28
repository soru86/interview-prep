"use server";

import bcrypt from "bcryptjs";
import { redirect } from "next/navigation";
import { z } from "zod";
import {
  clearSessionCookie,
  createSessionToken,
  setSessionCookie,
} from "@/lib/auth";
import { getDb, getUserByEmail } from "@/lib/db";
import type { ActionState } from "@/lib/types";

const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

const registerSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

function fieldErrors(error: z.ZodError): Record<string, string[]> {
  return error.flatten().fieldErrors as Record<string, string[]>;
}

export async function loginAction(
  _prev: ActionState,
  formData: FormData
): Promise<ActionState> {
  const parsed = loginSchema.safeParse({
    email: formData.get("email"),
    password: formData.get("password"),
  });

  if (!parsed.success) {
    return { success: false, errors: fieldErrors(parsed.error) };
  }

  const user = getUserByEmail(parsed.data.email);
  if (!user || !bcrypt.compareSync(parsed.data.password, user.password_hash)) {
    return {
      success: false,
      errors: { email: ["Invalid email or password"] },
    };
  }

  const token = await createSessionToken({
    userId: user.id,
    email: user.email,
    name: user.name,
  });
  await setSessionCookie(token);

  const callbackUrl = formData.get("callbackUrl");
  redirect(
    typeof callbackUrl === "string" && callbackUrl.startsWith("/")
      ? callbackUrl
      : "/dashboard"
  );
}

export async function registerAction(
  _prev: ActionState,
  formData: FormData
): Promise<ActionState> {
  const parsed = registerSchema.safeParse({
    name: formData.get("name"),
    email: formData.get("email"),
    password: formData.get("password"),
  });

  if (!parsed.success) {
    return { success: false, errors: fieldErrors(parsed.error) };
  }

  const existing = getUserByEmail(parsed.data.email);
  if (existing) {
    return {
      success: false,
      errors: { email: ["An account with this email already exists"] },
    };
  }

  const passwordHash = bcrypt.hashSync(parsed.data.password, 10);
  const result = getDb()
    .prepare("INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)")
    .run(parsed.data.email, passwordHash, parsed.data.name);

  const token = await createSessionToken({
    userId: Number(result.lastInsertRowid),
    email: parsed.data.email,
    name: parsed.data.name,
  });
  await setSessionCookie(token);
  redirect("/dashboard");
}

export async function logoutAction(): Promise<void> {
  await clearSessionCookie();
  redirect("/login");
}
