Recommend and implement statistical analysis for a Randomized Controlled Trial (RCT).

User input: $ARGUMENTS

## Instructions

### 1. Analysis Populations
- **ITT (Intention-to-Treat)**: all randomized subjects → PRIMARY analysis
- **mITT (Modified ITT)**: all randomized who received ≥1 dose and had ≥1 post-baseline assessment
- **Per-Protocol (PP)**: completed study without major protocol deviations → sensitivity analysis
- **Safety population**: all who received ≥1 dose of study treatment

### 2. Primary Analysis — by Endpoint Type

**Continuous endpoint**:
- ANCOVA with treatment group as factor, baseline value as covariate (preferred over change-from-baseline)
- Mixed-effects model for repeated measures (MMRM) for longitudinal data
- Assumption checks: normality of residuals, homogeneity of variance

**Binary endpoint**:
- Chi-square test or Fisher's exact (sparse data)
- Logistic regression adjusted for stratification factors
- Risk difference, relative risk, or odds ratio with 95% CI
- CMH test if stratified randomization

**Time-to-event endpoint**:
- Kaplan-Meier curves + log-rank test
- Cox proportional hazards regression
- Check PH assumption (Schoenfeld residuals, log-log plot)
- If PH violated: RMST, piecewise Cox, or accelerated failure time model

**Count / rate endpoint**:
- Poisson or negative binomial regression
- Account for overdispersion and exposure time

### 3. Multiplicity Adjustment
- **Multiple primary endpoints**: Bonferroni, Holm, or gatekeeping
- **Hierarchical testing**: pre-specified order, test at full α until first non-significant
- **Multiple dose groups vs. control**: Dunnett's test
- **Multiple timepoints**: no adjustment if single primary timepoint

### 4. Missing Data
- **Primary**: MMRM (MAR assumption, preferred by FDA/EMA)
- **Sensitivity**: pattern-mixture model, tipping point analysis, delta-adjustment
- **MNAR**: sensitivity under informative censoring (e.g., jump-to-reference, copy-reference)
- **Never**: LOCF (outdated, biased)

### 5. Subgroup Analysis
- Pre-specified in SAP: age, sex, disease severity, region, biomarker status
- Treatment-by-subgroup interaction test
- Forest plot of subgroup effects
- Label as exploratory unless powered

### 6. Interim Analysis (if applicable)
- Alpha spending function: O'Brien-Fleming (conservative early) or Lan-DeMets
- Futility stopping: conditional power or predictive probability
- DSMB charter requirements

### 7. Safety Analysis
- Adverse events: frequency table, system organ class, preferred term
- Serious adverse events, deaths, discontinuations due to AEs
- Laboratory: shift tables, clinically notable values
- Exposure-adjusted incidence rates

### 8. Code Generation
Generate reproducible analysis code in R or Python based on the specific trial design.

## Output
- Statistical analysis plan outline
- Primary analysis specification with code
- Missing data strategy
- Multiplicity adjustment approach
- Sensitivity analysis list
