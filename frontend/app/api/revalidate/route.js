import { timingSafeEqual } from "crypto";
import { revalidatePath, revalidateTag } from "next/cache";
import { NextResponse } from "next/server";
import { resolveCmsRevalidateTarget } from "@/lib/cmsRevalidate";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function secretsEqual(provided, expected) {
  if (typeof provided !== "string" || typeof expected !== "string") return false;
  if (!provided || !expected) return false;
  const left = Buffer.from(provided);
  const right = Buffer.from(expected);
  if (left.length !== right.length) return false;
  return timingSafeEqual(left, right);
}

function readSecret(request) {
  return (
    request.headers.get("x-revalidate-secret") ||
    request.headers.get("authorization")?.replace(/^Bearer\s+/i, "") ||
    ""
  ).trim();
}

export async function POST(request) {
  const expected = (process.env.REVALIDATION_SECRET || "").trim();
  if (!expected) {
    console.error("[revalidate] REVALIDATION_SECRET is not set");
    return NextResponse.json({ ok: false, error: "not_configured" }, { status: 503 });
  }

  let body = {};
  try {
    body = await request.json();
  } catch {
    body = {};
  }

  if (!secretsEqual(readSecret(request), expected)) {
    return NextResponse.json({ ok: false, error: "unauthorized" }, { status: 401 });
  }

  const resource = typeof body?.resource === "string" ? body.resource.trim() : "";
  const target = resolveCmsRevalidateTarget(resource);
  if (!target) {
    return NextResponse.json({ ok: false, error: "unknown_resource" }, { status: 400 });
  }

  try {
    for (const tag of target.tags || []) {
      revalidateTag(tag);
    }
    for (const path of target.paths || []) {
      revalidatePath(path);
    }
    if (target.layout) {
      revalidatePath("/", "layout");
    }
    return NextResponse.json({ ok: true, resource });
  } catch (error) {
    console.error("[revalidate] failed", resource, error);
    return NextResponse.json({ ok: false, error: "revalidate_failed" }, { status: 500 });
  }
}

export function GET() {
  return NextResponse.json({ ok: false, error: "method_not_allowed" }, { status: 405 });
}
