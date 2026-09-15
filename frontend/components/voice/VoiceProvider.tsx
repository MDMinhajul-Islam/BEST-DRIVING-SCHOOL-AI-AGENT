"use client";
import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import type { RetellWebClient } from "retell-client-js-sdk";
import { retellProvider, VoiceSessionError } from "@/lib/voice/retell";
export type VoiceState =
  | "idle"
  | "requesting"
  | "connecting"
  | "connected"
  | "user-speaking"
  | "speaking"
  | "muted"
  | "ended"
  | "error";
type VoiceContext = {
  state: VoiceState;
  message: string;
  seconds: number;
  muted: boolean;
  active: boolean;
  busy: boolean;
  start: () => void;
  end: () => void;
  toggleMute: () => void;
  open: () => void;
  close: () => void;
  modal: boolean;
  level: number;
};
const Context = createContext<VoiceContext | null>(null);
export function useVoice() {
  const value = useContext(Context);
  if (!value) throw new Error("VoiceProvider required");
  return value;
}
export function VoiceProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<VoiceState>("idle"),
    [message, setMessage] = useState(""),
    [seconds, setSeconds] = useState(0),
    [muted, setMuted] = useState(false),
    [modal, setModal] = useState(false),
    [level, setLevel] = useState(0);
  const client = useRef<RetellWebClient | null>(null),
    locked = useRef(false),
    generation = useRef(0),
    controller = useRef<AbortController | null>(null),
    timer = useRef<ReturnType<typeof setTimeout> | null>(null),
    started = useRef(0);
  const mutedRef = useRef(false);
  const active = ["connected", "user-speaking", "speaking", "muted"].includes(
      state,
    ),
    busy = ["requesting", "connecting"].includes(state);
  function cleanup() {
    mutedRef.current = false;
    if (timer.current) clearTimeout(timer.current);
    controller.current?.abort();
    const c = client.current;
    client.current = null;
    c?.removeAllListeners();
    c?.stopCall();
    locked.current = false;
    setMuted(false);
    setLevel(0);
  }
  function end() {
    generation.current++;
    cleanup();
    setState("ended");
    setMessage("Conversation ended. We’re here whenever you need us.");
  }
  async function start() {
    if (locked.current) return;
    if (process.env.NEXT_PUBLIC_VOICE_DEMO_MODE !== "false") {
      setState("error");
      setMessage(
        "Voice demo unavailable — connect Retell credentials to enable calls.",
      );
      return;
    }
    if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) {
      setState("error");
      setMessage(
        "Voice calling needs a browser with microphone support over HTTPS. You can also call the school.",
      );
      return;
    }
    locked.current = true;
    const id = ++generation.current;
    setState("requesting");
    setMessage("");
    setSeconds(0);
    const fail = (text: string) => {
      if (id !== generation.current) return;
      generation.current++;
      cleanup();
      setState("error");
      setMessage(text);
    };
    timer.current = setTimeout(
      () =>
        fail("Connecting took too long. Check your connection and try again."),
      30000,
    );
    try {
      setState("connecting");
      const { RetellWebClient } = await import("retell-client-js-sdk");
      if (id !== generation.current) return;
      const c = new RetellWebClient();
      client.current = c;
      c.on("call_started", () => {
        if (id !== generation.current) return;
        if (timer.current) clearTimeout(timer.current);
        started.current = Date.now();
        setState("connected");
      });
      c.on("call_ended", () => {
        if (id !== generation.current) return;
        generation.current++;
        cleanup();
        setState("ended");
        setMessage(
          "The call has ended. Start a new conversation or call the school if you still need help.",
        );
      });
      c.on("agent_start_talking", () => {
        if (id === generation.current) setState("speaking");
      });
      c.on("agent_stop_talking", () => {
        if (id === generation.current) {
          setState("connected");
          setLevel(0);
        }
      });
      c.on("audio", (samples: Float32Array) => {
        if (id !== generation.current || !c.isAgentTalking) return;
        let sum = 0;
        for (const v of samples) sum += v * v;
        setLevel(Math.min(1, Math.sqrt(sum / Math.max(1, samples.length)) * 5));
      });
      c.on("error", () =>
        fail(
          "The audio connection was interrupted. Check your microphone and network, then try again.",
        ),
      );
      controller.current = new AbortController();
      const session = await retellProvider.createSession(
        controller.current.signal,
      );
      if (id !== generation.current) return;
      await c.startCall({
        accessToken: session.accessToken,
        emitRawAudioSamples: true,
      });
      if (id !== generation.current) {
        c.removeAllListeners();
        c.stopCall();
      }
    } catch (error) {
      if (id !== generation.current) return;
      const name = error instanceof Error ? error.name : "";
      fail(
        name === "NotAllowedError"
          ? "We couldn’t access your microphone. Allow microphone access in your browser and try again."
          : name === "NotFoundError" || name === "NotReadableError"
            ? "Your microphone is missing or in use. Check your audio device and try again."
            : error instanceof TypeError
              ? "We couldn’t reach the voice service. Check your connection and try again."
              : error instanceof VoiceSessionError
                ? error.message
                : "We couldn’t start your call. Check your audio device and try again.",
      );
    }
  }
  function toggleMute() {
    const c = client.current;
    if (!c || !active) return;
    if (muted) c.unmute();
    else c.mute();
    mutedRef.current = !muted;
    setMuted(!muted);
  }
  useEffect(() => {
    if (!active) return;
    const interval = setInterval(
      () => setSeconds(Math.floor((Date.now() - started.current) / 1000)),
      1000,
    );
    return () => clearInterval(interval);
  }, [active]);
  useEffect(
    () => () => {
      generation.current++;
      if (timer.current) clearTimeout(timer.current);
      controller.current?.abort();
      client.current?.removeAllListeners();
      client.current?.stopCall();
    },
    [],
  );
  return (
    <Context.Provider
      value={{
        state,
        message,
        seconds,
        muted,
        active,
        busy,
        start,
        end,
        toggleMute,
        open: () => setModal(true),
        close: () => setModal(false),
        modal,
        level,
      }}
    >
      {children}
    </Context.Provider>
  );
}
