import type { Metadata } from "next";
import { VoiceProvider } from "@/components/voice/VoiceProvider";
import { VoiceAgentModal } from "@/components/voice/VoiceAgentModal";
import "./globals.css";
export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.SITE_ORIGIN || "https://bestdrivingschool.us",
  ),
  title: "Best Driving School | Plano, TX — Ask. Learn. Drive.",
  description:
    "Find your next step with Best Driving School in Plano. Explore teen driver education, adult driving lessons and road tests, or talk to our AI assistant.",
  openGraph: {
    title: "Your driving journey, one conversation away.",
    description:
      "Teen programs, adult lessons and road tests in Plano, Texas. Meet Best Driving School.",
    type: "website",
    images: [
      {
        url: "/brand/logo.webp",
        width: 360,
        height: 183,
        alt: "Best Driving School",
      },
    ],
  },
  robots: { index: true, follow: true },
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <VoiceProvider>
          <a className="skip-link" href="#main">
            Skip to content
          </a>
          {children}
          <VoiceAgentModal />
        </VoiceProvider>
      </body>
    </html>
  );
}
