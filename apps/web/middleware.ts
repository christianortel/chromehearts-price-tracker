import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { getAdminCookieName, verifyAdminSessionCookie } from "@/lib/admin-auth";

export async function middleware(request: NextRequest) {
  if (!request.nextUrl.pathname.startsWith("/admin") || request.nextUrl.pathname.startsWith("/admin/login")) {
    return NextResponse.next();
  }

  const secret = process.env.ADMIN_SESSION_SECRET ?? "change-me-too";
  const cookie = request.cookies.get(getAdminCookieName())?.value;
  if (!(await verifyAdminSessionCookie(cookie, secret))) {
    const loginUrl = new URL("/admin/login", request.url);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/admin/:path*"],
};
