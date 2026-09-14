"use client";
import { motion, useReducedMotion } from "motion/react";
import { Mic, MicOff, PhoneOff, ArrowUpRight, AudioLines } from "lucide-react";
import { useVoice } from "./VoiceProvider";
import { school } from "@/lib/content/school";
export function VoiceOrb({ small = false }: { small?: boolean }) {
  return (
    <div className={`orb-scene ${small ? "orb-small" : ""}`} aria-hidden="true">
      <div className="orbit orbit-one" />
      <div className="orbit orbit-two" />
      <div className="orb">
        <AudioLines strokeWidth={1.2} />
      </div>
      <span className="orbit-dot" />
    </div>
  );
}
export function VoiceAgent() {
  const v = useVoice();
  const status = v.busy
    ? v.state === "requesting"
      ? "Allow microphone access…"
      : "Connecting…"
    : v.active
      ? v.muted
        ? "Microphone muted"
        : v.state === "speaking"
          ? "AI is speaking…"
          : v.state === "user-speaking"
            ? "Hearing you…"
            : "Listening…"
      : v.state === "ended"
        ? "Until your next question"
        : v.state === "error"
          ? "Let’s get you connected"
          : "Ready to help";
  return (
    <div className={`voice-console ${v.active ? "is-active" : ""}`}>
      <div className="console-top">
        <span>
          <span className="status-dot" /> YOUR PERSONAL DRIVING GUIDE
        </span>
        <AudioLines size={17} />
      </div>
      <VoiceOrb />
      <div className="voice-heading">Best Driving School AI</div>
      <div className="voice-status" role="status" aria-live="polite">
        {status}
      </div>
      <p className="voice-description">
        A little guidance. A lot more confidence.
        <br />
        Ask about courses, permits, prices or road tests.
      </p>
      <div className="waveform" aria-hidden="true">
        {Array.from({ length: 27 }, (_, i) => (
          <i
            key={i}
            style={{
              height: `${4 + (v.active ? v.level : 0) * 30 * (0.4 + (i % 5) / 6)}px`,
            }}
          />
        ))}
      </div>
      {v.active || v.busy ? (
        <div className="call-controls">
          <span className="call-timer" aria-label="Call duration">
            {String(Math.floor(v.seconds / 60)).padStart(2, "0")}:
            {String(v.seconds % 60).padStart(2, "0")}
          </span>
          {v.active && (
            <button
              className="mute-button"
              onClick={v.toggleMute}
              aria-label={v.muted ? "Unmute microphone" : "Mute microphone"}
              aria-pressed={v.muted}
            >
              {v.muted ? <MicOff size={20} /> : <Mic size={20} />}
            </button>
          )}
          <button className="end-button" onClick={v.end}>
            <PhoneOff size={18} />
            {v.busy ? "Cancel" : "End call"}
          </button>
        </div>
      ) : (
        <button className="start-button" onClick={v.start}>
          <Mic size={19} />
          {v.state === "ended"
            ? "Start another conversation"
            : v.state === "error"
              ? "Try voice conversation"
              : "Start Voice Conversation"}
          <ArrowUpRight size={18} />
        </button>
      )}
      {v.message && (
        <p className="voice-message" role="status">
          {v.message}{" "}
          {v.state === "error" && (
            <a href={`tel:${school.telephone}`}>Call {school.phone}</a>
          )}
        </p>
      )}
      <p className="privacy-note">
        Microphone access requested when you start.
        <br />
        You’ll speak with an AI.{" "}
        <a href={`${school.website}/privacy-policy`}>Privacy policy</a>
      </p>
      <div className="prompt-area">
        <span>NOT SURE WHERE TO START? TRY ASKING</span>
        <div>
          {school.prompts.slice(0, 2).map((p) => (
            <button
              key={p}
              onClick={(event) => {
                event.currentTarget
                  .closest(".voice-console")
                  ?.querySelector<HTMLButtonElement>(".start-button")
                  ?.focus();
              }}
            >
              {p}
              <ArrowUpRight size={13} />
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
export function VoiceButton({
  children,
  className = "button",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  const v = useVoice();
  const reduced = useReducedMotion();
  return (
    <motion.button
      whileHover={reduced ? undefined : { y: -2 }}
      transition={{ duration: 0.3 }}
      className={className}
      onClick={v.open}
    >
      <Mic size={18} />
      {children}
      <ArrowUpRight size={17} />
    </motion.button>
  );
}
