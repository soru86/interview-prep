import Link from "next/link";
import { AuthForm } from "@/components/auth-form";
import { registerAction } from "@/lib/actions/auth";

export const metadata = { title: "Register" };

export default function RegisterPage() {
  return (
    <>
      <h1 className="mb-6 text-2xl font-bold">Create account</h1>
      <AuthForm
        action={registerAction}
        submitLabel="Register"
        fields={["name", "email", "password"]}
      />
      <p className="mt-4 text-center text-sm text-zinc-500">
        Already have an account?{" "}
        <Link href="/login" className="text-indigo-600 hover:underline">
          Sign in
        </Link>
      </p>
    </>
  );
}
