import { GalleryGrid } from "@/components/gallery-grid";

export const runtime = "nodejs";

export const metadata = { title: "Gallery" };

export default function GalleryPage() {
  return (
    <section className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Gallery</h1>
        <p className="mt-1 text-sm text-zinc-500">
          Click a photo for an intercepting route modal. Refresh or open in a
          new tab for the full page.
        </p>
      </header>
      <GalleryGrid />
    </section>
  );
}
