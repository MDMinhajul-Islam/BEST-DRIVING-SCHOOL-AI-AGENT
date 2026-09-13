# Booking system architecture

Design date: 2026-09-13. OUR NORMALIZED INTERFACE — not a claim about school endpoints or a Retell import.

Future manual Retell tools → our authenticated API → common BookingAdapter → school system. Current code supplies only adapters, not an HTTP server or deployed tools.

BestDrivingSchoolBookingAdapter: explicitly enabled date-only public GET reads; all production transaction/customer-lookup methods fail LIVE_WRITES_DISABLED without contacting the network. MockBookingAdapter: isolated in-memory synthetic slots/customer refs/bookings, verification guards, idempotent creation and atomic reschedule/cancel. No production data is seeded into mock.

Integration boundary: canonical catalog IDs → observed form product IDs (provisional) → authoritative mapping still required. Time-label normalization does not establish resource IDs or a real booking identity. Preserve separate adapter mode in every response; a mock success can never be spoken as a real school reservation.

Run offline investigation assembly: `python -m src.booking.investigate`. Live read is disabled by default; use enabled=True explicitly only for approved read-only observation and disable again with enabled=False/new default instance. No credentials/env keys are created because the actual authentication scheme is not known. No `.env.example` with guessed keys is needed.
