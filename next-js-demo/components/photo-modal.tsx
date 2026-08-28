"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import type { Photo } from "@/lib/types";

export function PhotoModal({ photo }: { photo: Photo }) {
  const router = useRouter();

  return (
    <section
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4"
      onClick={() => router.back()}
      role="dialog"
      aria-modal="true"
    >
      <section
        className="relative max-h-[90vh] max-w-4xl overflow-hidden rounded-2xl bg-zinc-900"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          type="button"
          onClick={() => router.back()}
          className="absolute right-3 top-3 z-10 rounded-full bg-black/50 px-3 py-1 text-sm text-white hover:bg-black/70"
        >
          Close
        </button>
        <Image
          src={photo.src}
          alt={photo.alt}
          width={photo.width}
          height={photo.height}
          className="max-h-[80vh] w-auto object-contain"
          priority
        />
        <p className="p-4 text-center text-white">{photo.title}</p>
      </section>
    </section>
  );
}
