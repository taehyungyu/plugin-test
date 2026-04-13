Implement longitudinal data analysis with mixed-effects models, MMRM, and GEE for repeated measures clinical data.

User input: $ARGUMENTS

## Instructions

### 1. Data Structure Assessment

**Input format**:
```
DataFrame (long format) with columns:
  - subject_id: patient identifier
  - time: measurement timepoint (numeric or categorical visit)
  - outcome: repeated outcome measurement
  - group: treatment/exposure group
  - covariates: baseline and time-varying confounders
```

- **Check**: balanced vs unbalanced design (unequal visits per subject)
- **Check**: missing data pattern — MCAR, MAR, MNAR
- **Check**: number of subjects, measurements per subject, total observations

### 2. Method Selection Guide

| Scenario | Recommended Method | Key Advantage |
|----------|-------------------|---------------|
| Continuous outcome, MAR missing | **MMRM** | FDA/EMA preferred for RCTs, handles MAR |
| Continuous outcome, complex random effects | **LMM** | Flexible correlation structure |
| Binary/count outcome, repeated | **GLMM** | Non-normal outcomes |
| Population-average effect (not subject-specific) | **GEE** | Robust to correlation misspecification |
| Non-ignorable missing (MNAR) | **Pattern-mixture / selection model** | Sensitivity analysis |
| Many timepoints, smooth trajectories | **Growth curve model** | Captures nonlinear trends |

### 3. MMRM (Mixed-Model Repeated Measures)

**The FDA/EMA preferred method for RCT primary analysis**.

**Model**: Y_ij = beta_0 + beta_1 * Treatment + beta_2 * Time + beta_3 * Treatment x Time + beta_4 * Baseline + epsilon_ij

**Key specifications**:
- **Fixed effects**: treatment, time (categorical), treatment x time interaction, baseline value
- **Covariance structure**: unstructured (UN) is default — no random effects needed
- **Degrees of freedom**: Kenward-Roger (preferred) or Satterthwaite
- **Primary estimand**: treatment difference at final timepoint (from treatment x time interaction)
- **Missing data**: MAR assumed — valid under MAR without imputation

**Covariance structure selection** (by AIC/BIC):

| Structure | Parameters | When |
|-----------|-----------|------|
| **Unstructured (UN)** | p(p+1)/2 | Default, most flexible |
| **Compound Symmetry (CS)** | 2 | Equal correlation across time |
| **AR(1)** | 2 | Declining correlation with time lag |
| **Toeplitz** | p | Correlation depends on lag only |
| **Heterogeneous CS/AR(1)** | p+1 | Unequal variances across time |

### 4. LMM (Linear Mixed Model)

**Model**: Y_ij = (X_ij * beta) + (Z_ij * b_i) + epsilon_ij

- **Fixed effects**: population-level parameters
- **Random effects**: subject-specific deviations (intercept, slope, or both)
- **Random intercept**: baseline differences between subjects
- **Random slope**: different rates of change per subject
- **Test random effects**: likelihood ratio test (LRT) comparing nested models

### 5. GLMM (Generalized Linear Mixed Model)

- **Binary outcome**: logistic GLMM → OR interpretation (subject-specific)
- **Count outcome**: Poisson or negative binomial GLMM → rate ratio
- **Ordinal outcome**: cumulative logit mixed model
- **Note**: GLMM gives conditional (subject-specific) effects, not marginal (population-average)

### 6. GEE (Generalized Estimating Equations)

- **Population-average** (marginal) model — no random effects
- Specify **working correlation**: independent, exchangeable, AR(1), unstructured
- **Sandwich (robust) SE**: consistent even if working correlation is wrong
- Use when population-average effect is of interest (e.g., policy questions)
- **QIC** for model selection (analogue of AIC)

### 7. Missing Data Strategy

| Pattern | Method | Assumption |
|---------|--------|------------|
| **MCAR/MAR** | MMRM or LMM (likelihood-based) | Direct modeling, no imputation needed |
| **MAR (sensitivity)** | Multiple imputation + analysis | Compare with MMRM results |
| **MNAR** | Pattern-mixture model | Different model per dropout pattern |
| **MNAR** | Tipping point analysis | How much shift in missing data to reverse conclusion |
| **MNAR** | Selection model (Heckman) | Model dropout process explicitly |

### 8. Template Python Code

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
# df: pd.DataFrame in LONG format with columns:
#   - 'subject_id': patient identifier (str/int)
#   - 'visit': timepoint (int or categorical, e.g., 0, 4, 8, 12, 24 weeks)
#   - 'outcome': continuous measurement (float)
#   - 'group': treatment group (str, e.g., 'treatment', 'placebo')
#   - 'baseline_value': baseline outcome value (float)
#   - additional covariates as needed
# ============================================================

