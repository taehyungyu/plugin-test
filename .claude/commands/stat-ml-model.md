Develop and validate a clinical prediction model using machine learning methods, following TRIPOD guidelines.

User input: $ARGUMENTS

## Instructions

### 1. Problem Framing
- **Task type**: classification (binary/multi-class) or regression
- **Clinical context**: diagnosis, prognosis, treatment response
- **Target variable**: clearly defined, clinically meaningful outcome
- **Time horizon** (for prognosis): e.g., 5-year mortality, 30-day readmission
- **Reporting**: follow TRIPOD+AI checklist

### 2. Input Data Specification

```
DataFrame requirements:
  - target: outcome column (binary 0/1, continuous, or multi-class)
  - features: clinical variables, imaging features, lab values, etc.
  - id: patient identifier (for data leakage prevention)
  - (optional) site: institution for external validation
  - (optional) time/event: for survival prediction tasks
```

### 3. Data Preprocessing Pipeline

| Step | Method | Notes |
|------|--------|-------|
| Missing values | Multiple imputation (MICE) or median/mode | Report % missing per variable |
| Outliers | Winsorize at 1st/99th percentile | Clinical plausibility check |
| Encoding | One-hot (nominal), ordinal (ordered) | Avoid high-cardinality one-hot |
| Scaling | StandardScaler (linear models), none (tree-based) | Fit on train only |
| Class imbalance | SMOTE, class_weight, threshold tuning | Prefer threshold tuning clinically |

### 4. Feature Selection

| Method | Type | When to Use |
|--------|------|-------------|
| **LASSO (L1)** | Embedded | Default for linear models |
| **Elastic Net** | Embedded | Correlated features |
| **Boruta** | Wrapper | Comprehensive, tree-based |
| **mRMR** | Filter | High-dimensional (radiomics, omics) |
| **Recursive Feature Elimination** | Wrapper | Small feature sets |
| **Univariate (p < 0.1)** | Filter | Simple pre-screening |

### 5. Model Selection

| Model | Strengths | Weaknesses | Hyperparameters |
|-------|-----------|------------|-----------------|
| **Logistic Regression** | Interpretable, calibrated, baseline | Linear boundary | C, penalty |
| **Random Forest** | Robust, handles nonlinearity | Black-box, overfits small data | n_estimators, max_depth, min_samples_leaf |
| **XGBoost/LightGBM** | Best tabular performance | Overfits, complex tuning | learning_rate, max_depth, n_estimators, reg_alpha/lambda |
| **SVM (RBF)** | Good margins, kernel trick | No probability by default, slow | C, gamma |
| **Neural Network (MLP)** | Flexible | Needs large data, opaque | layers, dropout, lr |
| **Ensemble (Stacking)** | Combines strengths | Complexity | Base models, meta-learner |

### 6. Validation Strategy

| Strategy | When | Implementation |
|----------|------|----------------|
| **Stratified k-fold CV** | Default (k=5 or 10) | Internal validation |
| **Nested CV** | Hyperparameter tuning + evaluation | Outer=5, Inner=5 |
| **Bootstrap (0.632+)** | Small datasets (<200) | 200+ iterations |
| **Temporal split** | Time-dependent data | Train on older, test on newer |
| **External validation** | Multi-site data available | Completely held-out site |

**CRITICAL**: Never use test data for any training decision (including feature selection, threshold tuning, imputation fitting).

### 7. Performance Metrics

**Discrimination**:
- AUC-ROC (primary for binary classification)
- AUC-PR (preferred for imbalanced data)
- Sensitivity, Specificity at optimal threshold

**Calibration**:
- Calibration plot (observed vs predicted)
- Hosmer-Lemeshow or calibration slope/intercept
- Brier score

**Clinical Utility**:
- Decision Curve Analysis (DCA) — net benefit at threshold range
- Number Needed to Screen/Treat

**Regression**:
- RMSE, MAE, R-squared
- Bland-Altman plot

### 8. Explainability

- **SHAP values**: global importance + individual explanations (preferred)
- **Permutation importance**: model-agnostic
- **Partial dependence plots**: marginal effect of features
- **LIME**: local explanations for individual predictions

### 9. Radiomics Pipeline (if imaging features)

```
Image → Segmentation → Feature Extraction (pyradiomics)
→ Feature Selection (ICC > 0.8, mRMR/LASSO) → Model → Validation
```

