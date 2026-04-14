"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { createAdminSessionCookie, getAdminCookieName } from "@/lib/admin-auth";

export async function loginAction(formData: FormData) {
  const token = String(formData.get("token") ?? "");
  const adminToken = process.env.ADMIN_TOKEN;
  const adminSessionSecret = process.env.ADMIN_SESSION_SECRET ?? "change-me-too";

  if (!adminToken || token !== adminToken) {
    redirect("/admin/login?error=1");
  }

  const cookieStore = await cookies();
  cookieStore.set(getAdminCookieName(), await createAdminSessionCookie(adminSessionSecret), {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
  });

  redirect("/admin");
}

export async function logoutAction() {
  const cookieStore = await cookies();
  cookieStore.delete(getAdminCookieName());
  redirect("/admin/login");
}
