import Image from "next/image";
import Link from "next/link";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getCachedPostBySlug } from "@/lib/cache";

export const runtime = "nodejs";

type PageProps = {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ debug?: string }>;
};

export async function generateMetadata({
  params,
}: PageProps): Promise<Metadata> {
  const { slug } = await params;
  const post = await getCachedPostBySlug(slug);

  if (!post) {
    return { title: "Post not found" };
  }

  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: [{ url: post.cover_image, alt: post.title }],
      type: "article",
    },
  };
}

export default async function PostPage({ params, searchParams }: PageProps) {
  const { slug } = await params;
  const { debug } = await searchParams;

  if (debug === "error") {
    throw new Error("Demo error — segment error.tsx will catch this");
  }

  const post = await getCachedPostBySlug(slug);
  if (!post) notFound();

  return (
    <article className="mx-auto max-w-3xl">
      <Link
        href="/posts"
        className="mb-6 inline-block text-sm text-indigo-600 hover:underline"
      >
        ← All posts
      </Link>
      <h1 className="text-3xl font-bold tracking-tight">{post.title}</h1>
      <p className="mt-2 text-sm text-zinc-500">
        By {post.author_name} · {new Date(post.published_at).toLocaleDateString()}
      </p>
      <section className="relative mt-6 aspect-[16/9] overflow-hidden rounded-2xl">
        <Image
          src={post.cover_image}
          alt={post.title}
          fill
          priority
          sizes="(max-width: 768px) 100vw, 768px"
          className="object-cover"
        />
      </section>
      <p className="mt-8 leading-relaxed text-zinc-700 dark:text-zinc-300">
        {post.body}
      </p>
      <p className="mt-8 text-xs text-zinc-400">
        Add <code>?debug=error</code> to trigger the segment error boundary.
      </p>
    </article>
  );
}
