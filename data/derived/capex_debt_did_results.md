# Capex & Debt-Service Matched DiD (V2 all-funds)

**Date:** 2026-06-10. Same 101-treated / 1:3 division-matched sample as the property-tax DiD (script 46); outcomes = change in capex/debt INTENSITY from v2 all-funds (script 47). Intensities are unit-free (cancel v2's x1000 errors) and window-averaged (smooth capex lumpiness). Debt = flows only (v2 carries no long-term debt stock).

Positive capex / new-borrowing effect = DC counties invest & finance more; positive debt-service-burden effect = they carry more debt service (could be GOOD — funding the build-out — or a strain; read alongside capex).


## Capex intensity change (capital outlay / total expenditure)

**(1) Matched-pair effect**

### FULL (state + division)

- N treated (matched): **41**
- Matched effect mean **-1.951pp** (t p=0.2317); median -1.960pp
- Wilcoxon p=0.2411; sign 17/41 positive (p=0.3489)
- Bootstrap 95% CI [-5.075, +1.186]pp

### STATE-ONLY

- N treated (matched): **39**
- Matched effect mean **-1.761pp** (t p=0.2997); median -1.960pp
- Wilcoxon p=0.3290; sign 17/39 positive (p=0.5224)
- Bootstrap 95% CI [-4.932, +1.478]pp

### ESC-DROPPED

- N treated (matched): **38**
- Matched effect mean **-3.203pp** (t p=0.0425); median -2.556pp
- Wilcoxon p=0.0549; sign 14/38 positive (p=0.1433)
- Bootstrap 95% CI [-6.200, -0.267]pp

**(2) Pair-stacked OLS, clustered on county**

- FULL: treated coef **-3.020pp** (SE 1.489, p=0.0425), N=308, clusters=109
- STATE-ONLY: treated coef **-2.681pp** (SE 1.542, p=0.0822), N=274, clusters=107
- ESC-DROPPED: treated coef **-3.775pp** (SE 1.499, p=0.0118), N=267, clusters=100

**(3) Unique-county OLS, state FE, HC1**

- FULL: treated coef **-2.770pp** (SE 1.503, p=0.0653), N=109


## Debt-service burden change ((principal+interest) / total revenue)

**(1) Matched-pair effect**

### FULL (state + division)

- N treated (matched): **54**
- Matched effect mean **+0.178pp** (t p=0.8363); median +0.114pp
- Wilcoxon p=0.5486; sign 29/54 positive (p=0.6835)
- Bootstrap 95% CI [-1.533, +1.773]pp

### STATE-ONLY

- N treated (matched): **52**
- Matched effect mean **-0.109pp** (t p=0.9004); median +0.078pp
- Wilcoxon p=0.9960; sign 27/52 positive (p=0.8899)
- Bootstrap 95% CI [-1.816, +1.546]pp

### ESC-DROPPED

- N treated (matched): **49**
- Matched effect mean **-0.653pp** (t p=0.4321); median +0.047pp
- Wilcoxon p=0.7974; sign 25/49 positive (p=1.0000)
- Bootstrap 95% CI [-2.372, +0.840]pp

**(2) Pair-stacked OLS, clustered on county**

- FULL: treated coef **+0.187pp** (SE 0.903, p=0.8358), N=384, clusters=142
- STATE-ONLY: treated coef **-0.126pp** (SE 0.869, p=0.8844), N=344, clusters=140
- ESC-DROPPED: treated coef **-0.583pp** (SE 0.945, p=0.5371), N=336, clusters=130

**(3) Unique-county OLS, state FE, HC1**

- FULL: treated coef **-0.129pp** (SE 0.897, p=0.8860), N=142


## New-borrowing intensity change (proceeds from capital debt / total exp)

**(1) Matched-pair effect**

### FULL (state + division)

- N treated (matched): **11**
- Matched effect mean **+0.821pp** (t p=0.8041); median +2.706pp
- Wilcoxon p=0.5771; sign 6/11 positive (p=1.0000)
- Bootstrap 95% CI [-5.671, +6.311]pp

### STATE-ONLY

- N treated (matched): **10**
- Matched effect mean **+1.628pp** (t p=0.6485); median +3.385pp
- Wilcoxon p=0.3750; sign 6/10 positive (p=0.7539)
- Bootstrap 95% CI [-5.303, +7.335]pp

### ESC-DROPPED

- N treated (matched): **10**
- Matched effect mean **-0.439pp** (t p=0.8965); median +1.279pp
- Wilcoxon p=0.8457; sign 5/10 positive (p=1.0000)
- Bootstrap 95% CI [-7.129, +4.920]pp

**(2) Pair-stacked OLS, clustered on county**

- FULL: treated coef **+2.385pp** (SE 2.818, p=0.3973), N=139, clusters=50
- STATE-ONLY: treated coef **+2.298pp** (SE 3.157, p=0.4668), N=119, clusters=49
- ESC-DROPPED: treated coef **+1.624pp** (SE 2.932, p=0.5797), N=124, clusters=46

**(3) Unique-county OLS, state FE, HC1**

- FULL: treated coef **+3.124pp** (SE 3.566, p=0.3810), N=50


## Capex level CAGR (secondary, lumpy)

**(1) Matched-pair effect**

### FULL (state + division)

- N treated (matched): **37**
- Matched effect mean **-3.773pp** (t p=0.2343); median -4.478pp
- Wilcoxon p=0.1037; sign 13/37 positive (p=0.0989)
- Bootstrap 95% CI [-9.647, +2.369]pp

### STATE-ONLY

- N treated (matched): **34**
- Matched effect mean **-3.431pp** (t p=0.3184); median -2.701pp
- Wilcoxon p=0.2025; sign 13/34 positive (p=0.2295)
- Bootstrap 95% CI [-9.950, +3.054]pp

### ESC-DROPPED

- N treated (matched): **36**
- Matched effect mean **-3.994pp** (t p=0.2201); median -4.990pp
- Wilcoxon p=0.0915; sign 12/36 positive (p=0.0652)
- Bootstrap 95% CI [-10.164, +2.293]pp

**(2) Pair-stacked OLS, clustered on county**

- FULL: treated coef **-4.312pp** (SE 2.977, p=0.1475), N=275, clusters=98
- STATE-ONLY: treated coef **-4.068pp** (SE 3.125, p=0.1929), N=249, clusters=96
- ESC-DROPPED: treated coef **-4.570pp** (SE 3.098, p=0.1402), N=240, clusters=91

**(3) Unique-county OLS, state FE, HC1**

- FULL: treated coef **-4.157pp** (SE 3.430, p=0.2256), N=98

## Reading guide
- Capex/debt intensities are shares, so effects are in **percentage points of the share** (e.g. +1.0pp capex_share = capital outlay rises by 1% of total expenditure relative to controls).
- The matched-pair effect (1) is the headline; the county-clustered OLS (2) is the preferred inferential spec (controls reused up to ~8x). STATE-ONLY and ESC-DROPPED are the same two robustness probes as the property-tax DiD.
- Coverage is far better than property tax (capex ~1,041, debt-service ~1,431 counties nationally) because these are clean GASB expenditure lines, not bundled tax lines.
