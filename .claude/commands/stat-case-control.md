Recommend and implement statistical analysis for a case-control study.

User input: $ARGUMENTS

## Instructions

### 1. Study Structure
- **Unmatched** case-control: cases vs independent controls
- **Matched** case-control: individual matching (1:1, 1:k) or frequency matching
- **Nested** case-control: sampled from a defined cohort (preserves time)

### 2. Primary Effect Measure
- **Odds Ratio (OR)**: the standard measure for case-control studies
- OR approximates RR when outcome is rare (<10%) — "rare disease assumption"
- Report OR with 95% CI

### 3. Analysis Methods

**Unmatched**:
- 2x2 table: OR = (a×d)/(b×c), Woolf's method for CI
- Chi-square test or Fisher's exact test
- Unconditional logistic regression for adjusted OR

**Matched (individual)**:
- Conditional logistic regression (McNemar's test for 1:1 matched pairs)
- Stratified analysis preserving matched sets
- DO NOT break matching in analysis — this introduces bias

**Frequency matched**:
- Unconditional logistic regression adjusting for matching variables
- Stratified analysis (Mantel-Haenszel) by matching factors

**Nested case-control**:
- Conditional logistic regression on risk sets
- Can estimate rate ratios (not just odds ratios)

### 4. Confounding & Effect Modification
- **Stratified analysis**: Mantel-Haenszel adjusted OR, Breslow-Day test for homogeneity
- **Multivariable logistic regression**: include confounders identified by DAG
- **Effect modification**: test interaction terms, report stratum-specific ORs if significant
- **Trend test**: Cochran-Armitage for ordinal exposure levels

### 5. Dose-Response Analysis
- Categorize exposure into ordered levels (tertiles, quartiles)
- Test for linear trend across categories
- Restricted cubic splines for flexible dose-response curve
- Report p-for-trend

### 6. Bias Assessment
| Bias | Issue | Mitigation |
|------|-------|------------|
| Selection bias | Control selection not representative | Population-based controls, multiple control groups |
| Recall bias | Cases recall exposure differently | Use objective records, blinded assessment |
| Berkson's bias | Hospital-based controls | Population-based controls |
| Reverse causation | Exposure measured after disease onset | Exclude recent diagnoses, lag analysis |

### 7. Sensitivity Analyses
- Vary case/control definitions
- Restrict to confirmed cases only
- Use different control groups if available
- E-value for unmeasured confounding

### 8. Code Template (R)
```r
# Unmatched
glm(case ~ exposure + age + sex, data = df, family = binomial) |> 
  exp(cbind(OR = coef(.), confint(.)))

# Matched (conditional logistic regression)
library(survival)
clogit(case ~ exposure + age + strata(matched_set), data = df)

# Mantel-Haenszel
mantelhaen.test(table(df$case, df$exposure, df$stratum))
```

## Output
- Matching strategy assessment
- Appropriate regression method
- Confounder adjustment plan
- Dose-response analysis if applicable
- Executable code
