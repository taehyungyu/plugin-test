---
name: stat-propensity
description: Implement propensity score methods and causal inference analysis for observational studies.
---

User input: {{input}}

## Instructions

### 1. Causal Question Framing
- Define **treatment/exposure** (A), **outcome** (Y), **confounders** (L)
- Draw a DAG (Directed Acyclic Graph) to identify confounders vs mediators vs colliders
- Specify **target estimand**: ATE (average treatment effect), ATT (on the treated), or ATO (overlap)
- Check **positivity**: P(A=1|L) must be bounded away from 0 and 1

### 2. Propensity Score Estimation

**Input format**:
```
DataFrame with columns:
  - treatment: binary (0/1)
  - outcome: continuous, binary, or time-to-event
  - covariates: all pre-treatment confounders (NO post-treatment variables)
```

**PS model**:
- Default: logistic regression
- Complex confounding: GBM (gradient boosted model) or random forest
- Include: main effects, clinically meaningful interactions, nonlinear terms (splines for continuous)
- DO NOT include: instruments (affect treatment but not outcome directly)

### 3. Method Selection

| Method | Estimand | When to Use | Key Assumption |
|--------|----------|-------------|----------------|
| **PSM (Matching)** | ATT | Clear treated group of interest | Common support |
| **IPTW** | ATE | Full population effect | Correct PS model |
| **AIPW (Doubly Robust)** | ATE | Best practice — robust to one model misspecification | Either PS or outcome model correct |
| **Overlap Weighting** | ATO | Extreme weights problem | Smooth weight function |
| **PS Stratification** | ATE | Simple, transparent | Sufficient strata |

### 4. PSM (Propensity Score Matching)

**Parameters**:
- `method`: nearest-neighbor (default), optimal, full, genetic
- `caliper`: 0.2 x SD(logit(PS)) — standard recommendation
- `ratio`: 1:1 (default), 1:k for more power (k <= 4)
- `replace`: with/without replacement
- `distance`: logit PS (default), Mahalanobis

**Output**: Matched dataset with weights

### 5. IPTW (Inverse Probability of Treatment Weighting)

**Weight calculation**:
- ATE: w = A/PS + (1-A)/(1-PS)
- ATT: w = 1 (treated), PS/(1-PS) (control)
- **Stabilized weights**: multiply by P(A) or P(1-A) — reduces variance
- **Truncation**: cap at 1st/99th percentile if extreme weights exist

**Output**: Original dataset with stabilized IPTW weights

### 6. AIPW (Augmented IPW / Doubly Robust)

- Combines PS weighting with outcome regression
- Consistent if EITHER the PS model OR the outcome model is correct
- Preferred method when feasible
- Use `sklearn` or `econml` for implementation

### 7. Balance Diagnostics (MANDATORY)

**Before/After comparison**:
- **SMD (Standardized Mean Difference)**: |SMD| < 0.1 for all covariates
- **Variance ratio**: between 0.5 and 2.0
- **Love plot**: visualize SMD before/after

**Output table format**:
```
| Covariate | Before SMD | After SMD | Variance Ratio |
|-----------|-----------|-----------|----------------|
| Age       | 0.35      | 0.02      | 1.05           |
| Sex       | 0.22      | 0.01      | 0.98           |
```

### 8. Outcome Analysis After PS

- **Continuous outcome**: weighted linear regression or matched t-test
- **Binary outcome**: weighted logistic regression, risk difference
- **Time-to-event**: weighted Cox regression (robust SE) or weighted KM
- **Always use robust/sandwich standard errors** with IPTW

### 9. Sensitivity Analysis

**E-value**:
- Minimum strength of unmeasured confounding to explain away the result
- E-value = RR + sqrt(RR x (RR - 1)) for point estimate
- Report for both point estimate and CI bound

**Rosenbaum bounds** (for matching):
- Gamma (sensitivity parameter): how much hidden bias could alter conclusion

