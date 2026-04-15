---
name: meta-analysis
description: Guide or perform a meta-analysis with appropriate statistical methods.
---

User input: {{input}}

## Instructions

### 1. Data Preparation
- **Effect measure selection**:
  - Binary: OR, RR, RD (prefer OR for case-control, RR for cohort/RCT)
  - Continuous: mean difference (MD), standardized MD (SMD/Hedges' g)
  - Time-to-event: HR (log-transformed)
  - Diagnostic: sensitivity, specificity, DOR, paired (bivariate model)
- **Extract per study**: effect estimate, SE/CI, sample size, events

### 2. Model Selection
- **Fixed-effect** (Mantel-Haenszel or inverse-variance): when studies are clinically homogeneous
- **Random-effects** (DerSimonian-Laird, REML, Paule-Mandel): when heterogeneity expected
- **Default recommendation**: random-effects with REML estimator for tau²
- Justify choice in the analysis plan

### 3. Heterogeneity Assessment
- **Q-test** (Cochran's): p < 0.10 suggests heterogeneity
- **I²**: 0-40% low, 30-60% moderate, 50-90% substantial, 75-100% considerable
- **tau²**: absolute heterogeneity measure
- **Prediction interval**: range of true effects across settings
- If I² > 50%, explore sources via subgroup analysis or meta-regression

### 4. Publication Bias
- **Funnel plot**: visual assessment (≥10 studies recommended)
- **Egger's test**: regression-based (continuous outcomes)
- **Peters' test**: preferred for binary outcomes
- **Trim-and-fill**: sensitivity analysis for missing studies
- **P-curve / selection models**: newer methods for robustness

### 5. Subgroup & Sensitivity Analysis
- **Pre-specified subgroups**: by population, intervention, study quality, region
- **Meta-regression**: for continuous moderators
- **Leave-one-out**: influence of individual studies
- **Sensitivity to**: model choice (FE vs RE), effect measure, quality exclusion

### 6. Advanced Methods (if applicable)
- **Network meta-analysis** (NMA): for multiple treatment comparisons
- **IPD meta-analysis**: if individual patient data available
- **Bivariate model**: for diagnostic test accuracy meta-analysis
- **Dose-response meta-analysis**: for exposure-response relationships
- **Cumulative meta-analysis**: temporal trend of evidence

### 7. Code Generation
Generate analysis code in R (meta/metafor) or Python (as requested):

```r
# Template: Random-effects meta-analysis
library(meta); library(metafor)
ma <- metagen(TE, seTE, studlab = study, data = df, sm = "OR", method.tau = "REML")
forest(ma, sortvar = TE, prediction = TRUE)
funnel(ma, studlab = TRUE)
metabias(ma, method.rank = "linreg")
metainf(ma)  # leave-one-out influence
```

### 8. Reporting
- Forest plot with prediction interval
- Heterogeneity statistics (I², tau², Q-test p-value)
- Publication bias assessment results
- GRADE certainty rating
- Follow PRISMA 2020 reporting items for synthesis

## Output
- Complete statistical analysis code
- Interpretation guide for results
- Checklist of assumptions verified
