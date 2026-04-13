Implement Bayesian statistical analysis for clinical trials and observational studies.

User input: $ARGUMENTS

## Instructions

### 1. When to Use Bayesian Methods
- **Adaptive trial designs**: interim analyses with probability-based stopping
- **Small sample sizes**: incorporate prior information to stabilize estimates
- **Ordinal/complex outcomes**: natural framework for ordinal mixed models
- **Probability statements**: "probability of benefit" rather than "reject null"
- **Medical device trials**: FDA guidance supports Bayesian approaches
- **Prior evidence integration**: leverage historical data formally

### 2. Input Specification

```
DataFrame with columns:
  - outcome: continuous, binary, ordinal, or time-to-event
  - group: treatment groups
  - covariates: confounders/predictors
  - (optional) historical_data: prior study data for informative priors

Analysis parameters:
  - prior_type: 'non_informative' | 'weakly_informative' | 'informative'
  - n_samples: MCMC samples (default: 4000)
  - n_chains: parallel chains (default: 4)
  - target_rope: Region of Practical Equivalence (optional)
```

### 3. Prior Specification

| Prior Type | When | Example |
|-----------|------|---------|
| **Non-informative** | No prior knowledge, regulatory requirement | Normal(0, 10000) |
| **Weakly informative** | Default recommendation (regularizing) | Normal(0, 2.5) for logistic coefficients |
| **Informative** | Strong prior data, meta-analytic prior | Normal(mu_prior, sigma_prior) from historical data |
| **Power prior** | Discount historical data by alpha (0-1) | L(theta|D_0)^alpha x L(theta|D) |
| **MAP (Meta-Analytic Predictive)** | Multiple historical studies | Mixture of posteriors |

**Sensitivity analysis**: ALWAYS run with at least 2 priors (informative + vague) to assess prior influence.

### 4. Bayesian Treatment Effect Estimation

**Continuous outcome**:
- Bayesian linear regression or t-test
- Report: posterior mean difference, 95% CrI (Credible Interval)
- P(treatment > control) = probability of superiority

**Binary outcome**:
- Bayesian logistic regression
- Report: posterior OR/RR, 95% CrI
- P(OR > 1) = probability of harmful effect

**Ordinal outcome** (as in EMORI-HCM):
- Bayesian cumulative ordinal model (proportional odds)
- Report: posterior common OR, 95% CrI
- P(benefit) = P(common OR > 1)

**Time-to-event**:
- Bayesian Cox or piecewise exponential
- Report: posterior HR, 95% CrI

### 5. Key Output Metrics

| Metric | Description | Interpretation |
|--------|------------|----------------|
| **Posterior mean** | Central estimate | Point estimate |
| **95% CrI** | 95% credible interval | 95% probability true value lies within |
| **P(benefit)** | P(effect > 0) | Direct probability of treatment benefit |
| **P(clinically meaningful)** | P(effect > MCID) | Probability of exceeding meaningful threshold |
| **ROPE** | P(effect in [-delta, delta]) | Probability of practical equivalence |
| **Bayes Factor** | BF_10 = P(data|H1)/P(data|H0) | Evidence for H1 vs H0 |
| **HDI** | Highest Density Interval | Narrowest interval containing 95% of posterior |

### 6. MCMC Diagnostics (MANDATORY)

- **Rhat (Gelman-Rubin)**: < 1.01 for all parameters (convergence)
- **ESS (Effective Sample Size)**: > 400 for stable estimates
- **Trace plots**: visual check for mixing and stationarity
- **Divergent transitions**: 0 divergences (for NUTS/HMC)
- **Posterior predictive check**: simulated data resembles observed data

### 7. Bayesian Adaptive Design (for trials)

- **Posterior probability stopping**: stop if P(benefit) > 0.99 or P(futility) > 0.95
- **Predictive probability**: probability that final analysis will be successful
- **Bayesian information borrowing**: adaptive prior from concurrent/historical data
- **Response-adaptive randomization**: shift allocation based on accumulating data

### 8. Template Python Code

