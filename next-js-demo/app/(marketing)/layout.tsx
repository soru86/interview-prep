import Link from "next/link";

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <header className="border-b border-zinc-200 dark:border-zinc-800">
        <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/" className="text-lg font-bold text-indigo-600">
            NextBoard
          </Link>
          <section className="flex gap-4 text-sm">
            <Link href="/login" className="text-zinc-600 hover:text-indigo-600">
              Sign in
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-indigo-600 px-3 py-1.5 text-white hover:bg-indigo-500"
            >
              Register
            </Link>
          </section>
        </nav>
      </header>
      {children}
    </>
  );
}
