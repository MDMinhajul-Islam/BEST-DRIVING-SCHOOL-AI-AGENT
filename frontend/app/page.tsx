import Image from "next/image";
import {
  ArrowUpRight,
  ArrowRight,
  MapPin,
  Check,
  Star,
  Route,
  ShieldCheck,
  CalendarDays,
} from "lucide-react";
import { Header } from "@/components/layout/Header";
import {
  VoiceAgent,
  VoiceButton,
  VoiceOrb,
} from "@/components/voice/VoiceAgent";
import { RoadVisual } from "@/components/hero/RoadVisual";
import { school } from "@/lib/content/school";
import { programs } from "@/lib/content/programs";
export default function Home() {
  const adminUrl =
    process.env.NEXT_PUBLIC_ADMIN_URL ||
    "https://minhaj-bdsbackend-xbnn3q-3c4628-206-189-183-167.sslip.io/admin";
  return (
    <>
      <Header />
      <main id="main">
        <section id="hero" className="hero">
          <RoadVisual />
          <div className="hero-grid container">
            <div className="hero-copy">
              <p className="eyebrow">
                <span /> PLANO, TEXAS · YOUR ROAD STARTS HERE
              </p>
              <h1>
                Your Texas <br />
                driving journey,
                <br />
                <span>one conversation</span>
                <br />
                away.
              </h1>
              <p className="hero-intro">
                A first lesson. A fresh start. Your next milestone.
                <br className="desktop-break" /> Talk with our AI assistant and
                find the right path for you.
              </p>
              <VoiceButton>Talk to our AI</VoiceButton>
              <a className="hero-phone" href={`tel:${school.telephone}`}>
                or call {school.phone} <ArrowUpRight size={13} />
              </a>
              <div className="hero-trust">
                <span>
                  <Check />
                  Teen & adult programs
                </span>
                <span>
                  <Check />
                  Open 7 days
                </span>
                <span>
                  <Check />
                  Local Plano office
                </span>
              </div>
            </div>
            <div className="hero-console">
              <VoiceAgent />
              <div className="console-caption">
                <span>LESS SEARCHING. MORE CLARITY.</span>
                <span>01 / YOUR NEXT STEP</span>
              </div>
            </div>
          </div>
          <div className="hero-bottom container">
            <span>CONFIDENCE STARTS WITH A CONVERSATION.</span>
            <a href="#programs">
              EXPLORE THE ROAD AHEAD <ArrowRight size={15} />
            </a>
          </div>
        </section>
        <section className="trust-strip">
          <div className="container trust-grid">
            <div className="rating-proof">
              <Star fill="currentColor" size={23} />
              <strong>
                {school.rating}
                <small>/ 5</small>
              </strong>
              <span>
                Google rating<small>School website · {school.snapshot}</small>
              </span>
            </div>
            {school.proof.map((p, i) => (
              <div className="proof-item" key={p}>
                {i === 0 ? (
                  <ShieldCheck />
                ) : i === 1 ? (
                  <Route />
                ) : (
                  <CalendarDays />
                )}
                <span>{p}</span>
              </div>
            ))}
          </div>
        </section>
        <section className="section container" id="programs">
          <div className="section-heading">
            <div>
              <p className="eyebrow dark">A CLEARER WAY FORWARD</p>
              <h2>
                Big questions.
                <br />
                <span>Simple conversations.</span>
              </h2>
            </div>
            <p>
              You don’t have to figure it all out first.
              <br />
              Start with what’s on your mind.
            </p>
          </div>
          <div className="intent-grid">
            {school.intents.map((intent, i) => (
              <div className="intent" key={intent}>
                <span className="index">0{i + 1}</span>
                <h3>{intent}</h3>
                <VoiceButton className="intent-action">Ask the AI</VoiceButton>
              </div>
            ))}
          </div>
        </section>
        <section id="pricing" className="pricing-section">
          <div className="section container">
            <div className="section-heading">
              <div>
                <p className="eyebrow dark">PROGRAMS, AT A GLANCE</p>
                <h2>
                  A path for every
                  <br />
                  <span>kind of beginning.</span>
                </h2>
              </div>
              <p>
                Explore a few starting points.
                <br />
                Our assistant can help you choose.
              </p>
            </div>
            <div className="program-list">
              {programs.map((p, i) => (
                <a className="program-row" href={p.url} key={p.id}>
                  <span className="index">0{i + 1}</span>
                  <div>
                    <h3>{p.title}</h3>
                    <p>{p.detail}</p>
                  </div>
                  <div className="program-price">
                    <span>BASE PRICE</span>
                    <strong>
                      {new Intl.NumberFormat("en-US", {
                        style: "currency",
                        currency: "USD",
                        maximumFractionDigits: 2,
                        minimumFractionDigits: 0,
                      }).format(p.price)}
                    </strong>
                  </div>
                  <ArrowUpRight className="program-arrow" />
                </a>
              ))}
            </div>
            <p className="price-note">
              Published base prices from {school.snapshot}. Online payments
              carry a separate 3% processing charge. Confirm current pricing,
              eligibility and scheduling with the school. Course links open the
              school’s existing enrollment pages.
            </p>
          </div>
        </section>
        <section id="road-test" className="section container">
          <div className="road-card">
            <div>
              <p className="eyebrow">THE NEXT MILESTONE</p>
              <h2>
                Your road test.
                <br />A familiar place
                <br />
                <span>to move forward.</span>
              </h2>
              <p>
                Explore third-party road testing at our Plano location. Ask
                about preparation, what to bring and your next steps.
              </p>
              <VoiceButton className="button light-button">
                Ask about Road Tests
              </VoiceButton>
            </div>
            <div className="road-art" aria-hidden="true">
              <div className="road-circle">
                <span>
                  YOUR NEXT
                  <br />
                  <strong>CHAPTER.</strong>
                </span>
                <ArrowUpRight />
              </div>
              <div className="lane lane-left" />
              <div className="lane lane-center" />
              <div className="lane lane-right" />
              <span className="road-art-caption">
                PLANO, TX
                <br />
                YOUR NEXT STEP
              </span>
            </div>
          </div>
        </section>
        <section id="why-us" className="section container why-section">
          <div>
            <p className="eyebrow dark">LOCAL ROADS. PERSONAL GUIDANCE.</p>
            <h2>
              Confidence is built.
              <br />
              <span>One lesson at a time.</span>
            </h2>
            <p>
              From your first time behind the wheel to preparing for a road
              test, find support close to home.
            </p>
          </div>
          <div className="why-list">
            {school.why.map((item, i) => (
              <div key={item.title}>
                <span className="index">0{i + 1}</span>
                <div>
                  <h3>{item.title}</h3>
                  <p>{item.text}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
        <section className="reviews-section">
          <div className="section container">
            <div className="review-heading">
              <div>
                <p className="eyebrow dark">FROM THE PASSENGER SEAT</p>
                <h2>
                  Real steps.
                  <br />
                  <span>New confidence.</span>
                </h2>
              </div>
              <a href={school.reviewsUrl} className="review-rating">
                <span className="stars" aria-label="5 stars">
                  ★★★★★
                </span>
                <strong>
                  {school.rating}
                  <small> / 5</small>
                </strong>
                <span>
                  {school.reviewCount} Google reviews <ArrowUpRight size={15} />
                </span>
                <small>As shown on the school website, {school.snapshot}</small>
              </a>
            </div>
            <div className="reviews-grid">
              {school.testimonials.map((r) => (
                <figure key={r.name}>
                  <span className="quote-mark" aria-hidden="true">
                    “
                  </span>
                  <blockquote>{r.quote}</blockquote>
                  <figcaption>
                    <span className="review-avatar">{r.name[0]}</span>
                    <div>
                      {r.name}
                      <small>Student testimonial · school website</small>
                    </div>
                  </figcaption>
                </figure>
              ))}
            </div>
          </div>
        </section>
        <section id="location" className="section container location-section">
          <div>
            <p className="eyebrow dark">RIGHT HERE IN PLANO</p>
            <h2>
              Your neighborhood.
              <br />
              <span>Your driving school.</span>
            </h2>
            <p>Serving {school.areas.join(", ")}.</p>
            <address>
              {school.name}
              <br />
              {school.address}
              <br />
              {school.city}, {school.region} {school.postalCode}
            </address>
            <div className="location-links">
              <a href={school.directions}>
                Get directions <ArrowUpRight size={18} />
              </a>
              <a href={`tel:${school.telephone}`}>{school.phone}</a>
            </div>
          </div>
          <div
            className="location-art"
            aria-label="Illustration of the Plano office location, not a navigational map"
          >
            <div className="map-road map-road-a" />
            <div className="map-road map-road-b" />
            <div className="map-road map-road-c" />
            <span className="map-label">INDEPENDENCE PKWY</span>
            <div className="map-pin">
              <MapPin />
              <span>
                BEST DRIVING SCHOOL<small>Plano, Texas</small>
              </span>
            </div>
            <span className="map-note">YOUR LOCAL STARTING POINT</span>
          </div>
        </section>
        <section className="final-cta">
          <div className="container">
            <VoiceOrb small />
            <p className="eyebrow">LET’S FIND YOUR NEXT STEP</p>
            <h2>
              Still not sure which
              <br />
              driving program you need?
            </h2>
            <VoiceButton className="button light-button">
              Talk to Best Driving School AI
            </VoiceButton>
            <a href={`tel:${school.telephone}`}>Or call {school.phone}</a>
          </div>
        </section>
      </main>
      <footer className="container">
        <div className="footer-top">
          <Image
            src="/brand/logo.webp"
            alt="Best Driving School"
            width={360}
            height={183}
          />
          <p>
            {school.address}
            <br />
            {school.city}, {school.region} {school.postalCode} ·{" "}
            <a href={`tel:${school.telephone}`}>{school.phone}</a>
          </p>
          <a href="#programs">Programs</a>
          <a href={`${school.website}/privacy-policy`}>Privacy</a>
          <a href={`${school.website}/terms-and-conditions`}>Terms</a>
          <a className="staff-link" href={adminUrl}>
            Staff Login
          </a>
        </div>
        <div className="footer-bottom">
          <span>© {new Date().getFullYear()} Best Driving School</span>
          <span>ASK. LEARN. DRIVE.</span>
        </div>
      </footer>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            name: school.name,
            telephone: school.telephone,
            url: school.website,
            address: {
              "@type": "PostalAddress",
              streetAddress: school.address,
              addressLocality: school.city,
              addressRegion: school.region,
              postalCode: school.postalCode,
              addressCountry: "US",
            },
            areaServed: school.areas,
          }),
        }}
      />
    </>
  );
}
