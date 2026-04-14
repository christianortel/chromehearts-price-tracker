const COOKIE_NAME = "chpi_admin_session";
const encoder = new TextEncoder();

async function signValue(value: string, secret: string) {
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );
  const signature = await crypto.subtle.sign("HMAC", key, encoder.encode(value));
  return Array.from(new Uint8Array(signature))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

export function getAdminCookieName() {
  return COOKIE_NAME;
}

export async function createAdminSessionCookie(secret: string) {
  return `authorized.${await signValue("authorized", secret)}`;
}

export async function verifyAdminSessionCookie(value: string | undefined, secret: string) {
  if (!value) {
    return false;
  }
  const expected = await createAdminSessionCookie(secret);
  return value === expected;
}
