---
name: bias-assessment
description: Assess risk of bias for clinical studies using appropriate validated tools.
---

User input: {{input}}

## Instructions

### 1. Select the Appropriate Tool

| Study Design | Risk of Bias Tool | Domains |
|---|---|---|
| RCT | **RoB 2** (Cochrane) | Randomization, deviations, missing data, measurement, selection |
| Non-randomized intervention | **ROBINS-I** | Confounding, selection, classification, deviations, missing, measurement, reporting |
| Diagnostic accuracy | **QUADAS-2** | Patient selection, index test, reference standard, flow/timing |
| Prognostic studies | **QUIPS** | Participation, attrition, measurement, confounding, analysis |
| Prevalence studies | **JBI Critical Appraisal** | Sample, sampling, sample size, description, coverage, measurement, methods, response |
| Case reports/series | **JBI Case Report/Series** | Patient characteristics, timeline, clinical condition, interventions, outcomes |

### 2. RoB 2 (for RCTs)
Assess each domain with signaling questions:
1. **Randomization process**: sequence generation, allocation concealment, baseline balance
2. **Deviations from intended interventions**: blinding, adherence, appropriate analysis
3. **Missing outcome data**: proportion, reasons, evidence of impact
4. **Measurement of outcome**: blinding of assessors, appropriate method
5. **Selection of reported result**: pre-specified analysis plan, multiple measures/timepoints

Judgement per domain: **Low risk** / **Some concerns** / **High risk**
Overall: worst domain drives overall judgement (with nuance)

### 3. ROBINS-I (for observational studies)
Pre-intervention:
1. **Confounding**: all important confounders measured and controlled?
2. **Selection of participants**: selection into study related to intervention AND outcome?

At intervention:
3. **Classification of interventions**: well-defined, potential for misclassification?

Post-intervention:
4. **Deviations from intended interventions**: co-interventions, adherence
5. **Missing data**: proportion, differential by group
6. **Measurement of outcomes**: blinding, valid measurement
7. **Selection of reported result**: pre-specified, multiple analyses

Judgement: **Low** / **Moderate** / **Serious** / **Critical** / **No information**

### 4. QUADAS-2 (for diagnostic studies)
Each domain assessed for **risk of bias** AND **applicability concerns**:
1. **Patient selection**: consecutive/random sampling, case-control avoidance, exclusions
2. **Index test**: pre-specified threshold, blinding to reference standard
3. **Reference standard**: correct classification, blinding to index test
4. **Flow and timing**: appropriate interval, all patients receive reference, all included

### 5. Output Format

Generate a structured assessment table:

| Domain | Signaling Questions | Support for Judgement | Judgement |
|--------|--------------------|-----------------------|-----------|
| D1 | Q1: Yes, Q2: Yes | [explanation] | Low risk |
| ... | ... | ... | ... |

And a traffic-light summary figure description:
- Green (low risk), Yellow (some concerns/moderate), Red (high risk/serious/critical)

### 6. Across-Study Summary (for systematic reviews)
- Risk of bias summary figure (all studies × all domains)
- Risk of bias graph (proportion of low/some concerns/high per domain)
- GRADE downgrading decision based on risk of bias findings

## Output
- Selected tool with justification
- Domain-by-domain assessment with signaling questions answered
- Overall risk of bias judgement with rationale
- Recommendations for interpreting results given bias risk
