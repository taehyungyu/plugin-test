---
name: stat-mediation
description: Implement mediation analysis, interaction testing, and subgroup analysis for clinical research.
---

User input: {{input}}

## Instructions

### 1. Analysis Type Identification

| Analysis | Question | Example |
|----------|----------|---------|
| **Mediation** | Does X affect Y *through* M? | Does OSA increase cardiac arrest *through* atrial fibrillation? |
| **Moderation (Interaction)** | Does the effect of X on Y *differ by* Z? | Does aficamten efficacy differ between men and women? |
| **Subgroup analysis** | Is the treatment effect consistent across subgroups? | Is benefit similar in mild vs severe HCM? |

### 2. Mediation Analysis Framework

**Causal mediation (counterfactual framework)**:
```
Treatment (A) → Mediator (M) → Outcome (Y)
         A ─────────────────→ Y  (direct effect)
```

- **Total Effect (TE)**: A → Y (unadjusted)
- **Natural Direct Effect (NDE)**: A → Y not through M
- **Natural Indirect Effect (NIE)**: A → M → Y (the mediated portion)
- **TE = NDE + NIE** (on additive scale)
- **% Mediated** = NIE / TE x 100

**Input format**:
```
DataFrame with columns:
  - treatment: exposure/treatment variable (binary or continuous)
  - mediator: intermediate variable
  - outcome: final outcome (continuous, binary, or time-to-event)
  - covariates: confounders of A→Y, A→M, and M→Y paths
```

**Key assumptions**:
1. No unmeasured A→Y confounding (given covariates)
2. No unmeasured A→M confounding (given covariates)
3. No unmeasured M→Y confounding (given A and covariates)
4. **No treatment-induced confounding of M→Y** (cross-world independence)

### 3. Mediation Methods

| Method | When | Outcome Type |
|--------|------|-------------|
| **Baron-Kenny (product method)** | Simple, continuous outcome | Continuous |
| **Causal mediation (ACME)** | Gold standard, counterfactual-based | Any |
| **Structural Equation Modeling** | Multiple mediators, complex paths | Continuous |
| **VanderWeele approach** | Exposure-mediator interaction allowed | Any |
| **Marginal structural model** | Time-varying mediation | Time-to-event |

### 4. Interaction / Effect Modification

**Types**:
- **Additive interaction**: difference in risk differences (RERI, AP, S)
- **Multiplicative interaction**: ratio of ratios (OR/RR interaction term)
- **Qualitative interaction**: effect reverses direction across subgroups (most concerning)

**Testing**:
- Add treatment x modifier interaction term to regression model
- Test: p_interaction < 0.05 (or 0.10 for exploratory)
- Report stratum-specific effects regardless of interaction test result

### 5. Subgroup Analysis (Forest Plot)

**Pre-specified subgroups** (for RCTs):
- Age (< median vs >= median)
- Sex (male vs female)
- Disease severity (mild vs moderate-severe)
- Baseline biomarker (above vs below threshold)
- Region/race/ethnicity

**Rules**:
- Pre-specify in SAP (Statistical Analysis Plan)
- Label exploratory unless study powered for subgroup
- Use interaction test, NOT separate subgroup p-values
- Forest plot with interaction p-values
- Limit number of subgroups (< 10 recommended)

### 6. Template Python Code