- Extract: shape, first-order, GLCM, GLRLM, GLSZM, GLDM features
- Reproducibility: ICC > 0.8 for inter/intra-observer
- Typically 100-1000+ features → aggressive selection needed

### 10. Template Python Code

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    roc_auc_score, roc_curve, brier_score_loss,
    classification_report, confusion_matrix
)
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# INPUT SPECIFICATION
# ============================================================
# df: pd.DataFrame
#   - target_col: str, binary outcome (0/1)
#   - feature_cols: list[str], predictor variable names
#   - (optional) site_col: str, for external validation split
# ============================================================

def preprocess_data(df, feature_cols, target_col, test_size=0.2, random_state=42):
    """Split and preprocess data.

    Input:
        df: DataFrame
        feature_cols: list[str]
        target_col: str
        test_size: float, holdout fraction
    Output:
        X_train, X_test, y_train, y_test, preprocessor (fitted on train)
    """
    from sklearn.model_selection import train_test_split

    X = df[feature_cols].copy()
    y = df[target_col].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    preprocessor = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
    ])
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    print(f"Train: {len(y_train)} (pos={y_train.sum()}, neg={len(y_train)-y_train.sum()})")
    print(f"Test:  {len(y_test)} (pos={y_test.sum()}, neg={len(y_test)-y_test.sum()})")
    return X_train_processed, X_test_processed, y_train, y_test, preprocessor


def feature_selection_lasso(X_train, y_train, feature_names, n_features=20):
    """LASSO-based feature selection.

    Output: selected feature indices and names with coefficients
    """
    from sklearn.linear_model import LogisticRegressionCV
    lasso = LogisticRegressionCV(
        penalty='l1', solver='saga', cv=5, max_iter=5000, random_state=42
    ).fit(X_train, y_train)

    coef = np.abs(lasso.coef_[0])
    top_idx = np.argsort(coef)[::-1][:n_features]
    selected = [(feature_names[i], coef[i]) for i in top_idx if coef[i] > 0]

    print(f"LASSO selected {len(selected)} features:")
    for name, c in selected:
        print(f"  {name}: {c:.4f}")
    return [s[0] for s in selected], top_idx[:len(selected)]


def train_multiple_models(X_train, y_train, X_test, y_test):
    """Train and compare multiple ML models.

    Output:
        results: dict[model_name -> {auc, brier, y_pred_proba}]
        models: dict[model_name -> fitted model]
    """
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(
            n_estimators=500, max_depth=10, min_samples_leaf=10, random_state=42
        ),
        'XGBoost': GradientBoostingClassifier(
            n_estimators=300, max_depth=4, learning_rate=0.05,
            min_samples_leaf=10, random_state=42
        ),
        'SVM (RBF)': SVC(probability=True, kernel='rbf', random_state=42),
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_prob = model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, y_prob)
        brier = brier_score_loss(y_test, y_prob)
        results[name] = {'auc': auc, 'brier': brier, 'y_prob': y_prob}
        print(f"{name:25s} — AUC: {auc:.4f}, Brier: {brier:.4f}")

    return results, models


def cross_validated_evaluation(X, y, model, cv=5):
    """Nested cross-validation for unbiased performance estimation.

    Output: mean AUC, std AUC, fold-wise predictions
    """
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    aucs, briers = [], []
    y_pred_all = np.zeros(len(y))

    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
        X_tr, X_val = X[train_idx], X[val_idx]
        y_tr, y_val = y[train_idx], y[val_idx]

        model_clone = type(model)(**model.get_params())
        model_clone.fit(X_tr, y_tr)
        y_prob = model_clone.predict_proba(X_val)[:, 1]

        aucs.append(roc_auc_score(y_val, y_prob))
        briers.append(brier_score_loss(y_val, y_prob))
        y_pred_all[val_idx] = y_prob

    print(f"=== {cv}-Fold Cross-Validation ===")
    print(f"  AUC:   {np.mean(aucs):.4f} +/- {np.std(aucs):.4f}")
    print(f"  Brier: {np.mean(briers):.4f} +/- {np.std(briers):.4f}")
    return {'mean_auc': np.mean(aucs), 'std_auc': np.std(aucs),
            'y_pred': y_pred_all, 'fold_aucs': aucs}


