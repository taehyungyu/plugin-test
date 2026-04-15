---
name: reporting-checklist
description: Generate a reporting guideline checklist for a clinical study manuscript.
---

User input: {{input}}

## Instructions

### 1. Identify the Appropriate Guideline

| Study Type | Guideline | Items |
|---|---|---|
| RCT | CONSORT 2010 | 25 items |
| Observational (cohort, case-control, cross-sectional) | STROBE | 22 items |
| Diagnostic accuracy | STARD 2015 | 30 items |
| Systematic review / meta-analysis | PRISMA 2020 | 27 items |
| Prediction model (development) | TRIPOD | 22 items |
| Prediction model (validation) | TRIPOD | 22 items (subset) |
| Quality improvement | SQUIRE 2.0 | 18 items |
| Case report | CARE | 13 items |
| Animal research | ARRIVE 2.0 | 21 items |
| Economic evaluation | CHEERS 2022 | 28 items |
| Non-inferiority/equivalence RCT | CONSORT extension | Additional items |
| Cluster RCT | CONSORT extension | Additional items |
| Stepped-wedge RCT | CONSORT extension | Additional items |
| Network meta-analysis | PRISMA-NMA | Additional items |
| AI/ML clinical studies | CONSORT-AI / SPIRIT-AI | Additional items |

### 2. Generate Interactive Checklist

For each item in the selected guideline, provide:
- **Item number and topic**
- **What to report** (brief description)
- **Section** where it typically appears (Title, Abstract, Methods, Results, Discussion)
- **Status**: [ ] Not addressed / [~] Partially addressed / [x] Fully addressed
- **Location**: page/paragraph number in manuscript (to be filled)

### 3. Common Deficiencies to Flag

**CONSORT**: randomization details, allocation concealment, ITT statement, CONSORT flow diagram, trial registration
**STROBE**: participation flow, handling of confounders, missing data description, sensitivity analyses
**STARD**: index test details, reference standard, cross-tabulation (2x2), STARD flow diagram
**PRISMA**: protocol registration, search strategy (full), risk of bias per study, certainty of evidence
**TRIPOD**: model development details, predictor selection, handling of missing data, calibration, discrimination

### 4. Extensions & Add-ons
Flag if additional reporting standards apply:
- **Abstract reporting**: structured abstract checklist
- **Protocol**: SPIRIT (for RCT), PRISMA-P (for SR)
- **Patient-reported outcomes**: SISAQOL, ISOQOL guidelines
- **Harms/adverse events**: CONSORT harms extension
- **AI/ML**: CONSORT-AI, STARD-AI, TRIPOD-AI, DECIDE-AI

### 5. Output Format

```markdown
# [GUIDELINE] Checklist for: [Study Title]

## Title and Abstract
- [ ] Item 1a: Title — Identification as [study type]
  - Guideline: [what to report]
  - Status: [Not addressed / Partially / Fully]
  - Location: Page __, Para __

## Introduction
- [ ] Item 2a: ...

## Methods
...

## Compliance Summary
- Fully addressed: __/__ items
- Partially addressed: __/__ items
- Not addressed: __/__ items
- Priority items to address: [list]
```

## Output
- Complete checklist for the identified guideline
- Compliance summary with gaps highlighted
- Priority items to address before submission
