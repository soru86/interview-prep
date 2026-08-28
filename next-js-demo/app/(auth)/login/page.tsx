import Link from "next/link";
import { AuthForm } from "@/components/auth-form";
import { loginAction } from "@/lib/actions/auth";

export const metadata = { title: "Sign in" };

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ callbackUrl?: string }>;
}) {
  const { callbackUrl } = await searchParams;

  return (
    <>
      <h1 className="mb-6 text-2xl font-bold">Sign in</h1>
      <AuthForm
        action={loginAction}
        submitLabel="Sign in"
        fields={["email", "password"]}
        callbackUrl={callbackUrl}
      />
      <p className="mt-4 text-center text-sm text-zinc-500">
        No account?{" "}
        <Link href="/register" className="text-indigo-600 hover:underline">
          Register
        </Link>
      </p>
      <p className="mt-2 text-center text-xs text-zinc-400">
        Demo: demo@example.com / password123
      </p>
    </>
  );
}
