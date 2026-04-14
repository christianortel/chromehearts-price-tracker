"use server";

import { revalidatePath } from "next/cache";

const API_BASE_URL = process.env.API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function adminFetch(path: string, init?: RequestInit) {
  const adminToken = process.env.ADMIN_TOKEN;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "x-admin-token": adminToken ?? "",
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    throw new Error(`Admin request failed: ${response.status}`);
  }
  return response;
}

export async function reviewSubmissionAction(formData: FormData) {
  const submissionId = String(formData.get("submissionId"));
  const decision = String(formData.get("decision"));
  const productId = String(formData.get("productId") ?? "").trim();
  const query = new URLSearchParams({ decision });
  if (productId) {
    query.set("product_id", productId);
  }
  await adminFetch(`/admin/submissions/${submissionId}/decision?${query.toString()}`, {
    method: "POST",
  });
  revalidatePath("/admin");
}

export async function autoMatchObservationAction(formData: FormData) {
  const observationId = Number(formData.get("observationId"));
  await adminFetch("/admin/match", {
    method: "POST",
    body: JSON.stringify({
      observation_id: observationId,
      decision: "matched",
    }),
  });
  revalidatePath("/admin");
}

export async function matchObservationAction(formData: FormData) {
  const observationId = Number(formData.get("observationId"));
  const decision = String(formData.get("decision") ?? "matched");
  const productIdValue = String(formData.get("productId") ?? "").trim();
  await adminFetch("/admin/match", {
    method: "POST",
    body: JSON.stringify({
      observation_id: observationId,
      product_id: productIdValue ? Number(productIdValue) : null,
      decision,
    }),
  });
  revalidatePath("/admin");
}

export async function addAliasAction(formData: FormData) {
  const productId = Number(formData.get("productId"));
  const aliasText = String(formData.get("aliasText") ?? "").trim();
  const aliasType = String(formData.get("aliasType") ?? "manual");
  if (!aliasText) {
    throw new Error("Alias text is required.");
  }
  await adminFetch(`/admin/products/${productId}/aliases`, {
    method: "POST",
    body: JSON.stringify({
      alias_text: aliasText,
      alias_type: aliasType,
      source_name: "admin",
    }),
  });
  revalidatePath("/admin/aliases");
  revalidatePath("/admin");
}

export async function deleteAliasAction(formData: FormData) {
  const aliasId = Number(formData.get("aliasId"));
  await adminFetch(`/admin/aliases/${aliasId}`, {
    method: "DELETE",
  });
  revalidatePath("/admin/aliases");
  revalidatePath("/admin");
}

export async function recomputeMetricsAction() {
  await adminFetch("/admin/recompute", {
    method: "POST",
    body: JSON.stringify({}),
  });
  revalidatePath("/admin");
}

export async function runSourceAction(formData: FormData) {
  const sourceId = Number(formData.get("sourceId"));
  const query = String(formData.get("query") ?? "chrome hearts").trim() || "chrome hearts";
  await adminFetch(`/admin/sources/${sourceId}/run`, {
    method: "POST",
    body: JSON.stringify({ query }),
  });
  revalidatePath("/admin");
}

export async function toggleSourceAction(formData: FormData) {
  const sourceId = Number(formData.get("sourceId"));
  const enabled = String(formData.get("enabled")) === "true";
  await adminFetch(`/admin/sources/${sourceId}/toggle`, {
    method: "POST",
    body: JSON.stringify({ enabled }),
  });
  revalidatePath("/admin");
}

export async function reviewDuplicateObservationAction(formData: FormData) {
  const observationId = Number(formData.get("observationId"));
  const decision = String(formData.get("decision") ?? "reject");
  await adminFetch("/admin/duplicates/review", {
    method: "POST",
    body: JSON.stringify({
      observation_id: observationId,
      decision,
    }),
  });
  revalidatePath("/admin/duplicates");
  revalidatePath("/admin");
}

export async function resolveDuplicateGroupAction(formData: FormData) {
  const duplicateGroupKey = String(formData.get("duplicateGroupKey") ?? "").trim();
  const keepObservationId = Number(formData.get("keepObservationId"));
  if (!duplicateGroupKey) {
    throw new Error("Duplicate group key is required.");
  }
  await adminFetch("/admin/duplicates/resolve", {
    method: "POST",
    body: JSON.stringify({
      duplicate_group_key: duplicateGroupKey,
      keep_observation_id: keepObservationId,
    }),
  });
  revalidatePath("/admin/duplicates");
  revalidatePath("/admin");
}
