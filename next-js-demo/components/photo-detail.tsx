import Image from "next/image";
import Link from "next/link";
import type { Photo } from "@/lib/types";

export function PhotoDetail({ photo }: { photo: Photo }) {
  return (
    <article className="mx-auto max-w-3xl">
      <Link
        href="/gallery"
        className="mb-6 inline-block text-sm text-indigo-600 hover:underline dark:text-indigo-400"
      >
        ← Back to gallery
      </Link>
      <h1 className="mb-4 text-2xl font-bold">{photo.title}</h1>
      <section className="relative aspect-[4/3] overflow-hidden rounded-2xl">
        <Image
          src={photo.src}
          alt={photo.alt}
          fill
          sizes="(max-width: 768px) 100vw, 768px"
          className="object-cover"
          priority
        />
      </section>
    </article>
  );
}
