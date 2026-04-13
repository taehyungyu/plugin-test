Recommend and implement statistical analysis for a cohort study.

User input: $ARGUMENTS

## Instructions

### 1. Study Classification
- **Prospective** vs **retrospective** cohort
- **Exposed vs unexposed** comparison, or **multi-level exposure**
- **Single cohort with internal comparison** or **external comparator**

### 2. Primary Effect Measures
- **Relative risk (RR)**: for common outcomes in prospective cohorts
- **Incidence rate ratio (IRR)**: when follow-up time varies
- **Hazard ratio (HR)**: for time-to-event outcomes
- **Risk difference (RD)**: for absolute effect

### 3. Confounding Control

**Regression-based**:
- Multivariable Cox regression, logistic regression, or Poisson regression
- Include known confounders (DAG-based selection preferred over p-value-based)

**Propensity Score methods** (preferred for observational causal inference):
- **PS Matching**: 1:1 or 1:k nearest-neighbor, caliper = 0.2×SD(logit PS)
- **IPTW (Inverse Probability of Treatment Weighting)**: stabilized weights, check extreme weights
- **PS Stratification**: quintiles of propensity score
- **AIPW (Augmented IPW)**: doubly robust estimator

**Balance diagnostics** (MANDATORY after PS):
- Standardized mean difference (SMD) < 0.1 for all covariates
- Love plot / balance table
- Variance ratio near 1.0

### 4. Time-to-Event Analysis
- **Kaplan-Meier** estimator with log-rank test
- **Cox proportional hazards**: check PH assumption (Schoenfeld, log-log)
- **Competing risks**: Fine-Gray subdistribution hazard or cause-specific hazard
- **Time-varying exposure**: extended Cox model or marginal structural model
- **Immortal time bias**: avoid by proper time-zero definition and time-varying analysis

### 5. Common Biases — Detection & Mitigation
| Bias | Mitigation |
|------|------------|
| Confounding | PS methods, multivariable adjustment, DAG |
| Selection bias | Sensitivity analysis, inverse probability of selection weighting |
| Immortal time bias | Landmark analysis, time-varying exposure |
| Prevalent user bias | New-user (incident user) design |
| Protopathic bias | Lag exposure window |
| Information bias | Validation substudy, sensitivity analysis |
| Loss to follow-up | IPW for censoring, sensitivity analysis |

### 6. Sensitivity Analysis
- **E-value**: quantify unmeasured confounding needed to explain away result
- **Negative control exposure/outcome**: detect residual confounding
- **Quantitative bias analysis**: probabilistic, Monte Carlo
- **Different PS methods**: compare matching, IPTW, stratification results

### 7. Code Template (R)
```r
library(MatchIt); library(survival); library(cobalt)

# Propensity score matching
m <- matchit(treatment ~ age + sex + comorbidity, data = df, method = "nearest", caliper = 0.2)
love.plot(m, threshold = 0.1)  # Balance check

matched_df <- match.data(m)
coxph(Surv(time, event) ~ treatment, data = matched_df, weights = weights, robust = TRUE)
```

## Output
- Analysis strategy with justification
- Confounder selection rationale (DAG recommended)
- PS method specification + balance check plan
- Sensitivity analysis for unmeasured confounding
- Executable code