def bootstrap_validation(X_train, y_train, X_test, y_test, model, n_boot=200):
    """Bootstrap 0.632+ validation for small datasets.

    Output: optimism-corrected AUC
    """
    from sklearn.utils import resample

    # Apparent performance
    model.fit(X_train, y_train)
    apparent_auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])

    optimisms = []
    for i in range(n_boot):
        idx = resample(range(len(y_train)), random_state=i)
        oob_idx = list(set(range(len(y_train))) - set(idx))
        if len(oob_idx) < 5:
            continue
        X_boot, y_boot = X_train[idx], y_train[idx]
        X_oob, y_oob = X_train[oob_idx], y_train[oob_idx]

        m = type(model)(**model.get_params())
        m.fit(X_boot, y_boot)
        boot_auc = roc_auc_score(y_boot, m.predict_proba(X_boot)[:, 1])
        oob_auc = roc_auc_score(y_oob, m.predict_proba(X_oob)[:, 1])
        optimisms.append(boot_auc - oob_auc)

    optimism = np.mean(optimisms)
    corrected_auc = apparent_auc - optimism
    print(f"=== Bootstrap Validation (n={n_boot}) ===")
    print(f"  Apparent AUC:  {apparent_auc:.4f}")
    print(f"  Optimism:      {optimism:.4f}")
    print(f"  Corrected AUC: {corrected_auc:.4f}")
    return {'apparent': apparent_auc, 'optimism': optimism, 'corrected': corrected_auc}


def plot_roc_curves(y_test, results_dict):
    """Plot ROC curves for all models.

    Output: matplotlib Figure with ROC curves
    """
    fig, ax = plt.subplots(1, 1, figsize=(7, 6))
    for name, res in results_dict.items():
        fpr, tpr, _ = roc_curve(y_test, res['y_prob'])
        ax.plot(fpr, tpr, label=f"{name} (AUC={res['auc']:.3f})")
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.5)
    ax.set_xlabel('1 - Specificity (FPR)')
    ax.set_ylabel('Sensitivity (TPR)')
    ax.set_title('ROC Curves — Model Comparison')
    ax.legend(loc='lower right')
    plt.tight_layout()
    return fig


def plot_calibration(y_test, results_dict, n_bins=10):
    """Plot calibration curves for all models.

    Output: matplotlib Figure with calibration plots
    """
    fig, ax = plt.subplots(1, 1, figsize=(7, 6))
    for name, res in results_dict.items():
        prob_true, prob_pred = calibration_curve(y_test, res['y_prob'], n_bins=n_bins)
        ax.plot(prob_pred, prob_true, marker='o', label=name)
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Perfect')
    ax.set_xlabel('Predicted Probability')
    ax.set_ylabel('Observed Frequency')
    ax.set_title('Calibration Plot')
    ax.legend()
    plt.tight_layout()
    return fig


def decision_curve_analysis(y_test, y_prob, thresholds=np.arange(0.01, 0.99, 0.01)):
    """Decision Curve Analysis — net benefit across threshold probabilities.

    Output: DCA plot (treat all, treat none, model)
    """
    n = len(y_test)
    prevalence = y_test.mean()
    net_benefit_model, net_benefit_all = [], []

    for pt in thresholds:
        tp = ((y_prob >= pt) & (y_test == 1)).sum()
        fp = ((y_prob >= pt) & (y_test == 0)).sum()
        nb = tp / n - fp / n * pt / (1 - pt)
        net_benefit_model.append(nb)
        nb_all = prevalence - (1 - prevalence) * pt / (1 - pt)
        net_benefit_all.append(nb_all)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(thresholds, net_benefit_model, label='Model', color='blue')
    ax.plot(thresholds, net_benefit_all, label='Treat All', color='gray', linestyle='--')
    ax.axhline(y=0, color='black', linestyle=':', label='Treat None')
    ax.set_xlabel('Threshold Probability')
    ax.set_ylabel('Net Benefit')
    ax.set_title('Decision Curve Analysis')
    ax.legend()
    ax.set_xlim([0, 1])
    ax.set_ylim([-0.05, max(net_benefit_model) * 1.2])
    plt.tight_layout()
    return fig


def shap_explanation(model, X_test, feature_names):
    """SHAP-based model explanation.

    Output: SHAP summary plot + feature importance table
    """
    import shap

    if hasattr(model, 'predict_proba'):
        explainer = shap.Explainer(model, feature_names=feature_names)
    else:
        explainer = shap.KernelExplainer(model.predict_proba, X_test[:100])

    shap_values = explainer(X_test)

    fig_summary = plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X_test, feature_names=feature_names, show=False)
    plt.tight_layout()

    # Feature importance table
    mean_abs_shap = np.abs(shap_values.values).mean(axis=0)
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'mean_abs_shap': mean_abs_shap
    }).sort_values('mean_abs_shap', ascending=False)

    print("=== SHAP Feature Importance ===")
    print(importance_df.to_string(index=False))
    return importance_df, fig_summary


