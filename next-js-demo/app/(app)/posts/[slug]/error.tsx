"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function PostError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <section className="mx-auto max-w-lg rounded-xl border border-red-200 bg-red-50 p-6 dark:border-red-900 dark:bg-red-950/30">
      <h2 className="text-lg font-semibold text-red-800 dark:text-red-200">
        Failed to load post
      </h2>
      <p className="mt-2 text-sm text-red-600 dark:text-red-400">
        Segment-level error boundary (posts/[slug]/error.tsx)
      </p>
      <Button type="button" className="mt-4" onClick={() => reset()}>
        Try again
      </Button>
    </section>
  );
}
