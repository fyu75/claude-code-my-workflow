# Project Knowledge Base: Data Centers and Municipality Finances

Last updated: 2026-05-10. Living document — append as conventions stabilize.

## Mechanism Map

```
Data center investment in county c at time t
   │
   ▼
Property tax base ↑   +   Personal-property tax base ↑   (DC servers, cooling, generators)
   │
   ▼
Muni revenue per capita ↑     ←── INV-4: US-firm sample only
   │
   ├──→ Muni capex ↑          (new infrastructure, schools, hospitals)
   ├──→ Muni debt ↓ / paydown (de-leveraging)
   ├──→ Public services ↑
   ├──→ Bond ratings ↑        (Moody's / S&P / Fitch reassessment)
   └──→ Bond yields/spreads ↓ (lower borrowing cost on outstanding + new issues)
```

The paper estimates each of these channels. **Do not narrow to bond-yields-only without team approval.**

## Identification Map

| Strategy | Reference | Notes |
|---|---|---|
| Winner-vs-loser counties | `greenstone2010_milliondollar` | Classic template; needs runner-up county data |
| Corporate-subsidy yields-spread design | `chava_subsidies` | Closest existing precedent (15.2 bps effect) |
| Staggered DiD with heterogeneity-robust estimators | Callaway--Sant'Anna; de Chaisemartin--D'Haultfœuille | For panel of DC openings 2010–2025 |
| Construction-company press releases (Ravenpack) | — | Alternative shock-timing source |

**Key threats:**
1. Munis seek out DCs (selection on tax base).
2. DC siting correlates with unrelated tech / energy infrastructure shocks.
3. Tax-incentive deals are themselves outcomes — pre-incentive ATTs are not the right object.

## Notation Registry

| Symbol | Meaning | First defined |
|---|---|---|
| $c$ | County | Section 2 (Data) |
| $t$ | Year | Section 2 |
| $i$ | Bond / issuer | Section 4 (Empirical) |
| $\text{DC}_{c,t}$ | Indicator: county $c$ has $\geq 1$ operational DC by $t$ | Section 4 |
| $\text{MW}_{c,t}$ | Total operational MW capacity in county $c$ at $t$ | Section 4 |
| $\tau_{c,t}$ | DC-related personal-property tax revenue, county $c$, year $t$ | Section 5 |
| $r_{c,t}$ | Bond rating (numeric, AAA = 1, ... ) | Section 5 |
| $y_{i,t}$ | Bond $i$ yield-to-maturity at $t$ | Section 5 |
| $s_{i,t}$ | Yield spread over Treasury at $t$ | Section 5 |
| $\Delta y_i$ | Change in $y_i$ around DC announcement | Section 5 |

## S&P 451 Research Variable Reference

| Concept | File | Key fields (TODO: confirm after `01_import.do` runs) |
|---|---|---|
| Property characteristics | `dcproperties_latest.sas7bdat` | property_id, country, state, county, MW capacity, sqft |
| Property time series | `dcpropertiesperiodic_latest.sas7bdat` | property_id, period, status |
| Ownership | `dcownership_latest.sas7bdat` | property_id, owner_id, ownership_share |
| Provider | `dcprovider_latest.sas7bdat` | provider_id, provider_type |
| Provider type | `providertype_latest.sas7bdat` | type_code, type_name (colocation, hyperscale, ...) |
| Client / tenant | `dcclient_latest.sas7bdat` | tenant_id, property_id |
| Tenancy type | `dctenancytype_latest.sas7bdat` | type_code, type_name (wholesale, retail, ...) |
| Market | `dcmarket_latest.sas7bdat` | market_id, metro |
| Operational status | `operationalstatus_latest.sas7bdat` | status_code (active / planned / under construction) |
| NCREIF region | `ncreifregion_latest.sas7bdat` | region_code, region_name |
| Company identifiers | `ciqcompany.sas7bdat` | ciq_id → S&P Capital IQ identifier (cross-reference) |

(Confirm field names after first `import sas` run; update this table.)

## Geographic Anchors

| Anchor | Description | Role in paper |
|---|---|---|
| **Prince William County, VA** | Stylized fact: DC personal-property tax $2.9M (FY13) → $54.4M (FY22), 38.4% CAGR | Lead anecdote / motivation |
| **Loudoun County, VA** | Wealthy DC hub ("Data Center Alley") | Outlier — NOT representative |
| **San Bernardino County, CA** | Poor county example | Case study / heterogeneity probe |
| **Rural counties (general)** | Where new DCs are migrating | Main sample of interest |

## Anti-Patterns (Don't Do This)

| Anti-Pattern | What Happens | Correction |
|---|---|---|
| Conflate colocation hosts with hyperscale tenants | Wrong unit of analysis (the property vs the company) | Join on `property_id`; use `tenancy_type` to distinguish |
| Treat Loudoun County, VA as representative | Wealthy outlier biases the cross-section | Restrict main sample by county-income quartile; report Loudoun separately |
| Use bond yields as the only outcome | Misses the muni capex / debt / public services / ratings channels | Run all five outcomes in parallel |
| Ignore property-tax revenue volatility from short DC asset cycles | Overstate the long-run fiscal benefit | Include asset-replacement cycle (chip refresh) as a covariate / sensitivity |
| Apply US-firm filter inside an analysis script | Sample becomes invisible in lineage; INV-4 violation | Apply in `02_clean.do`; document the cell counts |
| Hand-edit a regression table in `.tex` | INV-1 violation; numbers drift from code | Change `esttab` call upstream |

## Stata Pitfalls (project-specific)

| Bug | Impact | Fix |
|---|---|---|
| `xtset` with reversed panel/time order | `xtreg` silently mis-specifies | Always `xtset county year`, never `xtset year county` |
| `xtreg, fe` cluster df ≠ `areg` cluster df | Different SEs, hard to detect | Pick one (`reghdfe` recommended); document |
| `merge 1:1` after non-unique master | Silent expansion of N | `isid <key>` before every merge |
| `encode` before standardizing case | Permanent string→numeric mapping with case-sensitive duplicates | `replace x = upper(trim(x))` first |

## Data Status

| Source | Status | Purpose |
|---|---|---|
| S&P 451 Research DC Database | ✅ Have (23 SAS files at `data/raw`) | DC properties, ownership, providers, clients |
| ACFR (county financials) | ☐ TODO | Muni revenue / expenditure / debt by year |
| TRACE / MSRB EMMA | ☐ TODO (later) | Muni bond trade data |
| NCSL state DC incentives | ☐ TODO | Tax-incentive variation across states |
| Moody's 2026 DC credit-risk hub | ☐ TODO | Institutional ratings perspective |
| S&P Global Ratings 2026 DC piece | ☐ TODO | Institutional ratings perspective |
| Prince William County FY22 fiscal-impact PDF | ☐ TODO | Stylized fact |
| Construction press releases (Ravenpack) | ☐ Optional | Alternative shock timing |
