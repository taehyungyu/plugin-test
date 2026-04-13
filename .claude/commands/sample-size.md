Calculate sample size for a clinical study.

User input: $ARGUMENTS

## Instructions

### 1. Identify Study Parameters
Ask for or infer from context:
- **Study design**: RCT, cohort, case-control, diagnostic, cross-sectional
- **Primary endpoint type**: continuous, binary, time-to-event, ordinal
- **Comparison type**: superiority, non-inferiority, equivalence
- **Alpha** (type I error): typically 0.05 (two-sided) or 0.025 (one-sided for NI)
- **Power** (1 - beta): typically 0.80 or 0.90
- **Allocation ratio**: 1:1, 2:1, etc.
- **Dropout/lost-to-follow-up rate**: adjustment factor

### 2. Effect Size & Variability
- **Continuous**: clinically meaningful difference (δ) and pooled SD (σ)
- **Binary**: expected proportions in each group (p1, p2)
- **Time-to-event**: hazard ratio (HR), median survival, accrual/follow-up time
- **Non-inferiority**: non-inferiority margin (δ_NI)
- **Diagnostic**: target sensitivity/specificity, CI width, disease prevalence

### 3. Formulas

**Two-sample means (superiority)**:
n per group = (Z_{α/2} + Z_β)² × 2σ² / δ²

**Two proportions (superiority)**:
n per group = (Z_{α/2} + Z_β)² × [p1(1-p1) + p2(1-p2)] / (p1 - p2)²

**Time-to-event (Schoenfeld)**:
Total events D = (Z_{α/2} + Z_β)² / [log(HR)]²
N = D / (probability of event)

**Non-inferiority (means)**:
n per group = (Z_α + Z_β)² × 2σ² / (δ - δ_NI)²
(one-sided α)

**Diagnostic accuracy**:
n = Z_{α/2}² × Se × (1-Se) / d²  (for sensitivity, d = margin of error)
Adjust for prevalence: n_total = n / prevalence

### 4. Generate Code

Provide calculation code in R and/or Python:

```r
# R: pwr package
library(pwr)
pwr.t.test(d = delta/sigma, sig.level = 0.05, power = 0.80, type = "two.sample")

# Survival: gsDesign
library(gsDesign)
nEvents(hr = 0.75, alpha = 0.025, beta = 0.10)

# Proportions
pwr.2p.test(h = ES.h(p1, p2), sig.level = 0.05, power = 0.80)
```

```python
# Python: statsmodels
from statsmodels.stats.power import TTestIndPower, NormalIndPower
analysis = TTestIndPower()
n = analysis.solve_power(effect_size=delta/sigma, alpha=0.05, power=0.80)
```

### 5. Sensitivity Table
Provide a table showing sample size across a range of assumptions:

| Effect Size | Power 80% | Power 90% |
|-------------|-----------|-----------|
| Small       | n = ?     | n = ?     |
| Medium      | n = ?     | n = ?     |
| Large       | n = ?     | n = ?     |

### 6. Final Recommendation
- State recommended N with all assumptions
- Include dropout adjustment: N_final = N / (1 - dropout_rate)
- Flag if assumptions seem unrealistic (search PubMed for reference values)

## Output
- Explicit assumptions list
- Formula used
- Calculated N (per group and total)
- Sensitivity analysis table
- Executable code (R and/or Python)
