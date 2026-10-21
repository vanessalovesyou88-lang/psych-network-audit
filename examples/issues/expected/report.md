# Network export audit

Findings apply only to supplied files; absence of errors is not scientific validation.

- **ERROR / EI_MISMATCH**: A: reported=0.9; computed=0.1; tolerance=0.001.
- **REVIEW / N_DIFFERS**: Stage sample sizes differ: {'network': 120, 'report': 118}. Explain exclusions/missingness; difference is not automatically an error.
- **REVIEW / CAUSAL_WORDING**: draft.txt:1: The cross-sectional network proves that B causes change in C.
- **INFO / SCOPE**: Checked supplied exports only. Raw signed one-step EI/BEI, all nodes included. No model refit, z scores, normalized/two-step centrality, stability validation or causal certification. Wording matches require human review, including negations.
