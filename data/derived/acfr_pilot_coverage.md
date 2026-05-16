# ACFR Pilot Collection — Status Report

*Run 2026-05-16. Top-25 high-DC-share counties; 5-county pilot.*

## Sample status

| # | County | State | DC share | Source URL | Direct PDF | Status |
|---:|---|---|---:|---|---|---|
| 1 | Crook County | OR | 81% | https://co.crook.or.us/treasurer-finance/page/financial-stat… | ✓ | ✅ downloaded |
| 2 | Mecklenburg County | VA | 49% | https://www.apa.virginia.gov/local-government/reports/Financ… | ✓ | ✅ downloaded |
| 3 | Grant County | WA | 36% | https://www.grantcountywa.gov/1103/Annual-Reports-Strategic-… | ✓ | ✅ downloaded |
| 4 | Morrow County | OR | 186% | https://www.co.morrow.or.us/finance/page/financial-statement… | — | 🟡 source identified, not downloaded |
| 5 | Umatilla County | OR | 45% | https://www.co.umatilla.or.us/departments/finance | — | 🟡 source identified, not downloaded |
| 6 | Lawrence County | KY | 191% | Kentucky Auditor: auditor.ky.gov | — | ⚪ no source URL yet |
| 7 | Dickens County | TX | 181% | Texas: state comptroller filings | — | ⚪ no source URL yet |
| 8 | Storey County | NV | 176% | https://www.storeycounty.org/government/finance | — | 🟡 source identified, not downloaded |
| 9 | Milam County | TX | 157% | Texas: state comptroller filings | — | ⚪ no source URL yet |
| 10 | Dickey County | ND | 145% | ND State Auditor portal | — | ⚪ no source URL yet |
| 11 | Franklin County | NC | 131% | NC Treasurer — LGC reports | — | ⚪ no source URL yet |
| 12 | Cook County | GA | 122% | GA Department of Audits and Accounts | — | ⚪ no source URL yet |
| 13 | Knox County | TX | 115% | Texas comptroller | — | ⚪ no source URL yet |
| 14 | Crane County | TX | 74% | Texas comptroller | — | ⚪ no source URL yet |
| 15 | Mayes County | OK | 56% | OK State Auditor | — | ⚪ no source URL yet |
| 16 | Pend Oreille County | WA | 53% | WA SAO | — | ⚪ no source URL yet |
| 17 | Washington County | GA | 52% | GA Audits | — | ⚪ no source URL yet |
| 18 | Ward County | TX | 51% | Texas comptroller | — | ⚪ no source URL yet |
| 19 | Valencia County | NM | 49% | NM State Auditor | — | ⚪ no source URL yet |
| 20 | Pecos County | TX | 47% | Texas comptroller | — | ⚪ no source URL yet |
| 21 | Marshall County | KY | 43% | KY Auditor | — | ⚪ no source URL yet |
| 22 | Glasscock County | TX | 38% | Texas comptroller | — | ⚪ no source URL yet |
| 23 | Wilkes County | GA | 37% | GA Audits | — | ⚪ no source URL yet |
| 24 | Briscoe County | TX | 37% | Texas comptroller | — | ⚪ no source URL yet |
| 25 | Cherokee County | NC | 34% | NC LGC | — | ⚪ no source URL yet |

## Pilot status

**Pilot counties**: 5 (Crook OR, Mecklenburg VA, Grant WA, Morrow OR, Umatilla OR)
**ACFR PDFs downloaded**: 3 / 5  (crook_or, mecklenburg_va, grant_wa)

**Outstanding**: Morrow OR (need direct PDF URL from finance page), Umatilla OR (same).

## State-centralized portals worth leveraging

Several states centralize county financial reports — these are bulk sources that cover many of our remaining 20 targets:
- **VA Auditor of Public Accounts** — covers Mecklenburg + all VA counties
- **WA State Auditor (SAO)** — covers Grant + Pend Oreille + all WA counties
- **TX Comptroller** — bulk filing repository; covers Dickens, Milam, Knox, Crane, Ward, Pecos, Glasscock, Briscoe
- **NC Treasurer / LGC** — covers Franklin + Cherokee + all NC counties (standardized)
- **GA Department of Audits** — covers Cook, Washington, Wilkes
- **KY Auditor** — covers Lawrence, Marshall
- **OK State Auditor** — covers Mayes
- **ND State Auditor** — covers Dickey
- **NM State Auditor** — covers Valencia

Direct county websites needed for: OR counties (Crook, Morrow, Umatilla), NV (Storey).

## Parser scaffolding

