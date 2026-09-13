# Router intent reference

Data organization for manual workflow design; this is not a production router prompt. Caller meaning, age and licensing stage will be considered in the later workflow.

| Intent | Knowledge tag | Reference |
| --- | --- | --- |
| general_license_guidance | license_guide | School licensing statements; official verification pending |
| adult_course | adult_sales | Adult six-hour online course; driving lessons are separate |
| adult_driving_lesson | adult_sales | Adult private driving sessions and package options |
| teen_driver_education | teen_sales | Teen classroom + driving + observation package |
| teen_driving_only | teen_sales | Behind-the-wheel-only package; retain published requirements |
| parent_taught | teen_sales | Parent-taught logged practice packages |
| road_test | road_test_sales | Test-only and practice + test packages |
| booking | booking | Static prerequisites and locations; live backend required |
| reschedule | booking | Verified appointment and policy; backend required |
| cancellation | booking | Service-specific policy review and backend required |
| existing_student_support | student_support | FAQ and policies; private issues require verified system or human |
| pricing_question | relevant sales persona | Use sourced package observations; conflicting prices must be reviewed |
| location_question | global | Distinguish Plano office from surrounding service areas |
| unknown | manual fallback design | Clarification or human assistance |

Sources: ../source_index.md; ../../data/structured/courses.json and faq.json. Do not infer age from a caller asking for practice; do not interpret booking links as open slots.
