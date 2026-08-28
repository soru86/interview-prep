import { Skeleton } from "@/components/ui/skeleton";

export function HeaderSkeleton() {
  return (
    <section className="space-y-2">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-4 w-96 max-w-full" />
    </section>
  );
}

export function ChartSkeleton() {
  return <Skeleton className="h-32 w-full rounded-xl" />;
}

export function ListSkeleton() {
  return <Skeleton className="h-48 w-full rounded-xl" />;
}

export function StatsSlotSkeleton() {
  return <Skeleton className="h-40 w-full rounded-xl" />;
}

export function ActivitySlotSkeleton() {
  return <Skeleton className="h-48 w-full rounded-xl" />;
}
