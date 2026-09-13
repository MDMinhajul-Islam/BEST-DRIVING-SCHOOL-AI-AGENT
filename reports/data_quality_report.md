# Data quality report

Automatically generated. Schema/source checks do not certify semantic completeness or business correctness. Manual review is required before Retell upload.

| Check | Result |
| --- | --- |
| total sitemap urls | 18 |
| successful pages | 18 |
| failed pages | 0 |
| skipped pages | 0 |
| redirected pages | 0 |
| empty pages | 0 |
| pages with prices | 16 |
| pages with faqs | 10 |
| location pages | 4 |
| package count | 13 |
| faq count | 102 |
| policy statement count | 65 |
| licensing statement count | 336 |
| conflicts | 8 |
| unbound price claims | 149 |
| restricted links discovered not crawled | 1 |
| restricted requests | 0 |
| source references validated | 4189 |

## Page category coverage

- homepage: 1
- faq: 1
- policy: 2
- service: 4
- location: 4
- course: 6

Missing expected categories: None

## Exact duplicate observations

- faqs: 97 merged, sources retained
- contacts: 156 merged, sources retained
- policies: 0 merged, sources retained
- facts: 191 merged, sources retained
- licensing_guidance: 229 merged, sources retained
- links: 1215 merged, sources retained

Only exact repetitions are consolidated; no fuzzy removal of similar subject matter. Package observations retain all page-specific evidence.

## Conflicts and narrative pricing

- Is Best Driving School located in Plano?: faq_answer — possible_conflict_requires_review
- Is Best Driving School licensed by TDLR?: faq_answer — possible_conflict_requires_review
- Can international drivers take lessons?: faq_answer — possible_conflict_requires_review
- Are weekend lessons available?: faq_answer — possible_conflict_requires_review
- Can parent-taught students take professional lessons?: faq_answer — possible_conflict_requires_review
- Does Best Driving School guarantee a first-attempt pass?: faq_answer — possible_conflict_requires_review
- Terms age restrictions and teen services: platform_age_policy_vs_teen_services — possible_conflict_requires_review
- Adult education applicability wording: adult_education_applicability — possible_conflict_requires_review

149 narrative price claims remain unbound. These include FAQ answers, ranges, per-hour rates and promotional wording. They are preserved with evidence, but not automatically assigned as package prices. See `knowledge_base.json` and manual review findings.

## Missing fields

Null is retained for information not explicitly extracted; no inferred ages, total component sums, zero classroom hours, session counts or prerequisite guarantees. Details are in `knowledge/retell_support/unresolved_information.md`.

## Request audit

1 restricted links discovered but not crawled. 0 restricted requests. Out-of-domain links are recorded but never followed. Only allowed sitemap HTML pages are downloaded.

## Extraction warnings and validation errors

None

## Failed/skipped pages

None

## Changed pages

- https://bestdrivingschool.us/
  old_hash: beb04a12e7b854db404f833b6415f4f45a0d39a97877f0fa54724874d32cd4c6
  new_hash: f34dbf6ef50b5baf9fc7f1de9665c66245d490c726b4e04d37f599b20d16b266
- https://bestdrivingschool.us/faqs
  old_hash: 8c3975eb45f111dcda0c99f72f2dd54c82f767c01cf25bb106c70715d34454d7
  new_hash: bc4ba7502dbac0c346df5f209a5b5ece6778d698bfab2259d13886c7be83da31
- https://bestdrivingschool.us/terms-and-conditions
  old_hash: d65af9d37a39059f84e85950f4d1f1129971b08866e69277f688196eb558576f
  new_hash: f0343e203ab51d50562b9a60bbf081da67f030618f3e88b0e9a252f9484e984f
- https://bestdrivingschool.us/privacy-policy
  old_hash: 48fddc45ba554320a5588fa697fe44a878eaaa33deb11c647beca9b700bfdb25
  new_hash: 994bb4e2b665e7c28960e44535cbb00f98be1f8cb7cc72e426873b3910e35f69
- https://bestdrivingschool.us/services/driving-lessons-for-teens
  old_hash: 931f5fdf8c75a0c19fdadaa62318d4f6c70113f45269ba632b76067f69e1f1bf
  new_hash: b0c070e4208e5685e9772d5df13f63ff04c13b35d4650362bbf1d229b339328c
