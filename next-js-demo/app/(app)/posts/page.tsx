import Image from "next/image";
import Link from "next/link";
import { getCachedPosts } from "@/lib/cache";

export const runtime = "nodejs";

export const metadata = { title: "Posts" };

export default async function PostsPage() {
  const { posts, cachedAt } = await getCachedPosts();

  return (
    <section className="space-y-8">
      <header>
        <h1 className="text-2xl font-bold">Posts</h1>
        <p className="mt-1 text-sm text-zinc-500">
          List loaded via{" "}
          <code className="rounded bg-zinc-100 px-1 dark:bg-zinc-800">
            unstable_cache
          </code>
          . Cached at: {new Date(cachedAt).toLocaleTimeString()}
        </p>
      </header>
      <ul className="grid gap-6 md:grid-cols-2">
        {posts.map((post) => (
          <li key={post.id}>
            <Link
              href={`/posts/${post.slug}`}
              className="group block overflow-hidden rounded-xl border border-zinc-200 dark:border-zinc-800"
            >
              <section className="relative aspect-[16/9]">
                <Image
                  src={post.cover_image}
                  alt={post.title}
                  fill
                  sizes="(max-width: 768px) 100vw, 50vw"
                  className="object-cover transition-transform group-hover:scale-105"
                />
              </section>
              <section className="p-4">
                <h2 className="font-semibold group-hover:text-indigo-600">
                  {post.title}
                </h2>
                <p className="mt-1 text-sm text-zinc-500">{post.excerpt}</p>
              </section>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