**Negative controls**:
- Test PS method on outcome known to be unrelated to treatment

### 10. Template Python Code

```python
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# INPUT SPECIFICATION
# ============================================================
# df: pd.DataFrame with columns:
#   - 'treatment' (int): 0 or 1
#   - 'outcome' (float): continuous outcome (or 'time'+'event' for survival)
#   - covariate columns: all pre-treatment confounders
#
# covariates: list of str, e.g. ['age', 'sex', 'bmi', 'nyha_class']
# ============================================================

def estimate_propensity_score(df, treatment_col, covariates, method='logistic'):
    """Estimate propensity scores.

    Input:
        df: DataFrame
        treatment_col: str, name of binary treatment column
        covariates: list[str], confounder column names
        method: 'logistic' | 'gbm'
    Output:
        df with added 'ps' column (propensity score)
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler

    X = df[covariates].copy()
    # Handle categorical variables
    X = pd.get_dummies(X, drop_first=True)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    y = df[treatment_col].values

    if method == 'logistic':
        model = LogisticRegression(max_iter=1000, random_state=42)
    elif method == 'gbm':
        model = GradientBoostingClassifier(
            n_estimators=200, max_depth=3, learning_rate=0.1, random_state=42
        )
    model.fit(X_scaled, y)
    df = df.copy()
    df['ps'] = model.predict_proba(X_scaled)[:, 1]
    return df, model


def check_positivity(df, treatment_col='treatment', ps_col='ps'):
    """Check positivity assumption — PS overlap between groups.

    Output: overlap statistics + histogram plot
    """
    treated = df[df[treatment_col] == 1][ps_col]
    control = df[df[treatment_col] == 0][ps_col]

    print("=== Positivity Check ===")
    print(f"Treated PS range:  [{treated.min():.4f}, {treated.max():.4f}]")
    print(f"Control PS range:  [{control.min():.4f}, {control.max():.4f}]")
    print(f"Common support:    [{max(treated.min(), control.min()):.4f}, "
          f"{min(treated.max(), control.max()):.4f}]")

    fig, ax = plt.subplots(1, 1, figsize=(8, 4))
    ax.hist(treated, bins=50, alpha=0.5, label='Treated', density=True)
    ax.hist(control, bins=50, alpha=0.5, label='Control', density=True)
    ax.set_xlabel('Propensity Score')
    ax.set_ylabel('Density')
    ax.set_title('Propensity Score Distribution')
    ax.legend()
    plt.tight_layout()
    return fig


def perform_psm(df, treatment_col, covariates, caliper=None, ratio=1):
    """Propensity Score Matching (nearest-neighbor, without replacement).

    Input:
        caliper: float or None. If None, uses 0.2 * SD(logit(PS))
        ratio: int, 1:ratio matching
    Output:
        matched_df: DataFrame with matched pairs
        match_ids: dict mapping treated index -> list of control indices
    """
    df = df.copy()
    ps = df['ps'].values
    logit_ps = np.log(ps / (1 - ps + 1e-10))

    if caliper is None:
        caliper = 0.2 * np.std(logit_ps)
    print(f"Caliper: {caliper:.4f} (0.2 x SD(logit(PS)))")

    treated_idx = df[df[treatment_col] == 1].index.tolist()
    control_idx = df[df[treatment_col] == 0].index.tolist()

    match_ids = {}
    used_controls = set()
    np.random.shuffle(treated_idx)

    for t_idx in treated_idx:
        t_logit = logit_ps[df.index.get_loc(t_idx)]
        best_matches = []
        for c_idx in control_idx:
            if c_idx in used_controls:
                continue
            c_logit = logit_ps[df.index.get_loc(c_idx)]
            dist = abs(t_logit - c_logit)
            if dist <= caliper:
                best_matches.append((c_idx, dist))
        best_matches.sort(key=lambda x: x[1])
        selected = [m[0] for m in best_matches[:ratio]]
        if len(selected) == ratio:
            match_ids[t_idx] = selected
            used_controls.update(selected)

    matched_treated = list(match_ids.keys())
    matched_control = [c for cs in match_ids.values() for c in cs]
    matched_df = df.loc[matched_treated + matched_control].copy()

    print(f"Matched: {len(matched_treated)} treated, {len(matched_control)} controls")
    print(f"Unmatched treated dropped: {len(treated_idx) - len(matched_treated)}")
    return matched_df, match_ids


def compute_iptw(df, treatment_col='treatment', ps_col='ps',
                 estimand='ATE', stabilized=True, truncate=(0.01, 0.99)):
    """Compute IPTW weights.

    Input:
        estimand: 'ATE' | 'ATT'
        stabilized: bool, use stabilized weights
        truncate: tuple (lower, upper) percentile for weight truncation
    Output:
        df with 'iptw' column
    """
    df = df.copy()
    ps = df[ps_col].values
    a = df[treatment_col].values

    if estimand == 'ATE':
        w = a / ps + (1 - a) / (1 - ps)
        if stabilized:
            p_treat = a.mean()
            w = a * p_treat / ps + (1 - a) * (1 - p_treat) / (1 - ps)
    elif estimand == 'ATT':
        w = a + (1 - a) * ps / (1 - ps)
        if stabilized:
            p_treat = a.mean()
            w = a + (1 - a) * ps / (1 - ps) * (1 - p_treat) / p_treat

    # Truncation
    if truncate:
        lo, hi = np.percentile(w, [truncate[0]*100, truncate[1]*100])
        w = np.clip(w, lo, hi)

    df['iptw'] = w
    print(f"=== IPTW Weights ({estimand}, stabilized={stabilized}) ===")
    print(f"  Mean: {w.mean():.3f}, Median: {np.median(w):.3f}")
    print(f"  Range: [{w.min():.3f}, {w.max():.3f}]")
    print(f"  ESS treated: {(df.loc[a==1,'iptw'].sum())**2 / (df.loc[a==1,'iptw']**2).sum():.0f}")
    print(f"  ESS control: {(df.loc[a==0,'iptw'].sum())**2 / (df.loc[a==0,'iptw']**2).sum():.0f}")
    return df


def balance_diagnostics(df, treatment_col, covariates, weight_col=None):
    """Compute SMD and variance ratios before/after weighting or matching.

    Output:
        balance_table: DataFrame with SMD and variance ratio
        love_plot: matplotlib Figure
    """
    results = []
    for cov in covariates:
        t = df[df[treatment_col] == 1]
        c = df[df[treatment_col] == 0]

        if weight_col:
            tw, cw = t[weight_col].values, c[weight_col].values
        else:
            tw, cw = np.ones(len(t)), np.ones(len(c))

        t_mean = np.average(t[cov], weights=tw)
        c_mean = np.average(c[cov], weights=cw)
        t_var = np.average((t[cov] - t_mean)**2, weights=tw)
        c_var = np.average((c[cov] - c_mean)**2, weights=cw)
        pooled_sd = np.sqrt((t_var + c_var) / 2)

        smd = (t_mean - c_mean) / pooled_sd if pooled_sd > 0 else 0
        vr = t_var / c_var if c_var > 0 else np.nan

        results.append({
            'covariate': cov,
            'smd': round(smd, 4),
            'abs_smd': round(abs(smd), 4),
            'variance_ratio': round(vr, 4),
            'treated_mean': round(t_mean, 4),
            'control_mean': round(c_mean, 4),
        })

    balance_df = pd.DataFrame(results)

    # Love plot
    fig, ax = plt.subplots(figsize=(6, max(4, len(covariates) * 0.4)))
    ax.scatter(balance_df['abs_smd'], range(len(covariates)), color='steelblue', zorder=3)
    ax.set_yticks(range(len(covariates)))
    ax.set_yticklabels(balance_df['covariate'])
    ax.axvline(x=0.1, color='red', linestyle='--', label='SMD = 0.1 threshold')
    ax.set_xlabel('|Standardized Mean Difference|')
    ax.set_title('Love Plot — Covariate Balance')
    ax.legend()
    plt.tight_layout()

    all_balanced = (balance_df['abs_smd'] < 0.1).all()
    print(f"All covariates balanced (|SMD| < 0.1): {all_balanced}")
    return balance_df, fig


def outcome_analysis_weighted(df, treatment_col, outcome_col, weight_col='iptw',
                              outcome_type='continuous'):
    """Weighted outcome analysis with robust standard errors.

    Input:
        outcome_type: 'continuous' | 'binary' | 'survival'
        For survival: outcome_col should be 'time' and df must have 'event' column
    Output:
        dict with effect_estimate, ci_lower, ci_upper, p_value
    """
    import statsmodels.api as sm

    if outcome_type == 'continuous':
        X = sm.add_constant(df[treatment_col])
        model = sm.WLS(df[outcome_col], X, weights=df[weight_col]).fit(
            cov_type='HC1'  # robust sandwich SE
        )
        effect = model.params[treatment_col]
        ci = model.conf_int().loc[treatment_col]
        p = model.pvalues[treatment_col]
        print(f"=== Weighted Treatment Effect (Continuous) ===")
        print(f"  Mean difference: {effect:.4f} (95% CI: {ci[0]:.4f} to {ci[1]:.4f})")
        print(f"  P-value: {p:.4f}")
        return {'effect': effect, 'ci_lower': ci[0], 'ci_upper': ci[1], 'p_value': p}

    elif outcome_type == 'binary':
        X = sm.add_constant(df[treatment_col])
        model = sm.GLM(df[outcome_col], X, family=sm.families.Binomial(),
                       freq_weights=df[weight_col]).fit(cov_type='HC1')
        log_or = model.params[treatment_col]
        or_val = np.exp(log_or)
        ci = np.exp(model.conf_int().loc[treatment_col])
        p = model.pvalues[treatment_col]
        print(f"=== Weighted Treatment Effect (Binary) ===")
        print(f"  OR: {or_val:.4f} (95% CI: {ci[0]:.4f} to {ci[1]:.4f})")
        print(f"  P-value: {p:.4f}")
        return {'OR': or_val, 'ci_lower': ci[0], 'ci_upper': ci[1], 'p_value': p}

    elif outcome_type == 'survival':
        from lifelines import CoxPHFitter
        surv_df = df[[treatment_col, 'time', 'event', weight_col]].copy()
        cph = CoxPHFitter()
        cph.fit(surv_df, duration_col='time', event_col='event',
                weights_col=weight_col, robust=True)
        hr = np.exp(cph.params_[treatment_col])
        ci = np.exp(cph.confidence_intervals_)
        p = cph.summary['p'][treatment_col]
        print(f"=== Weighted Cox Regression ===")
        print(cph.summary)
        return {'HR': hr, 'p_value': p}


def compute_e_value(effect, ci_lower=None, effect_type='RR'):
    """Compute E-value for sensitivity to unmeasured confounding.

    Input:
        effect: point estimate (RR, OR, or HR)
        ci_lower: lower bound of CI (optional)
        effect_type: 'RR' | 'OR' | 'HR'
    Output:
        dict with e_value_point, e_value_ci
    """
    if effect_type == 'OR':
        # Convert OR to RR approximation (for common outcomes use sqrt)
        rr = effect  # conservative: use OR directly
    else:
        rr = effect

    if rr < 1:
        rr = 1 / rr

    e_point = rr + np.sqrt(rr * (rr - 1))

    e_ci = None
    if ci_lower is not None:
        ci_rr = ci_lower if ci_lower >= 1 else 1 / ci_lower
        if ci_rr > 1:
            e_ci = ci_rr + np.sqrt(ci_rr * (ci_rr - 1))
        else:
            e_ci = 1.0

    print(f"=== E-value ===")
    print(f"  Point estimate: {e_point:.2f}")
    print(f"  (Unmeasured confounder must have RR >= {e_point:.2f} with both")
    print(f"   treatment and outcome to explain away the observed effect)")
    if e_ci:
        print(f"  CI bound: {e_ci:.2f}")
    return {'e_value_point': e_point, 'e_value_ci': e_ci}


# ============================================================
# FULL PIPELINE EXAMPLE
# ============================================================
def run_propensity_pipeline(df, treatment_col, outcome_col, covariates,
                            method='iptw', outcome_type='continuous'):
    """End-to-end propensity score analysis pipeline.

    Input:
        df: DataFrame
        treatment_col: str
        outcome_col: str
        covariates: list[str]
        method: 'psm' | 'iptw' | 'aipw'
        outcome_type: 'continuous' | 'binary' | 'survival'

    Output:
        results: dict with all analysis results
        figures: list of matplotlib figures
    """
    figures = []
    results = {}

    # Step 1: Estimate PS
    print("=" * 60)
    print("STEP 1: Propensity Score Estimation")
    print("=" * 60)
    df, ps_model = estimate_propensity_score(df, treatment_col, covariates)

    # Step 2: Check positivity
    fig_ps = check_positivity(df, treatment_col)
    figures.append(('ps_overlap', fig_ps))

    # Step 3: Unadjusted balance
    print("\n" + "=" * 60)
    print("STEP 2: Unadjusted Balance")
    print("=" * 60)
    bal_before, fig_before = balance_diagnostics(df, treatment_col, covariates)
    results['balance_before'] = bal_before

    # Step 4: Apply method
    print("\n" + "=" * 60)
    print(f"STEP 3: Apply {method.upper()}")
    print("=" * 60)
    if method == 'psm':
        df_analysis, match_ids = perform_psm(df, treatment_col, covariates)
        weight_col = None
    elif method == 'iptw':
        df_analysis = compute_iptw(df, treatment_col)
        weight_col = 'iptw'
    else:
        df_analysis = compute_iptw(df, treatment_col)
        weight_col = 'iptw'

    # Step 5: Post-adjustment balance
    print("\n" + "=" * 60)
    print("STEP 4: Post-Adjustment Balance")
    print("=" * 60)
    bal_after, fig_after = balance_diagnostics(
        df_analysis, treatment_col, covariates, weight_col=weight_col
    )
    results['balance_after'] = bal_after
    figures.append(('love_plot', fig_after))

    # Step 6: Outcome analysis
    print("\n" + "=" * 60)
    print("STEP 5: Outcome Analysis")
    print("=" * 60)
    if weight_col:
        effect = outcome_analysis_weighted(
            df_analysis, treatment_col, outcome_col, weight_col, outcome_type
        )
    else:
        effect = outcome_analysis_weighted(
            df_analysis, treatment_col, outcome_col,
            weight_col='__unit', outcome_type=outcome_type
        )
    results['effect'] = effect

    # Step 7: E-value
    print("\n" + "=" * 60)
    print("STEP 6: Sensitivity — E-value")
    print("=" * 60)
    if outcome_type == 'binary':
        ev = compute_e_value(effect['OR'], effect['ci_lower'], 'OR')
    elif outcome_type == 'survival':
        ev = compute_e_value(effect['HR'], effect_type='HR')
    else:
        # For continuous, convert to approximate RR (not always applicable)
        ev = None
        print("  E-value: compute manually for continuous outcomes")
    results['e_value'] = ev

    return results, figures
```

## Output
- Propensity score distribution plot with overlap assessment
- Balance table (SMD, variance ratio) before/after adjustment
- Love plot visualization
- Treatment effect estimate with robust CI
- E-value for sensitivity to unmeasured confounding
- Complete executable Python pipeline
- Clinical interpretation of causal effect
