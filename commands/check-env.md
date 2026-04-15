---
description: "Dummy test command — checks required environment variables for MCP servers"
---

Check if the following environment variables are set and report their status:

1. `NCBI_API_KEY` — required for PubMed MCP server
2. `ARXIV_STORAGE_PATH` — optional for arXiv paper storage

Run `echo $NCBI_API_KEY | head -c 4` and `echo $ARXIV_STORAGE_PATH` to verify.
Do NOT print full API keys — show only first 4 characters.

User input: $ARGUMENTS
