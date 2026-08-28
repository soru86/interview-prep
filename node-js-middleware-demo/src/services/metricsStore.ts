const counters = new Map<string, number>();

export function inc(name: string, by = 1): void {
  counters.set(name, (counters.get(name) ?? 0) + by);
}

export function snapshot(): Record<string, number> {
  return Object.fromEntries(counters.entries());
}

export function toPrometheus(): string {
  return Object.entries(snapshot())
    .map(([k, v]) => `# TYPE ${k} counter\n${k} ${v}`)
    .join('\n');
}