`scripts/python/22_acfr_pdf_parser_pilot.py` extracts candidate matches for five GASB-standard line items:
- Property tax revenue
- Total general revenue
- Capital outlay
- Long-term debt
- Interest expense

Match strategy: regex on line-level text from `pdfplumber`. Returns top-3 candidate hits per pattern per PDF; human verifies which is the load-bearing one.

## Extracted samples (first 3 hits per pattern per pilot PDF)

### Crook County (OR)

**property_tax**:
  - p17: `Property taxes 14,808,139 14,320,739 - - 14,808,139 14,320,739`
  - p22: `Property taxes receivable 642,369 - 642,369`
  - p23: `Property taxes for general purposes 14,808,139 - 14,808,139`

**total_revenue**:
  - p17: `Total revenues 64,838,191 48,170,992 7 ,994,874 4 ,590,449 72,833,065 52,761,441`
  - p23: `Total general revenues 23,568,529 469,297 24,037,826`
  - p26: `Total Revenues 1 6,693,392 5 ,447,889 3,664,457 1 3,632,920 7 ,896,699 287,080 16,603,449 5,678,704 69,904,590`

**capital_outlay**:
  - p26: `Capital outlay 183,528 6 75,618 70,391 90,950 49,015 - 3,063,950 3 71,172 4,504,624`
  - p80: `Capital outlay - - - - - 205,117`
  - p88: `Capital Outlay - 4 00,000 (1) 2 05,117 1 94,883`

**lt_debt**:
  - p17: `Interest on long-term debt 213,541 199,689 241,116 222,020 454,657 421,709`
  - p19: `Long-term debt. As of June 30, 2025, Crook County’s outstanding bonded debt was $51,563,310. Other`
  - p22: `Current portion of bonds payable (net of premium) 627,129 163,095 790,224`

**interest_expense**:
  - p17: `Interest on long-term debt 213,541 199,689 241,116 222,020 454,657 421,709`
  - p23: `Interest on long-term debt 213,541 - - - (213,541) - (213,541)`
  - p23: `Interest expense 241,116 - - - - (241,116) (241,116)`

### Mecklenburg County (VA)

**property_tax**:
  - p12: `General property taxes, real and personal 1 10,700,962 98,798,924`
  - p13: `$140,962,523. Property taxes comprise the largest source of these revenues, totaling`
  - p14: `general property taxes and other local taxes, while actual expenditures were $1,792,912, or 1.6%`

**total_revenue**:
  - p12: `Total Revenues 1 40,962,523 135,367,818`
  - p19: `Total General Revenues 125,059,332 46,842,745 57,943,601`
  - p22: `Total Revenues 132,256,708 98,750 4 49,381 3 ,082,677 33,211,208 2 ,494,461 2 ,069,101 1 ,679,192 175,341,478`

**capital_outlay**:
  - p3: `Microsoft Capital Project, and School Capital Outlay 116-119`
  - p13: `The Capital Outlay Fund has a total fund balance of $30,913,176, all of which is assigned for`
  - p23: `Lease asset capital outlay expenditures which were capitalized 58,363`

**lt_debt**:
  - p12: `Interest on long-term debt 3 ,825,482 4,079,271`
  - p13: `Interest on long-term debt and fiscal charges 3 ,825,482 ( 3,825,482) 4 ,079,271 ( 4,079,271)`
  - p15: `Long-term debt, plus premiums $1 19,683,525 $ 20,552,289 $ 140,235,814`

**interest_expense**:
  - p12: `Interest on long-term debt 3 ,825,482 4,079,271`
  - p13: `Interest on long-term debt and fiscal charges 3 ,825,482 ( 3,825,482) 4 ,079,271 ( 4,079,271)`
  - p19: `Interest on long-term debt and bond issuance costs 3 ,825,482 - - - ( 3,825,482)`

### Grant County (WA)

**property_tax**:
  - p36: `Note 12 – Property Tax`
  - p39: `0119 001 CURRENT EXPENSE 3111000 Property Tax $21,351,177`
  - p44: `0119 101 COUNTY ROADS 3111000 Property Tax $10,615,632`

**total_revenue**:
  - p2: `Total Revenues: 177,010,677 60,540,633 23,747,507 228,988`
  - p3: `Total Revenues: 5,325 889 - 18,228,488`
  - p4: `Total Revenues: 480,816 28,669 118,964 1,602,766`

**capital_outlay**:
  - p2: `594-595 Capital Expenditures 16,617,825 1,204,038 6,049,038 -`
  - p3: `594-595 Capital Expenditures - 7,200 - 109,721`
  - p4: `594-595 Capital Expenditures 100,450 - - -`

**lt_debt**:
  - p28: `Note 8 – Long-Term Debt`
