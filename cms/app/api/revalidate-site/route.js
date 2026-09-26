import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * Same-origin proxy so the CMS browser never sees REVALIDATION_SECRET.
 * Failures return 200 { ok: false } so CMS saves are never rolled back.
 */
export async function POST(request) {
  let resource = "";
  try {
    const body = await request.json();
    resource = typeof body?.resource === "string" ? body.resource.trim() : "";
  } catch {
    resource = "";
  }

  if (!resource) {
    console.error("[revalidate-site] missing resource");
    return NextResponse.json({ ok: false, skipped: true });
  }

  const secret = (process.env.REVALIDATION_SECRET || "").trim();
  const origin = (
    process.env.FRONTEND_ORIGIN ||
    process.env.NEXT_PUBLIC_SITE_URL ||
    ""
  )
    .trim()
    .replace(/\/$/, "");

  if (!secret || !origin) {
    console.error(
      "[revalidate-site] skipped: REVALIDATION_SECRET or FRONTEND_ORIGIN/NEXT_PUBLIC_SITE_URL missing"
    );
    return NextResponse.json({ ok: false, skipped: true });
  }

  try {
    const res = await fetch(`${origin}/api/revalidate`, {
      method: "POST",
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
        "x-revalidate-secret": secret,
      },
      body: JSON.stringify({ resource }),
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) {
      console.error("[revalidate-site] frontend rejected", resource, res.status);
      return NextResponse.json({ ok: false });
    }
    return NextResponse.json({ ok: true, resource });
  } catch (error) {
    console.error("[revalidate-site] frontend call failed", resource, error);
    return NextResponse.json({ ok: false });
  }
}
