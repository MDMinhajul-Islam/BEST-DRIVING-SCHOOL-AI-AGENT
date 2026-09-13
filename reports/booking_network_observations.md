# Booking network observations

Investigation date: 2026-09-13. Frontend observations, public date/time reads and backend-authoritative facts are distinguished. No private account or write workflow was traversed.

Evidence labels: JS/form declaration, browser-visible UI, and anonymous read-only replay. A raw DevTools request capture was unavailable; no headers/cookies are fabricated.

| Action | Method | Endpoint | Request fields | Response fields | Authentication observed | State changing? | Read-only safe? | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Road test date selected | GET | /api/appointment-times | date | array of time labels (27 for one date); object-value fallback in JS | None required for read replay | No state change observed/intended; date-time query only | Yes, isolated time-only response | enroll.js loadTimes, form data-enroll-api, sanitized read evidence |
| Adult dates contract | GET | /api/adult-appointment-times | date | array of time labels (0 for one date); object-value fallback in JS | None required for read replay | No state change observed/intended; date-time query only | Yes, isolated time-only response | enroll.js loadTimes, form data-enroll-api, sanitized read evidence |
| Teen/PTDE declared times contract | GET | /api/teen-appointment-times | date | array of time labels (5 for one date); object-value fallback in JS | None required for read replay | No state change observed/intended; date-time query only | Yes, isolated time-only response | enroll.js loadTimes, form data-enroll-api, sanitized read evidence |
| Enrollment/payment transition (NOT EXECUTED) | POST declaration | /product/index/payment | Public form field names, product_id and appointment fields as applicable; personal values omitted | UNKNOWN | Auth/CSRF/server validation UNKNOWN | Potential enrollment/payment/booking changes | NO | Preserved form action; Submit was not clicked |

No lookup/reschedule/cancel request was observed. Required headers from JS: Accept application/json; other browser headers/cookies not recorded. Read replay status: 200 for each GET; redirect/auth behavior beyond that single read is unknown. No query-grid enumeration.
