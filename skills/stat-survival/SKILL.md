---
name: stat-survival
description: Recommend and implement survival analysis methods for time-to-event data.
---

User input: {{input}}

## Instructions

### 1. Data Structure Check
- **Time variable**: follow-up duration (ensure consistent units)
- **Event indicator**: 1 = event occurred, 0 = censored
- **Censoring type**: right (most common), left, interval
- **Censoring mechanism**: administrative, loss-to-follow-up, competing event
- **Check**: are censoring patterns similar across groups? (informative censoring?)

### 2. Non-parametric Methods

**Kaplan-Meier estimator**:
- Survival curves by group
- Median survival with 95% CI
- Landmark survival rates (e.g., 1-year, 3-year, 5-year)
- Report number at risk at key timepoints

**Log-rank test**:
- Compare survival curves between groups
- Weighted variants: Gehan-Breslow (early differences), Tarone-Ware, Peto-Prentice
- Stratified log-rank: control for confounders with few levels

### 3. Semi-parametric: Cox Proportional Hazards

**Model**: h(t) = h₀(t) × exp(β₁X₁ + β₂X₂ + ...)
- Report HR with 95% CI
- Stratified Cox: for variables violating PH (strata term)

**Assumption checks** (MANDATORY):
- **PH assumption**: Schoenfeld residuals test + plot (p > 0.05), log(-log(S(t))) plot
- **Linearity**: Martingale residuals vs continuous covariates
- **Influential observations**: dfbeta residuals
- **Overall fit**: Cox-Snell residuals

**If PH violated**:
- Time-varying coefficients: interaction with time or time intervals
- Piecewise Cox: different HRs for different time intervals
- Restricted mean survival time (RMST): non-parametric alternative
- Accelerated failure time (AFT) model: parametric alternative

### 4. Parametric Models
- **Exponential**: constant hazard (rarely appropriate)
- **Weibull**: monotone increasing/decreasing hazard
- **Log-normal**: non-monotone hazard
- **Log-logistic**: non-monotone, proportional odds model
- **Generalized gamma**: flexible, includes Weibull and log-normal as special cases
- Select based on AIC/BIC and clinical plausibility of hazard shape

### 5. Competing Risks
- **Problem**: standard KM overestimates CIF when competing events exist
- **Cumulative incidence function (CIF)**: proper estimate of event probability
- **Fine-Gray model**: subdistribution hazard → estimates effect on CIF (SHR)
- **Cause-specific hazard**: standard Cox per event type → mechanistic interpretation
- **Recommendation**: report both cause-specific and subdistribution analyses

### 6. Advanced Methods
- **Time-varying covariates**: extended Cox model, landmark analysis
- **Recurrent events**: Andersen-Gill, Prentice-Williams-Peterson, frailty models
- **Multi-state models**: illness-death, competing risks as states
- **Cure models**: mixture cure, promotion time model (when plateau in KM curve)
- **RMST**: τ-restricted mean, difference/ratio — no PH assumption needed
- **Landmark analysis**: condition on being event-free at landmark time

### 7. Code Template (R)
```r
library(survival); library(survminer); library(cmprsk); library(flexsurv)

# Kaplan-Meier
km <- survfit(Surv(time, status) ~ group, data = df)
ggsurvplot(km, risk.table = TRUE, pval = TRUE, conf.int = TRUE,
           surv.median.line = "hv", break.time.by = 12)

# Cox regression
cox <- coxph(Surv(time, status) ~ group + age + sex, data = df)
summary(cox)
cox.zph(cox)  # PH assumption test
ggcoxzph(cox.zph(cox))

# RMST
library(survRM2)
rmst2(df$time, df$status, df$group, tau = 60)

# Competing risks
library(tidycmprsk)
cuminc(Surv(time, factor(status)) ~ group, data = df) |> ggcuminc()

# Fine-Gray
crr(df$time, df$status, df[, covariates])
```

## Output
- KM curves with risk table
- Cox regression with HR, CI, PH check
- Competing risk analysis if applicable
- Executable code with assumption checks