def describe_longitudinal_data(df, subject_col, time_col, outcome_col, group_col):
    """Describe the longitudinal data structure.

    Output: summary statistics, missing data pattern, spaghetti plot
    """
    print("=== Longitudinal Data Summary ===")
    print(f"Subjects: {df[subject_col].nunique()}")
    print(f"Timepoints: {sorted(df[time_col].unique())}")
    print(f"Total observations: {len(df)}")

    visits_per_subject = df.groupby(subject_col)[time_col].count()
    print(f"Visits/subject: mean={visits_per_subject.mean():.1f}, "
          f"min={visits_per_subject.min()}, max={visits_per_subject.max()}")

    # Missing data pattern
    pivot = df.pivot_table(index=subject_col, columns=time_col,
                           values=outcome_col, aggfunc='first')
    missing_pct = pivot.isnull().mean() * 100
    print(f"\nMissing % by timepoint:")
    for t, pct in missing_pct.items():
        print(f"  Visit {t}: {pct:.1f}%")

    # Spaghetti plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    groups = df[group_col].unique()
    for i, grp in enumerate(groups):
        grp_df = df[df[group_col] == grp]
        for subj in grp_df[subject_col].unique():
            subj_df = grp_df[grp_df[subject_col] == subj]
            axes[i].plot(subj_df[time_col], subj_df[outcome_col], alpha=0.2, color='gray')
        # Group mean
        mean_df = grp_df.groupby(time_col)[outcome_col].mean()
        axes[i].plot(mean_df.index, mean_df.values, 'o-', color='red', linewidth=2)
        axes[i].set_title(f'{grp} (n={grp_df[subject_col].nunique()})')
        axes[i].set_xlabel('Time')
        axes[i].set_ylabel(outcome_col)
    plt.suptitle('Individual Trajectories + Group Mean')
    plt.tight_layout()
    return fig


def fit_mmrm(df, outcome_col, group_col, time_col, baseline_col, subject_col,
             covariance='un'):
    """Fit MMRM model (Mixed-Model Repeated Measures).

    Input:
        covariance: 'un' (unstructured), 'cs' (compound symmetry), 'ar1'
    Output:
        model results with treatment effect at each timepoint
    """
    df = df.copy()
    df[time_col] = df[time_col].astype(str)  # categorical time

    # Formula: outcome ~ group * visit + baseline
    formula = f'{outcome_col} ~ C({group_col}) * C({time_col}) + {baseline_col}'

    # Covariance structure mapping
    cov_map = {
        'un': sm.cov_struct.Unstructured(),
        'cs': sm.cov_struct.Exchangeable(),
        'ar1': sm.cov_struct.Autoregressive(),
    }

    # Use GEE with specified covariance as MMRM approximation
    # For true MMRM, use R's nlme/mmrm or SAS PROC MIXED
    model = smf.gee(
        formula, groups=subject_col, data=df,
        cov_struct=cov_map.get(covariance, sm.cov_struct.Exchangeable()),
        family=sm.families.Gaussian()
    )
    result = model.fit()
    print("=== MMRM Results ===")
    print(result.summary())

    return result


def fit_lmm(df, outcome_col, group_col, time_col, subject_col,
            random_effects='intercept_slope', covariates=None):
    """Fit Linear Mixed Model.

    Input:
        random_effects: 'intercept' | 'intercept_slope'
        covariates: list of additional covariate names
    Output:
        fitted MixedLM result
    """
    df = df.copy()
    # Ensure numeric time
    if df[time_col].dtype == object:
        time_map = {v: i for i, v in enumerate(sorted(df[time_col].unique()))}
        df['time_num'] = df[time_col].map(time_map)
    else:
        df['time_num'] = df[time_col]

    # Build formula
    fixed_parts = [f'C({group_col})', 'time_num', f'C({group_col}):time_num']
    if covariates:
        fixed_parts.extend(covariates)
    formula = f'{outcome_col} ~ ' + ' + '.join(fixed_parts)

    # Random effects
    if random_effects == 'intercept':
        re_formula = '1'
    elif random_effects == 'intercept_slope':
        re_formula = '1 + time_num'

    model = smf.mixedlm(formula, data=df, groups=df[subject_col],
                        re_formula=re_formula)
    result = model.fit(reml=True)

    print("=== Linear Mixed Model Results ===")
    print(result.summary())

    # Key result: group x time interaction = treatment effect on rate of change
    print(f"\n=== Key Interpretation ===")
    for param in result.params.index:
        if 'group' in param.lower() and 'time' in param.lower():
            coef = result.params[param]
            pval = result.pvalues[param]
            ci = result.conf_int().loc[param]
            print(f"  Group x Time interaction: {coef:.4f} "
                  f"(95% CI: {ci[0]:.4f} to {ci[1]:.4f}, P={pval:.4f})")
    return result


