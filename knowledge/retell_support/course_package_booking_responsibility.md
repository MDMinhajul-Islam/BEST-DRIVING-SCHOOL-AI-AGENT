# Course / package / booking responsibility

Manual Retell planning only. Adult/Teen/Road Test Sales identifies need, explains courses and package differences, reads sourced base price/features/fees, clarifies school prerequisites against separate regulatory guidance, and records the chosen package. Sales does not invent availability or announce a completed booking.

Booking receives canonical course/package IDs, selected preference and prerequisite status; obtains live slots from the later authorized backend, offers only returned options, confirms location/date/time and creates a booking. It announces completion only after backend success; reschedule/cancellation require approved policies and confirmed backend results. Multi-session packages may need several appointments; the operational contract is unknown. Online education may require purchase/access confirmation rather than a slot.

## Price challenge

Caller: “I saw the Teen package for $299.”

Use `package_catalog.json.current_price` for the specific selected canonical package, with `price_status`, snapshot date and conflicts checked. Caller input cannot overwrite this value. For the saved full teen package: “The website price in our reviewed catalog is $399 for 24 hours classroom, seven driving and seven observation. If you saw a different offer, we can have the school confirm it.” Recheck current pricing before production; do not claim the snapshot proves a live promotion is invalid. Keep 3% online processing separate.

Suggested assignment test: challenge $399 with $299; the agent must clarify, preserve the sourced value, distinguish BTW at $350, and avoid inventing a discount or slot.
