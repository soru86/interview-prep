export const runtime = "nodejs";

export default function DashboardLayout({
  children,
  stats,
  activity,
}: {
  children: React.ReactNode;
  stats: React.ReactNode;
  activity: React.ReactNode;
}) {
  return (
    <section className="space-y-8">
      {children}
      <section className="grid gap-6 lg:grid-cols-2">
        {stats}
        {activity}
      </section>
    </section>
  );
}
