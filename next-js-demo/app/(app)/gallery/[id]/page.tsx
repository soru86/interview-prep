import { notFound } from "next/navigation";
import { PhotoDetail } from "@/components/photo-detail";
import { getPhotoById } from "@/lib/db";

export const runtime = "nodejs";

type PageProps = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: PageProps) {
  const { id } = await params;
  const photo = getPhotoById(Number(id));
  if (!photo) return { title: "Photo not found" };
  return { title: photo.title, description: photo.alt };
}

export default async function GalleryPhotoPage({ params }: PageProps) {
  const { id } = await params;
  const photo = getPhotoById(Number(id));
  if (!photo) notFound();

  return <PhotoDetail photo={photo} />;
}
