# Clinical Research Harness

A plug-and-play clinical research toolkit that works across
[Claude Code](https://docs.anthropic.com/en/docs/claude-code),
[Cursor](https://cursor.sh), and [Codex CLI](https://github.com/openai/codex).
Clone this repo and get **20 specialized skills** covering the full lifecycle
of a clinical study — from PICO framing to statistical analysis to manuscript
reporting.

## Quick Start

```bash
# 1. Clone
git clone https://github.com/vuno-rnd/clinical-research-harness.git
cd clinical-research-harness

# 2. (Optional) Set PubMed API key for literature search
export NCBI_API_KEY="your-key-here"

# 3. Open Claude Code
claude

# 4. Use any skill
# /pico-extract HCM patients treated with mavacamten vs placebo, 24-week peak VO2 change
# /stat-rct continuous primary endpoint, MMRM, 24-week multicenter trial
# /stat-ml-model binary classification, HCM diagnosis from ECG features
```

## How It Works

All 20 clinical skills live in `skills/<name>/SKILL.md` (single source of
truth). Each supported tool is wired to the same files:

| Tool | Entry point | Skill discovery |
|------|-------------|-----------------|
| **Claude Code** | `CLAUDE.md` + `.claude/settings.json` | `.claude/skills/` symlinks to `skills/` — invoke as `/skill-name` |
| **Cursor** | `.cursor/rules/*.mdc` + `.cursor/mcp.json` | `.cursor/rules/skills-index.mdc` catalogs all skills — reference via `@skills/<name>/SKILL.md` |
| **Codex CLI** | `AGENTS.md` | Skills catalog embedded in `AGENTS.md` — read `skills/<name>/SKILL.md` as needed |

Shared assets:
- `CLAUDE.md` / `AGENTS.md` — system instructions (auto-loaded by the tool)
- `skills/` — 20 portable skill playbooks, each with input spec, method selection, template code, output spec
- `subagents/` — specialized agent definitions (statistician, reviewer, protocol checker)
- `.claude/settings.json` — PubMed MCP server + Claude Code quality-reminder hooks

No installation, no dependencies. Just `git clone` and start your tool of choice.

## Skill Catalog (20 Commands)

### Research Planning

| Command | Description |
|---------|-------------|
| `/pico-extract` | Extract PICO/PICOS elements from a research question |
| `/pubmed-search` | Structured PubMed literature search with MeSH terms |
| `/study-design` | Recommend and justify a study design |
| `/sample-size` | Calculate sample size (continuous, binary, time-to-event, NI) |
| `/protocol-review` | Review protocol for SPIRIT compliance and regulatory gaps |

### Study-Design-Based Analysis

| Command | Description |
|---------|-------------|
| `/stat-rct` | RCT analysis: ITT, ANCOVA, MMRM, multiplicity, missing data |
| `/stat-cohort` | Cohort study: RR, IRR, HR, propensity score, bias mitigation |
| `/stat-case-control` | Case-control: OR, conditional logistic, Mantel-Haenszel, dose-response |
| `/stat-diagnostic` | Diagnostic accuracy: Se/Sp, ROC/AUC, DCA, calibration, STARD |
| `/stat-survival` | Survival: Kaplan-Meier, Cox, RMST, competing risks, parametric models |

### Advanced Statistical Methods

| Command | Description | Key Techniques |
|---------|-------------|----------------|
| `/stat-propensity` | Causal inference for observational data | PSM, IPTW, AIPW, E-value, balance diagnostics |
| `/stat-ml-model` | ML clinical prediction models (TRIPOD) | RF, XGBoost, SVM, SHAP, radiomics, bootstrap validation |
| `/stat-longitudinal` | Repeated measures / longitudinal data | MMRM, LMM, GLMM, GEE, covariance selection |
| `/stat-bayesian` | Bayesian clinical trial analysis | PyMC, priors, CrI, P(benefit), MCMC diagnostics |
| `/stat-mediation` | Mediation and interaction analysis | ACME, Baron-Kenny, subgroup forest plots |
| `/stat-omics` | Multi-omics and bioinformatics | DESeq2, WGCNA, GSEA, Mendelian randomization, OPLS-DA |

### Evidence Synthesis

| Command | Description |
|---------|-------------|
| `/systematic-review` | PRISMA 2020 systematic review protocol |
| `/meta-analysis` | Fixed/random effects, heterogeneity, publication bias, NMA |

### Quality Assurance

| Command | Description |
|---------|-------------|
| `/bias-assessment` | Risk of bias: RoB 2, ROBINS-I, QUADAS-2, Newcastle-Ottawa |
| `/reporting-checklist` | CONSORT, STROBE, STARD, PRISMA, TRIPOD checklists |

## Each Skill Provides

Every statistical skill follows a standardized structure:

```
1. Input specification    — exact DataFrame format, column names, parameter types
2. Method selection guide — decision table for choosing the right technique
3. Step-by-step procedure — assumption checks, model fitting, diagnostics
4. Template Python code   — modular functions, immediately executable
5. Full pipeline function — run_*_pipeline() for end-to-end analysis
6. Output specification   — result tables, plots, clinical interpretation
```

### Example: `/stat-propensity`

```
Input:  DataFrame with treatment (0/1), outcome, covariates
        method='iptw', outcome_type='survival'

Output: - PS distribution overlap plot
        - Balance table (SMD < 0.1 check)
        - Love plot
        - Weighted Cox HR with robust CI
        - E-value for unmeasured confounding
        - Complete Python pipeline code
```

## Architecture

```
clinical-research-harness/
├── CLAUDE.md                      # Claude Code system prompt + skill selection
├── AGENTS.md                      # Codex CLI system prompt + skill catalog
├── skills/                        # ★ Portable skills (single source of truth)
│   ├── pico-extract/SKILL.md
│   ├── pubmed-search/SKILL.md
│   ├── study-design/SKILL.md
│   ├── sample-size/SKILL.md
│   ├── protocol-review/SKILL.md
│   ├── stat-rct/SKILL.md
│   ├── stat-cohort/SKILL.md
│   ├── stat-case-control/SKILL.md
│   ├── stat-diagnostic/SKILL.md
│   ├── stat-survival/SKILL.md
│   ├── stat-propensity/SKILL.md       # Causal inference
│   ├── stat-ml-model/SKILL.md         # ML prediction models
│   ├── stat-longitudinal/SKILL.md     # Mixed models / MMRM
│   ├── stat-bayesian/SKILL.md         # Bayesian analysis
│   ├── stat-mediation/SKILL.md        # Mediation & interaction
│   ├── stat-omics/SKILL.md            # Multi-omics / bioinformatics
│   ├── meta-analysis/SKILL.md
│   ├── systematic-review/SKILL.md
│   ├── bias-assessment/SKILL.md
│   └── reporting-checklist/SKILL.md
├── .claude/
│   ├── skills/ → ../skills            # symlink so Claude Code auto-loads skills
│   └── settings.json                  # MCP servers + hooks
├── .cursor/                            # Cursor IDE support
│   ├── mcp.json
│   └── rules/
│       ├── clinical-research.mdc
│       ├── statistics.mdc
│       └── skills-index.mdc           # catalog of all skills for Cursor
├── subagents/                          # Specialized agent definitions
│   ├── statistician.md
│   ├── literature-reviewer.md
│   └── protocol-checker.md
├── scripts/
│   └── convert-commands-to-skills.sh  # legacy commands → skills migration
└── examples/                           # Example outputs
    └── HCM_literature_review.md
```

## Workflow: From Data to Paper

```
Research Question
    │
    ├── /pico-extract          → PICO framework
    ├── /pubmed-search         → Prior evidence
    ├── /study-design          → Design selection
    ├── /sample-size           → Power calculation
    │
    ├── Statistical Analysis (pick one or combine):
    │   ├── /stat-rct              → RCT primary analysis
    │   ├── /stat-cohort           → Observational study
    │   ├── /stat-propensity       → Causal inference
    │   ├── /stat-ml-model         → Prediction model
    │   ├── /stat-longitudinal     → Repeated measures
    │   ├── /stat-bayesian         → Bayesian approach
    │   ├── /stat-mediation        → Mediation / subgroups
    │   ├── /stat-omics            → Genomics / metabolomics
    │   ├── /stat-survival         → Time-to-event
    │   ├── /stat-diagnostic       → Diagnostic accuracy
    │   ├── /stat-case-control     → Case-control
    │   └── /meta-analysis         → Evidence synthesis
    │
    ├── /bias-assessment       → Risk of bias evaluation
    └── /reporting-checklist   → CONSORT/STROBE/STARD/PRISMA/TRIPOD
```

## Python Dependencies

The template code in skills uses these packages. Install as needed:

```bash
# Core statistics
pip install numpy pandas scipy statsmodels lifelines

# ML / prediction models
pip install scikit-learn xgboost lightgbm shap

# Bayesian
pip install pymc arviz

# Omics
pip install pydeseq2 gseapy

# Radiomics (optional)
pip install pyradiomics

# Visualization
pip install matplotlib seaborn
```

## Tool Support

### Claude Code
Clone the repo and run `claude`. All 20 skills are auto-discovered via
`.claude/skills/` (symlinked to `skills/`). Invoke directly as
`/pubmed-search`, `/stat-rct`, etc.

### Cursor
`.cursor/rules/clinical-research.mdc` and `statistics.mdc` activate
automatically. `.cursor/rules/skills-index.mdc` catalogs all 20 skills
and tells Cursor when to use each. Reference a skill in chat with
`@skills/<name>/SKILL.md`. `.cursor/mcp.json` configures the PubMed MCP
server.

### Codex CLI
`AGENTS.md` is auto-loaded and contains the skill catalog plus detailed
statistical method reference. Codex does not auto-invoke skills — when
a task matches, read the relevant `skills/<name>/SKILL.md` into context.
PubMed MCP is not supported in Codex CLI; use direct API calls or the
web equivalent for literature search.

## PubMed Integration

The harness includes a PubMed MCP server for real-time literature search. To enable:

1. Get a free API key from [NCBI](https://www.ncbi.nlm.nih.gov/account/settings/)
2. Set the environment variable:
   ```bash
   export NCBI_API_KEY="your-key-here"
   ```
3. The PubMed server starts automatically when Claude Code launches in this repo

Without the API key, PubMed commands will still work but may be rate-limited.

## Reporting Guidelines Coverage

| Guideline | Study Type | Skill |
|-----------|-----------|-------|
| CONSORT | RCT | `/reporting-checklist`, `/stat-rct` |
| STROBE | Observational | `/reporting-checklist`, `/stat-cohort` |
| STARD | Diagnostic | `/reporting-checklist`, `/stat-diagnostic` |
| PRISMA | Systematic Review | `/systematic-review`, `/meta-analysis` |
| TRIPOD (+AI) | Prediction Model | `/reporting-checklist`, `/stat-ml-model` |
| STROBE-MR | Mendelian Randomization | `/stat-omics` |
| ROBUST | Bayesian | `/stat-bayesian` |

## Contributing

1. Add new skills as `skills/<name>/SKILL.md` with YAML frontmatter:
   ```
   ---
   name: <skill-name>
   description: <one-line summary — shown to all tools for dispatch>
   ---
   ```
2. Follow the existing skill format (see any `skills/stat-*/SKILL.md` as template)
3. Include: Input spec, method selection table, Python template code, output spec
4. Update the skill catalog in `CLAUDE.md`, `AGENTS.md`, and `.cursor/rules/skills-index.mdc`

## License

Apache 2.0
