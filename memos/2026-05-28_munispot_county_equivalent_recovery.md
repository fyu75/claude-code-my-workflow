# County-Government Coverage in the Delivery — After Applying the County-Equivalent Naming Fix

**Date:** 2026-05-28
**Re:** We re-checked county-government coverage after accounting for the point that states name county-equivalents differently (parishes, boroughs, independent cities). Below is the overall picture and a precise statement of what is still missing.

---

## What we did

You noted that some apparently-missing counties may simply carry a different label — Louisiana **parishes**, Alaska **boroughs**, Virginia **independent cities**, and consolidated **city-counties** (Denver, Philadelphia, Honolulu, and others) 

We applied that correction. A county-equivalent is counted as covered if it has a `County-General Purpose Government` record **or** a municipality record that is itself the county-equivalent government (independent city, consolidated city-county, or Alaska borough). A county is **not** counted as covered merely because some city inside it filed.

---

## Overall coverage

Against the 3,143 US county-equivalents (50 states + DC):

| | County-equivalents | Share |
|---|---:|---:|
| Covered in at least one year | 1,946 | **61.9%** |
| Covered in both FY2017 and FY2024 | 994 | 31.6% |
| Covered in all nine years (FY2016–24) | 639 | 20.3% |
| **Missing entirely** | **1,197** | **38.1%** |

The naming fix mattered but was modest. Parishes were **already** labeled correctly as county governments, so nothing was recovered there. The genuine relabeling gains — Virginia independent cities, Alaska boroughs, and consolidated city-counties — added **71** county-equivalents (from 1,879 under the strict label to 1,950). It does not close the bulk of the gap.

---

## What remains missing, and in what form

The 1,197 missing county-equivalents split into two distinct cases:

- **874 — county government absent, but a local entity is present.** For these, your delivery already contains a city, school district, or other entity located in the county, yet the **county government itself** never appears under any label. The geography is in your pipeline; the county-level filer is not. These are the most actionable, because the county is clearly within scope.
- **323 — entirely absent.** No record of any kind for the county-equivalent in any year.

A small portion of the 1,197 is structural rather than a true gap: Connecticut (8), Rhode Island (5), and Vermont (14) have effectively no general-purpose county governments, so no county-government ACFR can exist for them. That accounts for ~27 of the missing; the remaining ~1,170 are not explained by the absence of a county government.

---

## Does the complete FIPS information close the gap?

We confirmed the point that essentially every observation carries FIPS: `state_fips` is present on **99.98%** of rows, and a full 5-digit county code on **94.8%**. The FIPS fields are excellent, and we rely on them to join the delivery to our other data.

But complete FIPS does **not** recover the missing counties, because FIPS is an *identifier* — which county an entity sits in — not a financial record. The arithmetic makes this concrete: the filing entities in the delivery carry FIPS that reach **2,844** distinct counties, yet only **1,950** of those counties have an actual county-government record. The other ~894 counties are "reachable" by FIPS only because a **city, school district, or special district** located there filed — and those rows carry that county's FIPS. A row tagged FIPS `06037` that belongs to the *City of Long Beach* is a Long Beach record, not a Los Angeles County record.

So the 874 "county absent, local entity present" counties above are precisely the cases where FIPS is correct and complete, the county is plainly visible in the data's geography, **and the county government's financial statement still isn't there.** Complete FIPS is what let us measure the gap exactly; it cannot fill it.

---

## Do the year-gaps reflect a minimum-filing threshold?

The threshold idea points in two different directions, and the distinction matters.

**A revenue- or spending-based threshold does not explain the gaps.** Among the county governments that do appear, **about two-thirds (1,300 of 1,957) are missing at least one year** between FY2016 and FY2024. We measured how large those gap counties are, using the `TOTAL REVENUES` they reported in the years they *did* file:

| Typical annual total revenue of the gap counties | Share |
|---|---:|
| above $100,000 | **99.5%** |
| above $1 million | 98.2% |
| above $10 million | 67.2% |
| above $50 million | 22.6% |

The median gap county runs **$16.3 million** in annual total revenue; even the 10th percentile is **$4.1 million**. So if the rule were "don't file when total revenue or spending falls below $10K–$100K," it cannot explain these counties: a government reporting $16 million one year and absent the next is two to four orders of magnitude above any such floor.

**But the threshold that actually governs this delivery is a different one.** The data is compiled from Single Audit filings in the Federal Audit Clearinghouse. Under the Single Audit Act, an entity is only required to file when it expends **$750,000 or more in federal awards** in a given year (the figure for fiscal years through FY2024; raised to $1,000,000 for years beginning on/after Oct 1, 2024). That threshold is on **federal awards, not total revenue** — and federal awards swing year to year independently of a county's size. A $16 million county can expend $2 million in federal grants one year (and file) and under $750K the next (and not file), dropping out of the clearinghouse even though its overall budget never moved.

So the federal-award threshold is a live candidate for the year-gaps, and our revenue test does not rule it out. The two explanations are easy to confuse because both involve a dollar "threshold," but they behave oppositely: a revenue floor would hit only tiny governments, whereas the federal-award floor can intermittently drop even large ones. This is the precise point to settle with you (see question 3).

---

## Where the gaps concentrate

Coverage is highly uneven across states. Several states have almost no county governments in the delivery:

| State | County-equivalents | Covered | Coverage |
|---|---:|---:|---:|
| Oklahoma | 77 | 2 | 3% |
| Kansas | 105 | 7 | 7% |
| Arkansas | 75 | 7 | 9% |
| Indiana | 92 | 17 | 18% |
| Missouri | 115 | 24 | 21% |
| Nebraska | 93 | 22 | 24% |
| Kentucky | 120 | 32 | 27% |

And several states have **zero** county-government coverage: South Dakota (66 counties), New Jersey (21), plus the structural cases above (VT, CT, RI) and DC.

By raw count, the largest missing blocks are Texas (99 of 254), Kansas (98), Missouri (91), Kentucky (88), Oklahoma (75), and Indiana (75).

---

## Questions for you

1. **The 874 "local entity present, county absent" cases** — these counties are clearly within your collection geography. Can the county-government filings for them be added, or is there a reason the county-level entity drops out while a city in the same county comes through?
2. **The near-zero and zero-coverage states** (OK 3%, KS 7%, AR 9%, SD 0%, NJ 0%) — is there a systematic cause, e.g., a state filing framework or a source feed that isn't being ingested for those states?
3. **Year-gaps and the Single Audit trigger** — because the delivery is built from Single Audit filings, is it the case that an otherwise-covered county drops the specific years in which it didn't expend $750K in federal awards (and so wasn't required to file)? If so, the year-gaps are structural to the Single-Audit source rather than random, and those particular county-years simply cannot be supplied from this pipeline — which we'd want to know, since it determines whether we fill them ourselves from the underlying ACFRs. (A revenue threshold isn't the cause: the gap counties run $16M median, far above any such floor.)
