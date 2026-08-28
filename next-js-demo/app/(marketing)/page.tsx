import Image from "next/image";
import Link from "next/link";
import { InteractiveCounter } from "@/components/interactive-counter";

export default function MarketingPage() {
  return (
    <main>
      <section className="relative mx-auto max-w-6xl px-6 py-16 md:py-24">
        <section className="relative mb-12 aspect-[21/9] overflow-hidden rounded-2xl">
          <Image
            src="https://picsum.photos/seed/hero/1400/600"
            alt="NextBoard hero"
            fill
            priority
            sizes="(max-width: 768px) 100vw, 1200px"
            className="object-cover"
          />
          <section className="absolute inset-0 flex flex-col justify-end bg-gradient-to-t from-black/80 to-transparent p-8 md:p-12">
            <h1 className="max-w-2xl text-3xl font-bold tracking-tight text-white md:text-5xl">
              Next.js 16 Feature Showcase
            </h1>
            <p className="mt-3 max-w-xl text-lg text-zinc-200">
              App Router, parallel routes, intercepting modals, Server Actions,
              caching, streaming, JWT middleware, and more.
            </p>
            <Link
              href="/login"
              className="mt-6 inline-flex w-fit rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-indigo-500"
            >
              Get started — demo@example.com / password123
            </Link>
          </section>
        </section>

        <section className="grid gap-6 md:grid-cols-3">
          {features.map((feature) => (
            <article
              key={feature.title}
              className="rounded-xl border border-zinc-200 p-6 dark:border-zinc-800"
            >
              <h2 className="font-semibold">{feature.title}</h2>
              <p className="mt-2 text-sm text-zinc-500">{feature.description}</p>
            </article>
          ))}
        </section>

        <section className="mt-12">
          <InteractiveCounter />
        </section>
      </section>
    </main>
  );
}

const features = [
  {
    title: "App Router",
    description: "Route groups, dynamic [slug], parallel & intercepting routes.",
  },
  {
    title: "Server-first",
    description: "RSC, Server Actions with Zod, unstable_cache revalidation.",
  },
  {
    title: "Modern React",
    description: "Streaming Suspense, useOptimistic, React Compiler enabled.",
  },
];