def fit_gee(df, outcome_col, group_col, time_col, subject_col,
            family='gaussian', corr_structure='exchangeable'):
    """Fit GEE for population-average effects.

    Input:
        family: 'gaussian' | 'binomial' | 'poisson'
        corr_structure: 'exchangeable' | 'ar1' | 'unstructured' | 'independent'
    Output:
        GEE result with robust SE
    """
    df = df.copy()
    df[time_col] = df[time_col].astype(str)

    formula = f'{outcome_col} ~ C({group_col}) * C({time_col})'

    family_map = {
        'gaussian': sm.families.Gaussian(),
        'binomial': sm.families.Binomial(),
        'poisson': sm.families.Poisson(),
    }
    corr_map = {
        'exchangeable': sm.cov_struct.Exchangeable(),
        'ar1': sm.cov_struct.Autoregressive(),
        'unstructured': sm.cov_struct.Unstructured(),
        'independent': sm.cov_struct.Independence(),
    }

    model = smf.gee(
        formula, groups=subject_col, data=df,
        family=family_map[family], cov_struct=corr_map[corr_structure]
    )
    result = model.fit()
    print(f"=== GEE Results (family={family}, corr={corr_structure}) ===")
    print(result.summary())
    return result


def compare_covariance_structures(df, outcome_col, group_col, time_col,
                                  baseline_col, subject_col):
    """Compare covariance structures using QIC.

    Output: table of QIC values for each structure
    """
    structures = {
        'Independence': sm.cov_struct.Independence(),
        'Exchangeable (CS)': sm.cov_struct.Exchangeable(),
        'Autoregressive (AR1)': sm.cov_struct.Autoregressive(),
        'Unstructured': sm.cov_struct.Unstructured(),
    }

    df = df.copy()
    df[time_col] = df[time_col].astype(str)
    formula = f'{outcome_col} ~ C({group_col}) * C({time_col}) + {baseline_col}'

    results = []
    for name, cov in structures.items():
        try:
            model = smf.gee(formula, groups=subject_col, data=df,
                           cov_struct=cov, family=sm.families.Gaussian())
            res = model.fit()
            qic = res.qic()
            results.append({'Structure': name, 'QIC': qic[0], 'QICu': qic[1]})
        except Exception as e:
            results.append({'Structure': name, 'QIC': np.nan, 'QICu': np.nan})
            print(f"  {name}: failed ({e})")

    qic_df = pd.DataFrame(results).sort_values('QIC')
    print("=== Covariance Structure Comparison (QIC) ===")
    print(qic_df.to_string(index=False))
    print(f"\nRecommended: {qic_df.iloc[0]['Structure']} (lowest QIC)")
    return qic_df


def plot_treatment_effect_over_time(df, outcome_col, group_col, time_col):
    """Plot mean outcome trajectories with 95% CI per group.

    Output: matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    groups = df[group_col].unique()
    colors = ['#2196F3', '#F44336', '#4CAF50', '#FF9800']

    for i, grp in enumerate(groups):
        grp_df = df[df[group_col] == grp]
        summary = grp_df.groupby(time_col)[outcome_col].agg(['mean', 'sem', 'count'])
        summary['ci95'] = 1.96 * summary['sem']
        x = summary.index
        ax.errorbar(x, summary['mean'], yerr=summary['ci95'],
                    fmt='o-', color=colors[i % len(colors)], label=grp,
                    capsize=3, linewidth=2, markersize=6)

    ax.set_xlabel('Timepoint')
    ax.set_ylabel(f'{outcome_col} (mean +/- 95% CI)')
    ax.set_title('Treatment Effect Over Time')
    ax.legend()
    plt.tight_layout()
    return fig


# ============================================================
# FULL PIPELINE
# ============================================================
def run_longitudinal_pipeline(df, outcome_col, group_col, time_col,
                              subject_col, baseline_col=None, method='mmrm'):
    """End-to-end longitudinal analysis pipeline.

    Input:
        method: 'mmrm' | 'lmm' | 'gee'
    Output:
        model_result, figures
    """
    figures = []

    # 1. Data description
    print("=" * 60)
    print("STEP 1: Data Description")
    print("=" * 60)
    fig_desc = describe_longitudinal_data(df, subject_col, time_col, outcome_col, group_col)
    figures.append(('trajectories', fig_desc))

    # 2. Treatment trajectory plot
    fig_effect = plot_treatment_effect_over_time(df, outcome_col, group_col, time_col)
    figures.append(('treatment_effect', fig_effect))

    # 3. Compare covariance structures
    print("\n" + "=" * 60)
    print("STEP 2: Covariance Structure Selection")
    print("=" * 60)
    if baseline_col:
        qic_df = compare_covariance_structures(
            df, outcome_col, group_col, time_col, baseline_col, subject_col
        )

    # 4. Fit model
    print("\n" + "=" * 60)
    print(f"STEP 3: Fit {method.upper()} Model")
    print("=" * 60)
    if method == 'mmrm':
        result = fit_mmrm(df, outcome_col, group_col, time_col,
                         baseline_col, subject_col)
    elif method == 'lmm':
        result = fit_lmm(df, outcome_col, group_col, time_col, subject_col)
    elif method == 'gee':
        result = fit_gee(df, outcome_col, group_col, time_col, subject_col)

    return result, figures
```

## Output
- Data summary: subjects, timepoints, missing pattern
- Individual trajectory (spaghetti) plot
- Group mean trajectory with 95% CI
- Covariance structure comparison (QIC table)
- Model results with treatment x time interaction
- Treatment effect at each timepoint (LS means difference + 95% CI)
- Missing data strategy specification
- Executable Python code
