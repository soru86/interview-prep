import { notFound } from "next/navigation";
import { PhotoModal } from "@/components/photo-modal";
import { getPhotoById } from "@/lib/db";

export const runtime = "nodejs";

type PageProps = { params: Promise<{ id: string }> };

export default async function InterceptedPhotoModal({ params }: PageProps) {
  const { id } = await params;
  const photo = getPhotoById(Number(id));
  if (!photo) notFound();

  return <PhotoModal photo={photo} />;
}