```python
import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# INPUT SPECIFICATION
# ============================================================
# For mediation:
#   df: DataFrame with 'treatment', 'mediator', 'outcome', covariates
# For interaction:
#   df: DataFrame with 'treatment', 'modifier', 'outcome'
# For subgroup:
#   df: DataFrame with 'treatment', 'outcome', subgroup variables
# ============================================================


# ==============================
# MEDIATION ANALYSIS
# ==============================

def baron_kenny_mediation(df, treatment_col, mediator_col, outcome_col,
                          covariates=None):
    """Baron-Kenny 4-step mediation analysis (continuous outcome).

    Input:
        treatment_col: exposure variable
        mediator_col: mediator variable
        outcome_col: outcome variable
        covariates: list of confounder names
    Output:
        dict with total_effect, direct_effect, indirect_effect, pct_mediated, sobel_p
    """
    cov_str = ' + '.join(covariates) if covariates else ''
    cov_plus = f' + {cov_str}' if cov_str else ''

    # Step 1: Total effect (A → Y)
    m1 = smf.ols(f'{outcome_col} ~ {treatment_col}{cov_plus}', data=df).fit()
    total_effect = m1.params[treatment_col]
    p_total = m1.pvalues[treatment_col]

    # Step 2: A → M
    m2 = smf.ols(f'{mediator_col} ~ {treatment_col}{cov_plus}', data=df).fit()
    a_path = m2.params[treatment_col]
    p_a = m2.pvalues[treatment_col]

    # Step 3: A + M → Y (direct effect)
    m3 = smf.ols(f'{outcome_col} ~ {treatment_col} + {mediator_col}{cov_plus}',
                 data=df).fit()
    direct_effect = m3.params[treatment_col]
    b_path = m3.params[mediator_col]
    p_direct = m3.pvalues[treatment_col]
    p_b = m3.pvalues[mediator_col]

    # Indirect effect = a * b
    indirect_effect = a_path * b_path
    pct_mediated = (indirect_effect / total_effect * 100) if total_effect != 0 else 0

    # Sobel test
    se_a = m2.bse[treatment_col]
    se_b = m3.bse[mediator_col]
    sobel_se = np.sqrt(a_path**2 * se_b**2 + b_path**2 * se_a**2)
    sobel_z = indirect_effect / sobel_se
    sobel_p = 2 * (1 - stats.norm.cdf(abs(sobel_z)))

    print("=== Baron-Kenny Mediation Analysis ===")
    print(f"Step 1 — Total Effect (c):    {total_effect:.4f} (P={p_total:.4f})")
    print(f"Step 2 — A→M path (a):        {a_path:.4f} (P={p_a:.4f})")
    print(f"Step 3 — M→Y path (b):        {b_path:.4f} (P={p_b:.4f})")
    print(f"Step 3 — Direct Effect (c'):   {direct_effect:.4f} (P={p_direct:.4f})")
    print(f"Indirect Effect (a*b):         {indirect_effect:.4f}")
    print(f"% Mediated:                    {pct_mediated:.1f}%")
    print(f"Sobel test:                    Z={sobel_z:.3f}, P={sobel_p:.4f}")

    return {
        'total_effect': total_effect,
        'direct_effect': direct_effect,
        'indirect_effect': indirect_effect,
        'pct_mediated': pct_mediated,
        'a_path': a_path,
        'b_path': b_path,
        'sobel_z': sobel_z,
        'sobel_p': sobel_p,
    }


def causal_mediation_analysis(df, treatment_col, mediator_col, outcome_col,
                               covariates=None, n_boot=1000,
                               outcome_type='continuous', mediator_type='continuous'):
    """Counterfactual-based causal mediation analysis (ACME/ACDE).
    Implements the Imai, Keele & Tingley (2010) approach.

    Input:
        outcome_type: 'continuous' | 'binary'
        mediator_type: 'continuous' | 'binary'
        n_boot: number of bootstrap samples for CI
    Output:
        dict with ACME (avg causal mediation effect), ADE (avg direct effect),
        total_effect, pct_mediated, bootstrap CIs
    """
    cov_str = ' + '.join(covariates) if covariates else ''
    cov_plus = f' + {cov_str}' if cov_str else ''

    def _estimate_once(data):
        # Mediator model
        if mediator_type == 'continuous':
            m_model = smf.ols(
                f'{mediator_col} ~ {treatment_col}{cov_plus}', data=data
            ).fit()
        else:
            m_model = smf.logit(
                f'{mediator_col} ~ {treatment_col}{cov_plus}', data=data
            ).fit(disp=0)

        # Outcome model
        if outcome_type == 'continuous':
            y_model = smf.ols(
                f'{outcome_col} ~ {treatment_col} * {mediator_col}{cov_plus}',
                data=data
            ).fit()
        else:
            y_model = smf.logit(
                f'{outcome_col} ~ {treatment_col} * {mediator_col}{cov_plus}',
                data=data
            ).fit(disp=0)

        # Simulate mediator under treatment/control
        n = len(data)
        sim_data = data.copy()

        # M(1): mediator when treated
        sim_data[treatment_col] = 1
        if mediator_type == 'continuous':
            m1_pred = m_model.predict(sim_data)
            m1 = m1_pred + np.random.normal(0, np.sqrt(m_model.mse_resid), n)
        else:
            m1_prob = m_model.predict(sim_data)
            m1 = np.random.binomial(1, m1_prob)

        # M(0): mediator when control
        sim_data[treatment_col] = 0
        if mediator_type == 'continuous':
            m0_pred = m_model.predict(sim_data)
            m0 = m0_pred + np.random.normal(0, np.sqrt(m_model.mse_resid), n)
        else:
            m0_prob = m_model.predict(sim_data)
            m0 = np.random.binomial(1, m0_prob)

        # Y(1, M(1)) - Y(1, M(0)): ACME under treatment
        sim_data[treatment_col] = 1
        sim_data[mediator_col] = m1
        y11 = y_model.predict(sim_data).mean()
        sim_data[mediator_col] = m0
        y10 = y_model.predict(sim_data).mean()

        # Y(1, M(0)) - Y(0, M(0)): ADE under control mediator
        sim_data[treatment_col] = 0
        sim_data[mediator_col] = m0
        y00 = y_model.predict(sim_data).mean()

        acme = y11 - y10
        ade = y10 - y00
        total = y11 - y00

        return acme, ade, total

    # Point estimate
    acme, ade, total = _estimate_once(df)
    pct_med = (acme / total * 100) if total != 0 else 0

    # Bootstrap
    boot_acme, boot_ade, boot_total = [], [], []
    for i in range(n_boot):
        boot_df = df.sample(n=len(df), replace=True, random_state=i)
        try:
            a, d, t = _estimate_once(boot_df)
            boot_acme.append(a)
            boot_ade.append(d)
            boot_total.append(t)
        except Exception:
            continue

    acme_ci = np.percentile(boot_acme, [2.5, 97.5])
    ade_ci = np.percentile(boot_ade, [2.5, 97.5])
    total_ci = np.percentile(boot_total, [2.5, 97.5])

    # P-value (proportion of bootstrap not crossing 0)
    acme_p = 2 * min((np.array(boot_acme) > 0).mean(),
                     (np.array(boot_acme) < 0).mean())

    print("=== Causal Mediation Analysis (ACME) ===")
    print(f"ACME (indirect):   {acme:.4f} (95% CI: {acme_ci[0]:.4f} to {acme_ci[1]:.4f}, "
          f"P={acme_p:.4f})")
    print(f"ADE (direct):      {ade:.4f} (95% CI: {ade_ci[0]:.4f} to {ade_ci[1]:.4f})")
    print(f"Total effect:      {total:.4f} (95% CI: {total_ci[0]:.4f} to {total_ci[1]:.4f})")
    print(f"% Mediated:        {pct_med:.1f}%")

    return {
        'ACME': acme, 'ACME_ci': acme_ci, 'ACME_p': acme_p,
        'ADE': ade, 'ADE_ci': ade_ci,
        'total': total, 'total_ci': total_ci,
        'pct_mediated': pct_med,
    }


def plot_mediation_diagram(results, treatment_name, mediator_name, outcome_name):
    """Visual mediation path diagram.

    Output: matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Boxes
    for x, y, label in [(1, 3, treatment_name), (5, 5.5, mediator_name), (9, 3, outcome_name)]:
        ax.add_patch(plt.Rectangle((x-0.9, y-0.4), 1.8, 0.8,
                     fill=True, facecolor='lightblue', edgecolor='black'))
        ax.text(x, y, label, ha='center', va='center', fontsize=11, fontweight='bold')

    # Arrows with coefficients
    a = results.get('a_path', results.get('ACME', 0))
    b = results.get('b_path', 0)
    c_prime = results.get('direct_effect', results.get('ADE', 0))
    pct = results.get('pct_mediated', 0)

    # A → M
    ax.annotate('', xy=(4.1, 5.5), xytext=(1.9, 3.4),
               arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    ax.text(2.8, 4.8, f'a = {a:.3f}', fontsize=10, color='blue')

    # M → Y
    ax.annotate('', xy=(8.1, 3.4), xytext=(5.9, 5.1),
               arrowprops=dict(arrowstyle='->', color='blue', lw=2))
    ax.text(7.2, 4.8, f'b = {b:.3f}', fontsize=10, color='blue')

    # A → Y (direct)
    ax.annotate('', xy=(8.1, 3), xytext=(1.9, 3),
               arrowprops=dict(arrowstyle='->', color='red', lw=2))
    ax.text(5, 2.3, f"c' = {c_prime:.3f} (direct)", fontsize=10, color='red')

    ax.text(5, 1, f"% Mediated: {pct:.1f}%", fontsize=12,
            ha='center', fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightyellow'))

    plt.tight_layout()
    return fig


# ==============================
# INTERACTION / EFFECT MODIFICATION
# ==============================

def test_interaction(df, treatment_col, modifier_col, outcome_col,
                     covariates=None, outcome_type='continuous'):
    """Test treatment-by-modifier interaction.

    Input:
        modifier_col: effect modifier variable (binary or continuous)
        outcome_type: 'continuous' | 'binary' | 'survival'
    Output:
        interaction coefficient, p-value, stratum-specific effects
    """
    cov_str = ' + '.join(covariates) if covariates else ''
    cov_plus = f' + {cov_str}' if cov_str else ''

    if outcome_type == 'continuous':
        formula = f'{outcome_col} ~ {treatment_col} * {modifier_col}{cov_plus}'
        model = smf.ols(formula, data=df).fit()
    elif outcome_type == 'binary':
        formula = f'{outcome_col} ~ {treatment_col} * {modifier_col}{cov_plus}'
        model = smf.logit(formula, data=df).fit(disp=0)

    # Find interaction term
    interaction_term = f'{treatment_col}:{modifier_col}'
    if interaction_term not in model.params.index:
        # Try reversed order
        interaction_term = f'{modifier_col}:{treatment_col}'

    interaction_coef = model.params.get(interaction_term, np.nan)
    interaction_p = model.pvalues.get(interaction_term, np.nan)

    print(f"=== Interaction Test: {treatment_col} x {modifier_col} ===")
    print(f"Interaction coefficient: {interaction_coef:.4f}")
    print(f"Interaction P-value:     {interaction_p:.4f}")

    # Stratum-specific effects
    if df[modifier_col].nunique() <= 5:  # categorical
        for level in sorted(df[modifier_col].unique()):
            sub = df[df[modifier_col] == level]
            if outcome_type == 'continuous':
                sub_model = smf.ols(f'{outcome_col} ~ {treatment_col}{cov_plus}',
                                   data=sub).fit()
            else:
                sub_model = smf.logit(f'{outcome_col} ~ {treatment_col}{cov_plus}',
                                     data=sub).fit(disp=0)
            coef = sub_model.params[treatment_col]
            ci = sub_model.conf_int().loc[treatment_col]
            p = sub_model.pvalues[treatment_col]
            print(f"  {modifier_col}={level}: effect={coef:.4f} "
                  f"(95% CI: {ci[0]:.4f} to {ci[1]:.4f}, P={p:.4f}), N={len(sub)}")

    return {
        'interaction_coef': interaction_coef,
        'interaction_p': interaction_p,
        'model': model,
    }


# ==============================
# SUBGROUP FOREST PLOT
# ==============================

def subgroup_forest_plot(df, treatment_col, outcome_col, subgroup_vars,
                         covariates=None, outcome_type='continuous'):
    """Generate subgroup analysis with forest plot and interaction p-values.

    Input:
        subgroup_vars: dict of {display_name: (column, [level1, level2])} or
                       dict of {display_name: column} for auto-binarization at median
    Output:
        forest_data: DataFrame with subgroup effects
        fig: forest plot Figure
    """
    results = []

    for display_name, spec in subgroup_vars.items():
        if isinstance(spec, tuple):
            col, levels = spec
        else:
            col = spec
            median_val = df[col].median()
            df[f'{col}_cat'] = (df[col] >= median_val).astype(int)
            col = f'{col}_cat'
            levels = [0, 1]
            display_name = f'{display_name} (< vs >= median)'

        # Interaction test
        interaction_result = test_interaction(
            df, treatment_col, col, outcome_col, covariates, outcome_type
        )
        p_interaction = interaction_result['interaction_p']

        for level in levels:
            sub = df[df[col] == level]
            cov_plus = (' + ' + ' + '.join(covariates)) if covariates else ''

            if outcome_type == 'continuous':
                model = smf.ols(f'{outcome_col} ~ {treatment_col}{cov_plus}',
                               data=sub).fit()
                effect = model.params[treatment_col]
                ci = model.conf_int().loc[treatment_col]
            elif outcome_type == 'binary':
                model = smf.logit(f'{outcome_col} ~ {treatment_col}{cov_plus}',
                                 data=sub).fit(disp=0)
                effect = np.exp(model.params[treatment_col])
                ci = np.exp(model.conf_int().loc[treatment_col])

            results.append({
                'subgroup': f'{display_name}: {level}',
                'n': len(sub),
                'effect': effect,
                'ci_lower': ci[0],
                'ci_upper': ci[1],
                'p_interaction': p_interaction,
            })

    forest_df = pd.DataFrame(results)

    # Forest plot
    n_rows = len(forest_df)
    fig, ax = plt.subplots(figsize=(10, max(4, n_rows * 0.6)))
    y_pos = range(n_rows - 1, -1, -1)

    for i, (_, row) in enumerate(forest_df.iterrows()):
        y = list(y_pos)[i]
        ax.errorbarx = ax.plot([row['ci_lower'], row['ci_upper']], [y, y],
                               'b-', linewidth=1.5)
        ax.plot(row['effect'], y, 'bs', markersize=8)

    ref_val = 0 if outcome_type == 'continuous' else 1
    ax.axvline(x=ref_val, color='black', linestyle='--', alpha=0.5)

    ax.set_yticks(list(y_pos))
    labels = [f"{r['subgroup']} (n={r['n']})" for _, r in forest_df.iterrows()]
    ax.set_yticklabels(labels)
    xlabel = 'Treatment Effect (Mean Difference)' if outcome_type == 'continuous' else 'Odds Ratio'
    ax.set_xlabel(xlabel)
    ax.set_title('Subgroup Analysis — Forest Plot')

    # Add p_interaction on the right
    for i, (_, row) in enumerate(forest_df.iterrows()):
        y = list(y_pos)[i]
        if i % 2 == 0:  # first level of each subgroup
            ax.text(ax.get_xlim()[1] * 0.95, y + 0.3,
                    f'P_int={row["p_interaction"]:.3f}',
                    fontsize=8, ha='right', color='red')

    plt.tight_layout()

    print("\n=== Subgroup Forest Plot Data ===")
    print(forest_df.to_string(index=False))
    return forest_df, fig
```

## Output
- Mediation path diagram with coefficients
- ACME (indirect effect) with bootstrap 95% CI and P-value
- ADE (direct effect) with CI
- % mediated
- Interaction test results with P-value
- Stratum-specific treatment effects
- Forest plot with interaction P-values
- Sobel test (for Baron-Kenny)
- Complete executable Python code
