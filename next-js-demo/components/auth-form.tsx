"use client";

import { useActionState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import type { ActionState } from "@/lib/types";

const initialState: ActionState = { success: false };

type AuthFormProps = {
  action: (prev: ActionState, formData: FormData) => Promise<ActionState>;
  submitLabel: string;
  fields: Array<"email" | "password" | "name">;
  callbackUrl?: string;
};

export function AuthForm({
  action,
  submitLabel,
  fields,
  callbackUrl,
}: AuthFormProps) {
  const [state, formAction, pending] = useActionState(action, initialState);

  return (
    <form action={formAction} className="space-y-4">
      {callbackUrl ? (
        <input type="hidden" name="callbackUrl" value={callbackUrl} />
      ) : null}
      {fields.includes("name") ? (
        <Field label="Name" name="name" errors={state.errors?.name} />
      ) : null}
      {fields.includes("email") ? (
        <Field label="Email" name="email" type="email" errors={state.errors?.email} />
      ) : null}
      {fields.includes("password") ? (
        <Field
          label="Password"
          name="password"
          type="password"
          errors={state.errors?.password}
        />
      ) : null}
      {state.message ? (
        <p className="text-sm text-red-600">{state.message}</p>
      ) : null}
      <Button type="submit" disabled={pending} className="w-full">
        {pending ? "Please wait…" : submitLabel}
      </Button>
    </form>
  );
}

function Field({
  label,
  name,
  type = "text",
  errors,
}: {
  label: string;
  name: string;
  type?: string;
  errors?: string[];
}) {
  return (
    <label className="block space-y-1">
      <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
        {label}
      </span>
      <Input name={name} type={type} required />
      {errors?.map((error) => (
        <span key={error} className="block text-xs text-red-600">
          {error}
        </span>
      ))}
    </label>
  );
}