```python
import pandas as pd
import numpy as np
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# INPUT SPECIFICATION
# ============================================================
# df: pd.DataFrame with columns:
#   - 'outcome': continuous (float), binary (0/1), or ordinal (int)
#   - 'group': treatment indicator (0=control, 1=treatment)
#   - covariates: additional predictors
#
# prior_config: dict with prior specifications
# ============================================================

def bayesian_two_group_continuous(df, outcome_col, group_col,
                                  prior='weakly_informative', n_samples=4000):
    """Bayesian comparison of two groups (continuous outcome).

    Input:
        df: DataFrame
        outcome_col: str, continuous outcome
        group_col: str, binary group (0/1)
        prior: 'non_informative' | 'weakly_informative' | 'informative'
    Output:
        trace: posterior samples
        summary: posterior summary with CrI
        prob_benefit: P(treatment > control)
    """
    y = df[outcome_col].values
    group = df[group_col].values
    y_sd = np.std(y)

    with pm.Model() as model:
        # Priors
        if prior == 'non_informative':
            mu_c = pm.Normal('mu_control', mu=0, sigma=100)
            effect = pm.Normal('effect', mu=0, sigma=100)
        elif prior == 'weakly_informative':
            mu_c = pm.Normal('mu_control', mu=np.mean(y), sigma=y_sd * 5)
            effect = pm.Normal('effect', mu=0, sigma=y_sd * 2)
        elif prior == 'informative':
            # Replace with actual prior from historical data
            mu_c = pm.Normal('mu_control', mu=np.mean(y[group==0]),
                           sigma=y_sd)
            effect = pm.Normal('effect', mu=0, sigma=y_sd)

        sigma = pm.HalfNormal('sigma', sigma=y_sd * 2)

        # Likelihood
        mu = mu_c + effect * group
        likelihood = pm.Normal('y', mu=mu, sigma=sigma, observed=y)

        # Sample
        trace = pm.sample(n_samples, chains=4, return_inferencedata=True,
                         random_seed=42, progressbar=True)

    # Summary
    summary = az.summary(trace, var_names=['effect', 'mu_control', 'sigma'],
                        hdi_prob=0.95)
    print("=== Bayesian Two-Group Comparison ===")
    print(summary)

    # Probability of benefit
    effect_samples = trace.posterior['effect'].values.flatten()
    prob_benefit = (effect_samples > 0).mean()
    print(f"\nP(treatment benefit): {prob_benefit:.4f}")
    print(f"P(effect > 0): {prob_benefit:.4f}")

    # MCMC diagnostics
    rhat = az.rhat(trace)
    ess = az.ess(trace)
    print(f"\nMCMC Diagnostics:")
    print(f"  Rhat (effect): {rhat['effect'].values:.4f} (target: < 1.01)")
    print(f"  ESS (effect):  {ess['effect'].values:.0f} (target: > 400)")

    return trace, summary, prob_benefit


def bayesian_logistic(df, outcome_col, group_col, covariates=None,
                      prior='weakly_informative', n_samples=4000):
    """Bayesian logistic regression (binary outcome).

    Output:
        trace, posterior OR with CrI, P(OR > 1)
    """
    y = df[outcome_col].values
    X_cols = [group_col] + (covariates or [])
    X = df[X_cols].values

    with pm.Model() as model:
        if prior == 'weakly_informative':
            beta = pm.Normal('beta', mu=0, sigma=2.5, shape=X.shape[1])
            intercept = pm.Normal('intercept', mu=0, sigma=5)
        else:
            beta = pm.Normal('beta', mu=0, sigma=10, shape=X.shape[1])
            intercept = pm.Normal('intercept', mu=0, sigma=10)

        logit_p = intercept + pm.math.dot(X, beta)
        likelihood = pm.Bernoulli('y', logit_p=logit_p, observed=y)

        trace = pm.sample(n_samples, chains=4, return_inferencedata=True,
                         random_seed=42)

    # Extract OR
    beta_samples = trace.posterior['beta'].values[:, :, 0].flatten()  # treatment coef
    or_samples = np.exp(beta_samples)

    print("=== Bayesian Logistic Regression ===")
    print(f"Posterior OR: {np.median(or_samples):.3f} "
          f"(95% CrI: {np.percentile(or_samples, 2.5):.3f} "
          f"to {np.percentile(or_samples, 97.5):.3f})")
    print(f"P(OR > 1): {(or_samples > 1).mean():.4f}")
    print(f"P(OR < 1): {(or_samples < 1).mean():.4f}")

    return trace, or_samples


def bayesian_ordinal_model(df, outcome_col, group_col, n_categories=None,
                           n_samples=4000):
    """Bayesian cumulative ordinal model (as used in EMORI-HCM).

    Input:
        outcome_col: ordinal outcome (integer 0, 1, 2, ...)
        n_categories: number of ordinal levels (auto-detected if None)
    Output:
        trace, common OR, P(benefit)
    """
    y = df[outcome_col].values.astype(int)
    group = df[group_col].values

    if n_categories is None:
        n_categories = len(np.unique(y))

    with pm.Model() as model:
        # Treatment effect (log-OR scale)
        beta = pm.Normal('beta_treatment', mu=0, sigma=2.5)

        # Cutpoints (ordered)
        cutpoints = pm.Normal('cutpoints', mu=0, sigma=5,
                             shape=n_categories - 1,
                             transform=pm.distributions.transforms.ordered)

        # Cumulative logit model
        eta = cutpoints - beta * group[:, np.newaxis]
        likelihood = pm.OrderedLogistic('y', eta=beta * group, cutpoints=cutpoints,
                                        observed=y)

        trace = pm.sample(n_samples, chains=4, return_inferencedata=True,
                         random_seed=42)

    beta_samples = trace.posterior['beta_treatment'].values.flatten()
    or_samples = np.exp(beta_samples)

    print("=== Bayesian Ordinal Model ===")
    print(f"Common OR: {np.median(or_samples):.3f} "
          f"(95% CrI: {np.percentile(or_samples, 2.5):.3f} "
          f"to {np.percentile(or_samples, 97.5):.3f})")
    print(f"P(benefit): {(or_samples > 1).mean():.4f}")

    return trace, or_samples


def bayesian_mixed_model(df, outcome_col, group_col, time_col, subject_col,
                         n_samples=4000):
    """Bayesian linear mixed model for longitudinal data.

    Output: posterior treatment x time interaction, random effects variance
    """
    y = df[outcome_col].values
    group = df[group_col].values
    time = df[time_col].values.astype(float)
    subjects = pd.Categorical(df[subject_col]).codes

    n_subjects = len(np.unique(subjects))

    with pm.Model() as model:
        # Fixed effects
        intercept = pm.Normal('intercept', mu=np.mean(y), sigma=10)
        beta_group = pm.Normal('beta_group', mu=0, sigma=5)
        beta_time = pm.Normal('beta_time', mu=0, sigma=5)
        beta_interaction = pm.Normal('beta_group_x_time', mu=0, sigma=5)

        # Random effects
        sigma_subj = pm.HalfNormal('sigma_subject', sigma=5)
        re_subject = pm.Normal('re_subject', mu=0, sigma=sigma_subj,
                              shape=n_subjects)

        # Residual
        sigma = pm.HalfNormal('sigma', sigma=5)

        # Likelihood
        mu = (intercept + beta_group * group + beta_time * time +
              beta_interaction * group * time + re_subject[subjects])
        likelihood = pm.Normal('y', mu=mu, sigma=sigma, observed=y)

        trace = pm.sample(n_samples, chains=4, return_inferencedata=True,
                         random_seed=42)

    print("=== Bayesian Mixed Model ===")
    summary = az.summary(trace, var_names=[
        'beta_group', 'beta_time', 'beta_group_x_time',
        'sigma_subject', 'sigma'
    ], hdi_prob=0.95)
    print(summary)

    # Key: treatment x time interaction
    interaction_samples = trace.posterior['beta_group_x_time'].values.flatten()
    print(f"\nP(treatment accelerates improvement): "
          f"{(interaction_samples > 0).mean():.4f}")

    return trace, summary


def plot_posterior(trace, var_name, rope=None, ref_val=0, title=None):
    """Plot posterior distribution with HDI and ROPE.

    Output: matplotlib Figure
    """
    samples = trace.posterior[var_name].values.flatten()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(samples, bins=100, density=True, alpha=0.7, color='steelblue')
    ax.axvline(np.median(samples), color='red', linestyle='-', label='Median')

    # HDI
    hdi = az.hdi(trace, var_names=[var_name], hdi_prob=0.95)
    hdi_low = hdi[var_name].values[0]
    hdi_high = hdi[var_name].values[1]
    ax.axvline(hdi_low, color='orange', linestyle='--', label=f'95% HDI')
    ax.axvline(hdi_high, color='orange', linestyle='--')

    # Reference value
    ax.axvline(ref_val, color='black', linestyle=':', label=f'Ref={ref_val}')

    # ROPE
    if rope:
        ax.axvspan(rope[0], rope[1], alpha=0.2, color='green', label='ROPE')
        in_rope = ((samples >= rope[0]) & (samples <= rope[1])).mean()
        print(f"P(in ROPE [{rope[0]}, {rope[1]}]): {in_rope:.4f}")

    ax.set_xlabel(var_name)
    ax.set_ylabel('Density')
    ax.set_title(title or f'Posterior Distribution: {var_name}')
    ax.legend()
    plt.tight_layout()
    return fig


def mcmc_diagnostics_report(trace, var_names=None):
    """Comprehensive MCMC diagnostics.

    Output: diagnostic summary + trace plots
    """
    if var_names is None:
        var_names = [v for v in trace.posterior.data_vars if v != 're_subject']

    print("=== MCMC Diagnostics ===")
    rhat = az.rhat(trace, var_names=var_names)
    ess = az.ess(trace, var_names=var_names)

    for var in var_names:
        r = rhat[var].values
        e = ess[var].values
        r_val = r.item() if r.ndim == 0 else r.max()
        e_val = e.item() if e.ndim == 0 else e.min()
        status = "OK" if r_val < 1.01 and e_val > 400 else "WARNING"
        print(f"  {var:30s} Rhat={r_val:.4f}  ESS={e_val:.0f}  [{status}]")

    # Trace plots
    fig = az.plot_trace(trace, var_names=var_names[:6])
    plt.tight_layout()
    return fig


def compute_bayes_factor(trace, var_name, null_value=0, prior_sd=2.5):
    """Savage-Dickey Bayes Factor (for point null).

    Output: BF_10, interpretation
    """
    from scipy.stats import norm

    samples = trace.posterior[var_name].values.flatten()

    # Prior density at null
    prior_at_null = norm.pdf(null_value, loc=0, scale=prior_sd)

    # Posterior density at null (KDE)
    from scipy.stats import gaussian_kde
    kde = gaussian_kde(samples)
    posterior_at_null = kde(null_value)[0]

    bf_10 = prior_at_null / posterior_at_null

    interpretation = (
        "Anecdotal" if bf_10 < 3 else
        "Moderate" if bf_10 < 10 else
        "Strong" if bf_10 < 30 else
        "Very strong" if bf_10 < 100 else
        "Extreme"
    )

    print(f"=== Bayes Factor (Savage-Dickey) ===")
    print(f"  BF_10 = {bf_10:.2f} ({interpretation} evidence for H1)")
    print(f"  BF_01 = {1/bf_10:.2f} (evidence for H0)")
    return bf_10, interpretation
```

## Output
- Posterior summary table (mean, median, 95% CrI, ESS, Rhat)
- Posterior distribution plots with HDI and ROPE
- P(benefit), P(clinically meaningful benefit)
- MCMC diagnostic report (trace plots, Rhat, ESS)
- Bayes Factor (if requested)
- Prior sensitivity analysis (comparison across priors)
- Posterior predictive check
- Complete executable Python code (PyMC)
