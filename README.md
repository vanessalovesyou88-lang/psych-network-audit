# Psych Network Audit

**Offline checks for psychological network-analysis exports.** Version 0.1.0.

Check exported results for numerical and structural inconsistencies, then flag interpretation wording for human review. Includes an optional AI agent skill. Requires **Python 3.10+**, with no third-party Python dependencies or API key.

## Features

- Validate matrix dimensions, node labels and order, symmetry, zero diagonals, and finite weights.
- Recompute raw, signed, one-step Expected Influence (EI) and Bridge Expected Influence (BEI), and compare them with reported values.
- Flag differences in recorded sample sizes and undocumented missing-data handling.
- Screen English and Chinese text for wording that may require causal-interpretation review.
- Export findings as Markdown and JSON with node or line evidence where available.

## Quick start

Run from the repository root:

```bash
python skills/audit-psych-network/scripts/audit.py examples/clean --out audit-output/clean
python skills/audit-psych-network/scripts/audit.py examples/issues --out audit-output/issues
python -m unittest discover -s tests -v
```

Open `audit-output/clean/report.md` or `audit-output/issues/report.md` to read the results. JSON versions are also generated.

The `issues` example intentionally contains an incorrect EI value, differing recorded sample sizes, and causal wording. Its exit code of **1** is expected. The clean example returns **0**. Both examples use entirely synthetic data; expected reports are included in their `expected` folders.

## Audit your own exports

Copy `examples/clean` to a local folder named `private-input`, replace its contents with your exports, and run:

```bash
python skills/audit-psych-network/scripts/audit.py private-input --out audit-output/my-audit
```

Keep participant-level data and confidential reports out of public repositories. The included `.gitignore` excludes `private-input/` and `audit-output/` from normal Git tracking; it does not protect files uploaded manually or already tracked.

### Input files

Use UTF-8 encoding. UTF-8 BOM is accepted for JSON and CSV inputs.

| File | Required | Format |
|---|---|---|
| `manifest.json` | Yes | Ordered unique `nodes`; node-to-community mapping in `communities`; positive integer `sample_sizes` by analysis stage; a `missing_data` description; optional absolute `tolerance` (default 0.001, allowed range 0 to 0.01). |
| `adjacency.csv` | Yes | Square, undirected weighted adjacency matrix with row and column labels in exactly the same order as `nodes`. Use `node` in the first header cell and zero diagonal entries. |
| `centrality.csv` | No | Exact header: `node,EI,BEI`. One row per node. Supply raw, unstandardized, unnormalized, one-step values. |
| `draft.txt` | No | Plain-text manuscript excerpt for heuristic wording checks. |

The example folders provide complete input templates. Missing optional inputs are explicitly reported as skipped checks. BEI comparison requires a valid community label for every node and at least two communities.

### Supported metrics

For an adjacency matrix with signed weights `w`:

- `EI(i) = sum of w(i,j) over all j`.
- `BEI(i) = sum of w(i,j) over j in communities other than the community of i`.

Negative edges retain their signs. All nodes are included. Community assignments must match the original analysis. Export sufficient precision (preferably at least six decimal places) and use the same adjacency matrix as the reported analysis. Structural symmetry and diagonal checks use a tolerance of 1e-8; the configurable tolerance applies to centrality comparisons.

Do not supply a correlation matrix, standardized centrality scores, absolute-value strength, normalized BEI, or two-step BEI.

## Understanding the report

| Level | Meaning |
|---|---|
| `ERROR` | Invalid input or a deterministic inconsistency within the supplied exports. |
| `REVIEW` | A possible issue or skipped check requiring human judgment or additional information. |
| `INFO` | Scope and interpretation notes. |

The CLI returns 1 for reported errors and 0 otherwise. REVIEW findings do not trigger a failing exit code. Differing sample sizes can be legitimate; explain exclusions and missingness rather than assuming an error. Wording matches can include negations and quotations, so they are not automatic findings of causal overclaiming.

## Optional AI skill

The skill is in `skills/audit-psych-network`. Copy that entire folder to the skill directory used by your SKILL.md-compatible agent, or ask the agent to read its `SKILL.md` and follow the workflow. Installation paths depend on the agent. The standalone Python checker works without AI.

Example request:

> Use audit-psych-network to check private-input. Separate confirmed inconsistencies, items needing human review, and checks not performed. Do not modify the original analysis.

## Scope and limitations

This is an export-consistency tool, not a complete statistical audit. Version 0.1 does not refit networks, verify raw-data processing, read Word/PDF/RDS files, compare arbitrary manuscript statistics, or automatically validate bootstrap stability. Sample sizes are supplied records, not counts recomputed from raw data. Text screening uses keywords rather than contextual language understanding.

A report with no errors does not establish scientific validity or causal effects. The optional skill guides contextual review but does not replace methodological judgment. The tool has not undergone independent research validation.

## Upload to GitHub

Create a repository named `psych-network-audit`. Upload the files and folders inside this extracted project directory, preserving their structure. Upload the project contents rather than the ZIP archive. Alternatively, use Git to commit the project and push it to your repository.

The included `.github/workflows/tests.yml` runs the test suite on pushes and pull requests when GitHub Actions is enabled.

## Contributing

Bug reports and small, reproducible examples are welcome. Include your Python version, command, minimal synthetic or openly licensed inputs, expected behavior, and actual output. Add tests when introducing checks or fixing bugs. Do not post confidential research data in issues or pull requests.

## License

[MIT](LICENSE). All bundled examples are synthetic and unrelated to any real study.
