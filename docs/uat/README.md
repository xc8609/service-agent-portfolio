# Owner UAT pack — bank service core

Purpose: the business owner decides whether the merged workflow does what the accepted
rules say, using the running synthetic demo. Automated tests prove behaviour; this pack
records a person's acceptance. Nothing here is pre-filled as passed.

The owner delegated a browser-based assessment on 21 October 2026:
[executed results, defects and reference practices](2026-10-21-delegated-assessment.md).
Its decision is **changes required**; it does not fill in the owner's personal sign-off below.

## Setup

```bash
python3 scripts/configure_demo.py
docker compose up --build --wait
```

Open http://127.0.0.1:8000. Start with a fresh demo database. Use the persona selectors
named in each step. Record each result in the table at the end.

## Scenarios

| # | Requirement | Persona / section | Steps | Expected result |
|---|---|---|---|---|
| U1 | FR-01, NFR-01 | Inbound: *Customer not verified* | Start contact, try a search | Access denied; no customer data shown |
| U2 | FR-03 | Inbound: *Verified* — sections 1–3 | Search `DEMO STORE`, select both entries, inspect | Both entries, pending/posted states, "no relationship recorded"; no duplicate claimed |
| U3 | FR-02, FR-23 | Section 4 | Record "one purchase, cannot tell which" and save | Saved revision; recognition stored as unresolved; no entry chosen as the duplicate |
| U4 | FR-05, FR-04 | Rules and related cases | Read the cited rule and related case | Rule ID/version shown; existing case, owner and due time shown before any new enquiry |
| U5 | FR-06, FR-26 | Offline assistant, section 5 | Run the assistant; load the draft; return it with a reason | Cited draft; returned draft cannot be approved; no note committed |
| U6 | FR-08 | Section 5 | Write and approve a note | Receipt shown; note history lists it as committed |
| U7 | FR-16, FR-24, FR-25 | Section 6 | Prepare an enquiry with a material gap and unusable contact details; approve | Receipt with queue; contact-resolution task created; original deadline kept |
| U8 | FR-24 | Section 7 · *Demo specialist Alex*, then *Another feedback representative* | Claim; request material; as the representative record "Customer declined"; reopen as specialist | Specialist back to investigating; answer visible; deadline unchanged |
| U9 | FR-17 | Section 7 · *Demo specialist Alex* | Publish a finding with private notes | Finding recorded; private notes never shown to feedback staff |
| U10 | FR-18, FR-19 | Section 7 · *Feedback representative* | Claim feedback; open callback; record "no answer" | Work stays open (retry); not closed |
| U11 | FR-18 | Same | Approve explanation, simulate verified identity, retrieve disclosure, record verified feedback | Disclosure only after fresh identity; feedback completed; case still open until closure |
| U12 | FR-19 | *Responsible queue lead* | After attempts are exhausted, approve a new plan or hold | Reasoned decision recorded; original attempts and deadline kept |
| U13 | FR-27 | Inbound *Verified* → related cases | On a case with a published finding, record a disagreement | Case under review; closure history kept; nothing refunded |
| U14 | FR-21, FR-28 | Callback objection with complaint; *Complaint intake coordinator* | Request a complaint; after the worker runs, record acknowledgement | Complaint delivered and acknowledged independently of the re-review |
| U15 | FR-12 | Any | With the assistant failing or unused, complete U6–U7 manually | Manual path fully usable |

U14 needs the background worker (included in Docker Compose).

## Record

| # | Pass / fail | Notes, defects or decision |
|---|---|---|
| U1 | | |
| U2 | | |
| U3 | | |
| U4 | | |
| U5 | | |
| U6 | | |
| U7 | | |
| U8 | | |
| U9 | | |
| U10 | | |
| U11 | | |
| U12 | | |
| U13 | | |
| U14 | | |
| U15 | | |

Sign-off: owner name, date, environment (commit SHA, fixture version) and overall decision
(accept / accept with listed defects / reject). Defects become issues linked to the
requirement ID; failed rules are not silently changed in the specification.
