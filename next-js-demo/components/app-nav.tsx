import Link from "next/link";
import { logoutAction } from "@/lib/actions/auth";
import { getSession } from "@/lib/auth";
import { Button } from "@/components/ui/button";

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/posts", label: "Posts" },
  { href: "/gallery", label: "Gallery" },
  { href: "/tasks", label: "Tasks" },
];

export async function AppNav() {
  const session = await getSession();

  return (
    <nav className="flex flex-col gap-1 p-4">
      <p className="mb-4 px-2 text-xs font-semibold uppercase tracking-wider text-zinc-500">
        NextBoard
      </p>
      {links.map((link) => (
        <Link
          key={link.href}
          href={link.href}
          className="rounded-lg px-3 py-2 text-sm font-medium text-zinc-600 transition-colors hover:bg-indigo-50 hover:text-indigo-700 dark:text-zinc-400 dark:hover:bg-indigo-950/50 dark:hover:text-indigo-300"
        >
          {link.label}
        </Link>
      ))}
      <section className="mt-auto border-t border-zinc-200 pt-4 dark:border-zinc-800">
        {session ? (
          <>
            <p className="px-2 text-xs text-zinc-500">{session.name}</p>
            <form action={logoutAction} className="mt-2">
              <Button type="submit" variant="ghost" className="w-full justify-start">
                Sign out
              </Button>
            </form>
          </>
        ) : null}
      </section>
    </nav>
  );
}