- https://bestdrivingschool.us/services/driving-lessons-for-adults
  old_hash: ed53e3b920f9c5eabe6d59c47d4a70747749500f59b8bac6452fe4551d8d1986
  new_hash: 7896f4f773da0eb58eb1f977a5808e55d491b3830694f19d4cb8f895eca5adaa
- https://bestdrivingschool.us/services/parent-taught-log-driving
  old_hash: 205a4919e44144501388b6c2a39f8cf55e2a32a3b9f810c9a8e8c91b269d5ed0
  new_hash: 810ecc5b9b9afb2ed69ef1273f63e745f67b3d76b06ba2fe5b4c4839825ee677
- https://bestdrivingschool.us/services/3rd-party-road-test
  old_hash: 071d7e7ecad15aa2e59d46d1fbae73b4cdd6813caf3db3b6e20c46880b36978d
  new_hash: b12eb44f7274f17039fa93714900c7419e401218d376ae45ff55a494b3d643e5
- https://bestdrivingschool.us/driving-school-plano
  old_hash: 884e2b35d292fe9d0139556e1880335978a5e577bc82fabb07f1b3fdafec385f
  new_hash: b676f601be3af20540e801e76c9fbf6d15513f4fb41ce991fdfbfeb7abc73fba
- https://bestdrivingschool.us/driving-school-allen
  old_hash: 769a9178df880da00a8de3ea530b3e8946f3728d595571844201fbc6d07065e4
  new_hash: d9b76ec62b37e9de968d1bee48b08cfbe08035169a27719eacf343b07860886b
- https://bestdrivingschool.us/driving-school-frisco
  old_hash: 91bd6a92165bc20d91371bc00c58991a63311ffb398cd7df752a8ba008a6f6a6
  new_hash: 3e5eb5e62485723b3e7df4fb5f07a1724c8794e56748b1b3e96327ef5743e417
- https://bestdrivingschool.us/driving-school-mckinney
  old_hash: 20ddc18a63aeb0081af2f34d7c2b350d99b738ced2c876516541643858c9217d
  new_hash: 40e66b7cba4280bf68e74afd40afbf2a622c2e30418e6b08d0ff8989e9d3091b
- https://bestdrivingschool.us/driving-courses/teen-24-hour-class-room-and-driving-package
  old_hash: f0d016855ce1566c4e43fa849b58f4b16beee0afd6706920d135e2b98854260c
  new_hash: bcca060a2ed0db00b0483d240866c69f401f828416a0744c4f16b89d0511b321
- https://bestdrivingschool.us/driving-courses/teen-behind-the-wheel-only
  old_hash: fa513a86280782e3819e40c7f0c2bafc97795d87b7e56f4f9f7529780b6e3ac1
  new_hash: 4d4081dcec33da4becc232e3458869ee1504623cd60cc7989f783e36554b6d9d
- https://bestdrivingschool.us/driving-courses/road-test
  old_hash: 52c24600bf5df6ed70f755edda2486c4211102d8cec5934d92eb5ae5dfaba159
  new_hash: a8aa5287dea2fba14e2d4edc8f59fe77569299f1d8d448dc1107e8d6cf9e795a
- https://bestdrivingschool.us/driving-courses/log-driving-hours
  old_hash: f8f60219aff2921e5f82fb12b534a380c9067f07fac81185afeb74f68bde682a
  new_hash: 31f27e4048610e372781c257353e340c708048dc6095633a290bc781012fefff
- https://bestdrivingschool.us/driving-courses/adult-driving-sessions
  old_hash: c51b4f03ee90fb99e18143999856745456e54947f0c30b801f96d6caadeb2ac6
  new_hash: 62cc34610588c98140532c920044db3e0fdb5514f264fa76f4889beb73c37938
- https://bestdrivingschool.us/driving-courses/adult-6-hours-online-permit-class
  old_hash: fef54df64984d24ceaff4a12b8ea0515273e4b06cbae00928d4c843d404ca1d4
  new_hash: de2ab1c446db8ad2b2b3d797b41800a3a123816e63e2c6fb3edc5cba05be4624

Raw changes can include generated form tokens. Cleaned public content changes: 0.

