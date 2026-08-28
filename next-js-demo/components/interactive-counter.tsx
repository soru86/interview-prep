"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

export function InteractiveCounter() {
  const [count, setCount] = useState(0);

  return (
    <section className="flex items-center gap-4 rounded-xl border border-zinc-200 bg-zinc-50 p-4 dark:border-zinc-800 dark:bg-zinc-900/50">
      <section>
        <p className="text-sm font-medium text-zinc-900 dark:text-zinc-100">
          React Compiler demo
        </p>
        <p className="text-xs text-zinc-500">
          No useMemo — compiler auto-memoizes this component
        </p>
      </section>
      <section className="flex items-center gap-2">
        <Button type="button" variant="secondary" onClick={() => setCount((c) => c - 1)}>
          −
        </Button>
        <span className="min-w-[2ch] text-center font-mono text-lg">{count}</span>
        <Button type="button" onClick={() => setCount((c) => c + 1)}>
          +
        </Button>
      </section>
    </section>
  );
}
