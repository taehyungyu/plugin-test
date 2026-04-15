# Clinical Research Harness

A Claude Code plugin for clinical research — 20 skills, 3 agents, PubMed MCP
integration. Install from a marketplace and get study design, biostatistics,
and manuscript reporting capabilities.

## Quick Start

```bash
# 1. Register the marketplace (once)
claude plugin marketplace add taehyungyu/plugin-test

# 2. Install the plugin
claude plugin install clinical-research-harness@vuno-rnd-marketplace

# 3. (Optional) PubMed API key for literature search
export NCBI_API_KEY="your-key-here"

# 4. Restart Claude Code and use
claude
# /pico-extract HCM patients treated with mavacamten vs placebo, 24-week peak VO2 change
# /stat-rct continuous primary endpoint, MMRM, 24-week multicenter trial
```

## What's Included

| Component | Count | Description |
|-----------|-------|-------------|
| Skills | 20 | `/skill-name` slash commands for the full research lifecycle |
| Agents | 3 | Statistician, literature reviewer, protocol checker |
| Hooks | 2 | Assumption-check reminders on `.py` writes, PubMed post-search hints |
| Commands | 2 | `/hello`, `/check-env` (test utilities) |
| MCP | 1 | PubMed server for real-time literature search |

## Plugin Structure

These are the files that ship in the plugin package. `.claude/` and `.cursor/`
are **not** included — they are IDE-local configs that users set up themselves.

```
clinical-research-harness/
├── .claude-plugin/
│   ├── plugin.json              # Plugin manifest (name, version, author)
│   └── marketplace.json         # Marketplace catalog (for self-hosting)
├── skills/                      # 20 portable skill playbooks
│   ├── pico-extract/SKILL.md
│   ├── pubmed-search/SKILL.md
│   ├── stat-rct/SKILL.md
│   ├── stat-cohort/SKILL.md
│   ├── stat-propensity/SKILL.md
│   ├── stat-ml-model/SKILL.md
│   ├── ...                      # (16 more skills)
│   └── reporting-checklist/SKILL.md
├── agents/                      # Specialized subagents
│   ├── statistician.md
│   ├── literature-reviewer.md
│   └── protocol-checker.md
├── commands/                    # Slash commands (legacy format)
│   ├── hello.md
│   └── check-env.md
├── hooks/
│   └── hooks.json               # PreToolUse + PostToolUse automation
├── .mcp.json                    # PubMed MCP server config
├── CLAUDE.md                    # System prompt (loaded by Claude Code)
├── AGENTS.md                    # System prompt (loaded by Codex CLI)
└── README.md
```

## Skill Catalog

### Research Planning

| Skill | Description |
|-------|-------------|
| `/pico-extract` | Extract PICO/PICOS elements from a research question |
| `/pubmed-search` | Structured PubMed literature search with MeSH terms |
| `/study-design` | Recommend and justify a study design |
| `/sample-size` | Calculate sample size (continuous, binary, time-to-event, NI) |
| `/protocol-review` | Review protocol for SPIRIT compliance and regulatory gaps |

### Study-Design-Based Analysis

| Skill | Description |
|-------|-------------|
| `/stat-rct` | RCT: ITT, ANCOVA, MMRM, multiplicity, missing data |
| `/stat-cohort` | Cohort: RR, IRR, HR, propensity score, bias mitigation |
| `/stat-case-control` | Case-control: OR, conditional logistic, Mantel-Haenszel |
| `/stat-diagnostic` | Diagnostic accuracy: Se/Sp, ROC/AUC, DCA, STARD |
| `/stat-survival` | Survival: Kaplan-Meier, Cox, RMST, competing risks |

### Advanced Statistical Methods

| Skill | Key Techniques |
|-------|----------------|
| `/stat-propensity` | PSM, IPTW, AIPW, E-value, balance diagnostics |
| `/stat-ml-model` | RF, XGBoost, SVM, SHAP, radiomics, TRIPOD validation |
| `/stat-longitudinal` | MMRM, LMM, GLMM, GEE, covariance selection |
| `/stat-bayesian` | PyMC, priors, CrI, P(benefit), MCMC diagnostics |
| `/stat-mediation` | ACME, Baron-Kenny, subgroup forest plots |
| `/stat-omics` | DESeq2, WGCNA, GSEA, Mendelian randomization, OPLS-DA |

### Evidence Synthesis

| Skill | Description |
|-------|-------------|
| `/systematic-review` | PRISMA 2020 systematic review protocol |
| `/meta-analysis` | Fixed/random effects, heterogeneity, publication bias, NMA |

### Quality Assurance

| Skill | Description |
|-------|-------------|
| `/bias-assessment` | RoB 2, ROBINS-I, QUADAS-2, Newcastle-Ottawa |
| `/reporting-checklist` | CONSORT, STROBE, STARD, PRISMA, TRIPOD checklists |

## Workflow

```
Research Question
    │
    ├── /pico-extract          → PICO framework
    ├── /pubmed-search         → Prior evidence
    ├── /study-design          → Design selection
    ├── /sample-size           → Power calculation
    │
    ├── Statistical Analysis (pick one or combine):
    │   ├── /stat-rct, /stat-cohort, /stat-case-control
    │   ├── /stat-survival, /stat-diagnostic
    │   ├── /stat-propensity, /stat-ml-model
    │   ├── /stat-longitudinal, /stat-bayesian
    │   ├── /stat-mediation, /stat-omics
    │   └── /meta-analysis
    │
    ├── /bias-assessment       → Risk of bias
    └── /reporting-checklist   → Guideline compliance
```

## PubMed Integration

The plugin includes a PubMed MCP server (`.mcp.json`). To enable:

1. Get a free API key from [NCBI](https://www.ncbi.nlm.nih.gov/account/settings/)
2. `export NCBI_API_KEY="your-key-here"`
3. The server starts automatically when Claude Code loads the plugin

Without the API key, PubMed access may be rate-limited.

## Plugin Management

```bash
# Update
claude plugin update clinical-research-harness@vuno-rnd-marketplace

# Disable / Enable
claude plugin disable clinical-research-harness@vuno-rnd-marketplace
claude plugin enable clinical-research-harness@vuno-rnd-marketplace

# Uninstall
claude plugin uninstall clinical-research-harness@vuno-rnd-marketplace
```

## Local Development

To test plugin changes locally without publishing:

```bash
git clone https://github.com/taehyungyu/plugin-test.git
cd plugin-test
claude --plugin-dir .
```

## Contributing

1. Add new skills as `skills/<name>/SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: <skill-name>
   description: <one-line summary>
   ---
   ```
2. Follow the existing skill format (see any `skills/stat-*/SKILL.md`)
3. Bump version in `.claude-plugin/plugin.json` and marketplace.json

## License

MIT
