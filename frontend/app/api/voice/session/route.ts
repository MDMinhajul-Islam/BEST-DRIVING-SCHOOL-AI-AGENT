import { NextRequest, NextResponse } from "next/server";
export const runtime = "nodejs";
const reply = (body: object, status: number) =>
  NextResponse.json(body, { status, headers: { "Cache-Control": "no-store" } });
export async function POST(request: NextRequest) {
  if (
    !process.env.SITE_ORIGIN ||
    request.headers.get("origin") !== process.env.SITE_ORIGIN
  )
    return reply({ error: "forbidden" }, 403);
  if (
    process.env.NEXT_PUBLIC_VOICE_DEMO_MODE !== "false" ||
    !process.env.VOICE_PROXY_SECRET ||
    !process.env.VOICE_BACKEND_URL
  )
    return reply({ error: "service_unavailable" }, 503);
  try {
    const response = await fetch(
      `${process.env.VOICE_BACKEND_URL}/api/retell/web-call`,
      {
        method: "POST",
        headers: { "X-Voice-Proxy-Secret": process.env.VOICE_PROXY_SECRET },
        cache: "no-store",
        signal: AbortSignal.timeout(18000),
      },
    );
    if (!response.ok)
      return reply(
        { error: "service_unavailable" },
        response.status === 429 ? 429 : 503,
      );
    const data = await response.json();
    if (typeof data.access_token !== "string" || !data.access_token)
      return reply({ error: "service_unavailable" }, 503);
    return reply(
      { access_token: data.access_token, call_id: data.call_id },
      200,
    );
  } catch {
    return reply({ error: "service_unavailable" }, 503);
  }
}
