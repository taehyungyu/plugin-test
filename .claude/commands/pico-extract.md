Extract PICO/PICOS elements from a clinical research question or study description.

User input: $ARGUMENTS

## Instructions

1. **Identify and extract each PICO(S) element**:

   - **P (Population)**: Who are the patients/participants? Age, sex, condition, setting, severity
   - **I (Intervention)**: What is the treatment, exposure, or diagnostic test?
   - **C (Comparison)**: What is the control/comparator? (placebo, standard care, no treatment, alternative)
   - **O (Outcome)**: What outcomes are measured? Primary and secondary
   - **S (Study design)**: What study design is implied or appropriate?

2. **Refine each element**:
   - Make Population criteria specific and measurable
   - Distinguish Intervention details (dose, duration, route)
   - Clarify if Comparison is active vs. passive
   - Classify Outcomes by type (efficacy, safety, PRO, biomarker)

3. **Generate a structured search query** from PICO:
   - Map each element to MeSH terms + free-text synonyms
   - Provide a PubMed-ready search string

4. **Identify potential issues**:
   - Is the question too broad or too narrow?
   - Are outcomes measurable and clinically relevant?
   - Is the comparison group appropriate?

## Output Format

```
Population:    [specific description]
Intervention:  [specific description]
Comparison:    [specific description]
Outcome:       [primary] / [secondary]
Study Design:  [recommended type]

PubMed Query:  (P terms) AND (I terms) AND (C terms) AND (O terms)
```
