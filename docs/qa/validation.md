# Data integrity green gate

**[Evidence workflow](../physics/EVIDENCE-WORKFLOW.md) · [Research data](../../data/README.md)**

<img src="../../assets/phasegate-research-pipeline.svg" width="100%" alt="What the automated checks do and do not establish"/>

> **Visual guide:** Passing CI verifies links, files and registry structure; it does not validate experimental authenticity, instrument calibration or a scientific breakthrough.

---

This project uses only Python 3.12 standard library for automated checks; no paid services, API keys, external Python packages or AI tokens are required to run validation.

Local commands:
1. python tools/validate_research.py
2. python -m unittest discover -s tests -v
3. python tools/research_summary.py

GitHub Actions runs validation on research branch and PR pushes; it writes a dashboard to Actions step summary. GitHub-hosted Actions usage may count against the account's included Actions minutes (check account quotas). A passing green check means identifiers/links/record shapes passed automated rules. It does NOT demonstrate physical feasibility, data authenticity, experiment safety or real-world success. Reviews remain necessary.
