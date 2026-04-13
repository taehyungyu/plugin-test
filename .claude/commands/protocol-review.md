Review a clinical study protocol for completeness, methodological rigor, and regulatory compliance.

User input: $ARGUMENTS

## Instructions

### 1. Protocol Structure Check (SPIRIT 2013)
Verify the protocol includes all essential sections:

**Administrative**:
- [ ] Protocol title with version number and date
- [ ] Trial registration (ClinicalTrials.gov, CRIS, etc.)
- [ ] Protocol contributors and sponsor
- [ ] Roles and responsibilities
- [ ] Funding source

**Introduction**:
- [ ] Background with literature review and rationale
- [ ] Objectives and hypotheses (specific, measurable)

**Methods: Participants, Interventions, Outcomes**:
- [ ] Study design description with framework (superiority/NI/equivalence)
- [ ] Study setting (sites, countries)
- [ ] Eligibility criteria (inclusion AND exclusion, justified)
- [ ] Intervention details (dose, duration, route, modifications allowed)
- [ ] Comparator justification
- [ ] Outcome definitions — primary and secondary with measurement method and timepoint
- [ ] Timeline of assessments (schedule of events table)
- [ ] Sample size calculation with all assumptions stated

**Methods: Assignment of Interventions**:
- [ ] Randomization: sequence generation, type, allocation ratio
- [ ] Allocation concealment mechanism
- [ ] Blinding: who is blinded, how unblinding works

**Methods: Data Collection & Management**:
- [ ] Data collection methods and instruments
- [ ] Data management plan
- [ ] Data quality assurance

**Methods: Statistical Methods**:
- [ ] Primary analysis method for primary endpoint
- [ ] Analysis populations (ITT, PP, safety)
- [ ] Missing data handling (with justification)
- [ ] Multiplicity adjustment (if applicable)
- [ ] Interim analysis plan and stopping rules
- [ ] Sensitivity analyses
- [ ] Subgroup analyses (pre-specified)

**Ethics & Dissemination**:
- [ ] IRB/Ethics approval (or plan)
- [ ] Informed consent process
- [ ] Confidentiality and data protection
- [ ] DSMB charter (if applicable)
- [ ] Publication policy

### 2. Methodological Quality Assessment

**Internal validity**:
- Appropriate randomization for the research question?
- Adequate allocation concealment?
- Blinding feasible and implemented?
- Primary endpoint objective or subjective (blinding importance)?
- ITT analysis planned as primary?

**Statistical rigor**:
- Sample size assumptions reasonable? (search PubMed for reference data)
- Effect size clinically meaningful (not just statistically)?
- Power adequate (≥80%)?
- Missing data strategy appropriate for mechanism?
- Multiplicity controlled?

**Feasibility**:
- Recruitment target realistic for sites/timeframe?
- Inclusion/exclusion criteria not too restrictive?
- Follow-up duration adequate for outcome?
- Dropout rate assumption realistic?

### 3. Regulatory Compliance Check

**ICH Guidelines**:
- [ ] E6(R2) GCP: consent, monitoring, safety reporting, data integrity
- [ ] E9(R1) Statistical Principles: estimand framework applied?
- [ ] E10 Choice of Control: control group justified?
- [ ] E17 Multi-Regional: consistency across regions (if applicable)?

**Jurisdiction-specific**:
- [ ] FDA: IND requirements, 21 CFR Part 312
- [ ] EMA: IMPD, CTA requirements
- [ ] MFDS (식약처): 임상시험계획승인 (IND), 의약품 임상시험 관리기준

### 4. Red Flags to Identify
- Vague primary endpoint definition
- Missing or unreferenced sample size assumptions
- No plan for missing data
- Inappropriate control group
- Unblinded outcome assessment for subjective endpoint
- No interim analysis for long/large trials
- No DSMB for high-risk interventions
- Multiple primary endpoints without multiplicity control
- Post-hoc subgroup analysis disguised as pre-specified

### 5. Estimand Framework (ICH E9 R1)
For each endpoint, verify:
- **Population**: who is targeted
- **Treatment**: what treatment condition
- **Variable**: what outcome measured
- **Population-level summary**: what statistical measure
- **Intercurrent events**: how handled (treatment policy, composite, hypothetical, principal stratum, while-on-treatment)

## Output
- Section-by-section completeness checklist
- Methodological concerns ranked by severity
- Regulatory compliance gaps
- Specific recommendations for improvement
- Priority items requiring revision before submission
