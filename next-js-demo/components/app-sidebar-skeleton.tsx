import { Skeleton } from "@/components/ui/skeleton";

export function AppSidebarSkeleton() {
  return (
    <aside className="hidden w-56 shrink-0 border-r border-zinc-200 p-4 dark:border-zinc-800 md:block">
      <Skeleton className="mb-6 h-4 w-24" />
      {Array.from({ length: 4 }).map((_, i) => (
        <Skeleton key={i} className="mb-2 h-9 w-full" />
      ))}
    </aside>
  );
}
