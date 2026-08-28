import { Suspense } from "react";
import { AppNav } from "@/components/app-nav";
import { AppSidebarSkeleton } from "@/components/app-sidebar-skeleton";

export const runtime = "nodejs";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <section className="flex min-h-screen">
      <Suspense fallback={<AppSidebarSkeleton />}>
        <aside className="hidden w-56 shrink-0 border-r border-zinc-200 dark:border-zinc-800 md:block">
          <AppNav />
        </aside>
      </Suspense>
      <main className="flex-1 overflow-auto p-6 md:p-8">{children}</main>
    </section>
  );
}
