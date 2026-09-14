"use client";
import { useEffect, useRef, useState } from "react";
import { Mic, X } from "lucide-react";
import { useVoice } from "./VoiceProvider";
import { VoiceAgent } from "./VoiceAgent";
export function VoiceAgentModal() {
  const v = useVoice(),
    dialog = useRef<HTMLDialogElement>(null);
  const [floating, setFloating] = useState(false);
  useEffect(() => {
    const hero = document.getElementById("hero");
    if (!hero) return;
    const observer = new IntersectionObserver(
      ([entry]) => setFloating(!entry.isIntersecting),
      { threshold: 0 },
    );
    observer.observe(hero);
    return () => observer.disconnect();
  }, []);
  useEffect(() => {
    const d = dialog.current;
    if (!d) return;
    if (v.modal) {
      d.showModal();
      const previous = document.body.style.overflow;
      document.body.style.overflow = "hidden";
      return () => {
        document.body.style.overflow = previous;
        d.close();
      };
    } else d.close();
  }, [v.modal]);
  return (
    <>
      {(floating || v.active) && !v.modal && (
        <button className="floating-voice" onClick={v.open}>
          <Mic size={19} />
          {v.active ? "Return to your call" : "Ask Best Driving School"}
          <span className="status-dot" />
        </button>
      )}
      <dialog
        ref={dialog}
        className="voice-dialog"
        aria-label="Best Driving School AI voice conversation"
        onKeyDown={(e) => {
          if (e.key !== "Tab") return;
          const items = dialog.current?.querySelectorAll<HTMLElement>(
            'button:not(:disabled), a[href], [tabindex="0"]',
          );
          if (!items?.length) return;
          const first = items[0],
            last = items[items.length - 1];
          if (e.shiftKey && document.activeElement === first) {
            e.preventDefault();
            last.focus();
          } else if (!e.shiftKey && document.activeElement === last) {
            e.preventDefault();
            first.focus();
          }
        }}
        onCancel={(e) => {
          e.preventDefault();
          v.close();
        }}
        onClick={(e) => {
          if (e.target === dialog.current) v.close();
        }}
      >
        <button
          className="close-dialog"
          onClick={v.close}
          aria-label="Close voice panel; active call continues"
        >
          <X size={20} />
        </button>
        {v.modal && <VoiceAgent />}
      </dialog>
    </>
  );
}
