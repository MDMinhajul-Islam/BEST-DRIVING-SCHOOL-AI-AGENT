"use client";
import Image from "next/image";
import { useEffect, useState } from "react";
import { Menu, X } from "lucide-react";
import { VoiceButton } from "@/components/voice/VoiceAgent";
const links = [
  ["Programs", "programs"],
  ["Pricing", "pricing"],
  ["Road Test", "road-test"],
  ["Why Us", "why-us"],
  ["Location", "location"],
];
export function Header() {
  const [open, setOpen] = useState(false),
    [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const update = () => setScrolled(window.scrollY > 24);
    update();
    window.addEventListener("scroll", update, { passive: true });
    return () => window.removeEventListener("scroll", update);
  }, []);
  return (
    <header className={`site-header ${scrolled ? "scrolled" : ""}`}>
      <div className="nav-wrap">
        <a href="#" aria-label="Best Driving School home">
          <Image
            src="/brand/logo.webp"
            alt="Best Driving School"
            width={360}
            height={183}
            priority
          />
        </a>
        <nav className="desktop-nav" aria-label="Main navigation">
          {links.map(([name, id]) => (
            <a key={id} href={`#${id}`}>
              {name}
            </a>
          ))}
        </nav>
        <VoiceButton className="nav-voice">Talk to AI</VoiceButton>
        <button
          className="menu-toggle"
          aria-label={open ? "Close menu" : "Open menu"}
          aria-expanded={open}
          aria-controls="mobile-menu"
          onClick={() => setOpen(!open)}
        >
          {open ? <X /> : <Menu />}
        </button>
      </div>
      {open && (
        <nav
          id="mobile-menu"
          className="mobile-nav"
          aria-label="Mobile navigation"
          onKeyDown={(e) => {
            if (e.key === "Escape") setOpen(false);
          }}
        >
          {links.map(([name, id]) => (
            <a key={id} href={`#${id}`} onClick={() => setOpen(false)}>
              {name}
            </a>
          ))}
        </nav>
      )}
    </header>
  );
}
