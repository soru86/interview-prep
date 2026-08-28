import Image from "next/image";
import Link from "next/link";
import { getAllPhotos } from "@/lib/db";

export async function GalleryGrid() {
  const photos = getAllPhotos();

  return (
    <section className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4">
      {photos.map((photo) => (
        <Link
          key={photo.id}
          href={`/gallery/${photo.id}`}
          scroll={false}
          className="group relative aspect-[4/3] overflow-hidden rounded-xl bg-zinc-100 dark:bg-zinc-900"
        >
          <Image
            src={photo.src}
            alt={photo.alt}
            fill
            sizes="(max-width: 768px) 50vw, 25vw"
            className="object-cover transition-transform duration-300 group-hover:scale-105"
          />
          <span className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent p-3 text-sm font-medium text-white">
            {photo.title}
          </span>
        </Link>
      ))}
    </section>
  );
}
