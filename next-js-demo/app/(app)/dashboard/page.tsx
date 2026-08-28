import { Suspense } from "react";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { SlowChart } from "@/components/dashboard/slow-chart";
import { SlowRecentPosts } from "@/components/dashboard/slow-recent-posts";
import {
  ChartSkeleton,
  HeaderSkeleton,
  ListSkeleton,
} from "@/components/dashboard/dashboard-skeletons";

export const runtime = "nodejs";

export default function DashboardPage() {
  return (
    <section className="space-y-8">
      <Suspense fallback={<HeaderSkeleton />}>
        <DashboardHeader />
        <Suspense fallback={<ChartSkeleton />}>
          <SlowChart />
          <section className="mt-6">
            <Suspense fallback={<ListSkeleton />}>
              <SlowRecentPosts />
            </Suspense>
          </section>
        </Suspense>
      </Suspense>
    </section>
  );
}