# ============================================================
# FULL PIPELINE
# ============================================================
def run_ml_pipeline(df, target_col, feature_cols, site_col=None):
    """End-to-end ML clinical prediction model pipeline.

    Input:
        df: DataFrame with all data
        target_col: str, outcome column
        feature_cols: list[str], predictor columns
        site_col: str, optional — if provided, use as external validation split

    Output:
        best_model: fitted model
        results: dict with all metrics
        figures: list of (name, Figure)
    """
    figures = []

    # 1. Split
    if site_col:
        sites = df[site_col].unique()
        train_site, test_site = sites[:-1], sites[-1]
        train_df = df[df[site_col].isin(train_site)]
        test_df = df[df[site_col] == test_site]
        X_train = train_df[feature_cols].values
        X_test = test_df[feature_cols].values
        y_train = train_df[target_col].values
        y_test = test_df[target_col].values
        print(f"External validation: train sites={list(train_site)}, test site={test_site}")
    else:
        X_train, X_test, y_train, y_test, prep = preprocess_data(
            df, feature_cols, target_col
        )

    # 2. Train & compare
    print("\n=== Model Comparison ===")
    results, models = train_multiple_models(X_train, y_train, X_test, y_test)

    # 3. ROC curves
    figures.append(('roc', plot_roc_curves(y_test, results)))

    # 4. Calibration
    figures.append(('calibration', plot_calibration(y_test, results)))

    # 5. Best model
    best_name = max(results, key=lambda k: results[k]['auc'])
    best_model = models[best_name]
    best_prob = results[best_name]['y_prob']
    print(f"\nBest model: {best_name} (AUC={results[best_name]['auc']:.4f})")

    # 6. DCA
    figures.append(('dca', decision_curve_analysis(y_test, best_prob)))

    # 7. Bootstrap validation
    boot = bootstrap_validation(X_train, y_train, X_test, y_test, best_model)

    # 8. Classification report at optimal threshold
    from sklearn.metrics import f1_score
    fpr, tpr, thresholds = roc_curve(y_test, best_prob)
    youden = tpr - fpr
    optimal_idx = np.argmax(youden)
    optimal_threshold = thresholds[optimal_idx]
    y_pred = (best_prob >= optimal_threshold).astype(int)

    print(f"\n=== Optimal Threshold (Youden): {optimal_threshold:.3f} ===")
    print(classification_report(y_test, y_pred, target_names=['Negative', 'Positive']))

    return best_model, results, figures
```

### 11. Radiomics-Specific Pipeline

```python
# Requires: pip install pyradiomics
def radiomics_pipeline(image_paths, mask_paths, clinical_df, target_col):
    """Extract radiomics features and build prediction model.

    Input:
        image_paths: list of image file paths (NIFTI/DICOM)
        mask_paths: list of corresponding segmentation masks
        clinical_df: DataFrame with clinical variables and target
        target_col: str
    Output:
        Combined clinical + radiomics model
    """
    import radiomics
    from radiomics import featureextractor

    # Feature extraction
    extractor = featureextractor.RadiomicsFeatureExtractor()
    extractor.enableAllFeatures()

    features_list = []
    for img, mask in zip(image_paths, mask_paths):
        result = extractor.execute(img, mask)
        features = {k: v for k, v in result.items()
                    if not k.startswith('diagnostics_')}
        features_list.append(features)

    radio_df = pd.DataFrame(features_list)

    # ICC filtering (if repeat scans available)
    # Keep features with ICC > 0.8

    # mRMR or LASSO feature selection
    # ... (use feature_selection_lasso from above)

    # Combine with clinical features
    # combined_df = pd.concat([clinical_df, radio_df], axis=1)
    # ... run_ml_pipeline(combined_df, target_col, feature_cols)
    return radio_df
```

## Output
- Model comparison table (AUC, Brier score per model)
- ROC curves (all models overlaid)
- Calibration plot
- Decision Curve Analysis
- SHAP feature importance (global + local)
- Bootstrap-corrected AUC
- Optimal threshold with sensitivity/specificity/PPV/NPV
- TRIPOD checklist compliance
- Complete executable Python pipeline
