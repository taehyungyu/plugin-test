---
name: pubmed-search
description: Perform a structured PubMed literature search for clinical research.
---

User query: {{input}}

## Instructions

1. **Parse the research question** into PICO components:
   - Population, Intervention, Comparison, Outcome

2. **Build a search strategy**:
   - Identify MeSH terms for each PICO element using the PubMed MCP `mesh_terms` tool
   - Combine MeSH terms with free-text synonyms using OR
   - Combine PICO blocks with AND
   - Apply appropriate filters (humans, language, date range, article type)

3. **Execute the search** using the PubMed MCP `search` tool

4. **Screen results**:
   - Fetch abstracts for the top 10-20 most relevant articles
   - Categorize by study design (SR/MA, RCT, cohort, case-control, etc.)
   - Note sample sizes and key findings

5. **Summarize findings** in a structured table:

| PMID | Author (Year) | Design | N | Key Finding |
|------|---------------|--------|---|-------------|

6. **Identify gaps**: What hasn't been studied? Where is evidence weak?

7. **Suggest next steps**: Additional searches, citation tracking, grey literature

## Output Format
- Search strategy (reproducible, can be pasted into PubMed)
- Results summary table
- Evidence gap analysis
- Recommended next search iterations
