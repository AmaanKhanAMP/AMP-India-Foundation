import { NextResponse } from "next/server";

const PUBLIC_PATHS = ["/login", "/forgot-password", "/reset-password"];
const PUBLIC_CMS_ORIGIN = "https://cms.ampindiafoundation.org";

function isLocalHost(hostname) {
  return hostname === "localhost" || hostname === "127.0.0.1";
}

/**
 * Login redirects were built from the bind address (127.0.0.1:3012), so the
 * browser was sent to https://localhost:3012. Keep local dev on its own port,
 * and use the public CMS host in production.
 */
function redirectTo(request, pathname, { searchParams, clearSearch } = {}) {
  const url = request.nextUrl.clone();
  url.pathname = pathname;
  if (clearSearch) url.search = "";
  if (searchParams) {
    for (const [key, value] of Object.entries(searchParams)) {
      url.searchParams.set(key, value);
    }
  }

  const headerHost = (request.headers.get("x-forwarded-host") || request.headers.get("host") || "")
    .split(",")[0]
    .trim();
  const headerName = headerHost.split(":")[0].toLowerCase();

  if (headerName && !isLocalHost(headerName)) {
    const proto = (request.headers.get("x-forwarded-proto") || "https").split(",")[0].trim();
    url.protocol = proto.endsWith(":") ? proto : `${proto}:`;
    url.hostname = headerName;
    const headerPort = headerHost.split(":")[1];
    url.port = headerPort && headerPort !== "443" && headerPort !== "80" ? headerPort : "";
  } else if (url.port === "3012") {
    const origin = new URL(PUBLIC_CMS_ORIGIN);
    url.protocol = origin.protocol;
    url.hostname = origin.hostname;
    url.port = "";
  }

  return NextResponse.redirect(url);
}

export function middleware(request) {
  const { pathname } = request.nextUrl;
  const isPublic = PUBLIC_PATHS.some(
    (path) => pathname === path || pathname.startsWith(`${path}/`)
  );
  const auth = request.cookies.get("cms_auth")?.value;

  if (!auth && !isPublic) {
    if (pathname.startsWith("/api/")) {
      return NextResponse.json({ ok: false, error: "unauthorized" }, { status: 401 });
    }
    return redirectTo(request, "/login", { searchParams: { next: pathname } });
  }

  if (auth && (pathname === "/login" || pathname === "/")) {
    return redirectTo(request, "/dashboard", { clearSearch: true });
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)"],
};
