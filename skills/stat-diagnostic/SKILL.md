---
name: stat-diagnostic
description: Recommend and implement statistical analysis for a diagnostic accuracy study.
---

User input: {{input}}

## Instructions

### 1. Study Design Check (STARD)
- **Index test**: the diagnostic test being evaluated
- **Reference standard**: the gold standard for disease classification
- **Spectrum of disease**: severity range of included patients
- **Flow and timing**: interval between index test and reference standard
- **Blinding**: interpreters blinded to other test results?

### 2. Primary Accuracy Measures

| Measure | Formula | Interpretation |
|---------|---------|----------------|
| Sensitivity (Se) | TP / (TP + FN) | Ability to detect disease |
| Specificity (Sp) | TN / (TN + FP) | Ability to rule out disease |
| PPV | TP / (TP + FP) | Prob of disease given positive test |
| NPV | TN / (TN + FN) | Prob of no disease given negative test |
| LR+ | Se / (1 - Sp) | How much positive test increases odds |
| LR- | (1 - Se) / Sp | How much negative test decreases odds |
| DOR | (TP × TN) / (FP × FN) | Single accuracy summary |

- **95% CI** for all measures (Wilson score or Clopper-Pearson)
- PPV/NPV depend on prevalence — report at study prevalence AND clinically relevant prevalences

### 3. ROC Analysis
- **AUC (C-statistic)**: overall discriminative ability
- **DeLong test**: compare two ROC curves
- **Partial AUC**: focus on clinically relevant Se/Sp range
- **Optimal threshold**: Youden's index (Se + Sp - 1), or based on clinical cost-benefit

### 4. Calibration (for probability-producing models)
- **Calibration plot**: observed vs predicted probabilities
- **Hosmer-Lemeshow test**: goodness-of-fit (limited, use calibration plot instead)
- **Calibration slope and intercept**: slope = 1, intercept = 0 is ideal
- **Brier score**: combined measure of discrimination + calibration

### 5. Decision Curve Analysis (DCA)
- **Net benefit** at clinically relevant threshold probabilities
- Compare: treat all, treat none, model-guided
- Quantifies clinical utility beyond discrimination

### 6. Multi-threshold / Multi-test
- **Two-cutoff approach**: rule-in and rule-out thresholds
- **Sequential testing**: test A then test B — conditional accuracy
- **Head-to-head comparison**: paired design, McNemar's test for Se/Sp comparison

### 7. Special Considerations
- **Verification bias**: not all patients receive reference standard → correct with IPW
- **Spectrum bias**: narrow disease spectrum inflates accuracy
- **Clustering**: multiple lesions per patient → GEE or mixed models for CI
- **Imperfect reference**: latent class analysis if no gold standard

### 8. Code Template

```r
library(pROC); library(caret)

# ROC and AUC
roc1 <- roc(df$disease, df$test_score, ci = TRUE)
plot(roc1, print.auc = TRUE)
ci.auc(roc1)

# Compare two tests
roc2 <- roc(df$disease, df$test2_score)
roc.test(roc1, roc2, method = "delong")

# Optimal cutoff
coords(roc1, "best", ret = c("threshold", "sensitivity", "specificity", "ppv", "npv"))

# Confusion matrix at chosen threshold
pred <- ifelse(df$test_score > threshold, 1, 0)
confusionMatrix(factor(pred), factor(df$disease), positive = "1")
```

```python
from sklearn.metrics import roc_auc_score, roc_curve, classification_report
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt

fpr, tpr, thresholds = roc_curve(y_true, y_score)
auc = roc_auc_score(y_true, y_score)

# Calibration
prob_true, prob_pred = calibration_curve(y_true, y_score, n_bins=10)
plt.plot(prob_pred, prob_true, marker='o')
plt.plot([0,1],[0,1], '--')
```

## Output
- 2x2 table with all accuracy measures + CI
- ROC curve with AUC and optimal threshold
- Calibration assessment (if applicable)
- Clinical utility assessment (DCA)
- STARD checklist compliance
- Executable code
