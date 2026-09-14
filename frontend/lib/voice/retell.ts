export class VoiceSessionError extends Error {}
export interface VoiceSessionProvider {
  createSession(
    signal: AbortSignal,
  ): Promise<{ accessToken: string; callId?: string }>;
}
export const retellProvider: VoiceSessionProvider = {
  async createSession(signal) {
    const response = await fetch("/api/voice/session", {
      method: "POST",
      signal,
      cache: "no-store",
    });
    if (!response.ok)
      throw new VoiceSessionError(
        response.status === 429
          ? "Please wait a minute before trying another call."
          : "Our voice assistant is temporarily unavailable. Please try again or call the school.",
      );
    const data = await response.json();
    if (typeof data.access_token !== "string")
      throw new VoiceSessionError(
        "Our voice assistant is temporarily unavailable. Please call the school.",
      );
    return { accessToken: data.access_token, callId: data.call_id };
  },
};
