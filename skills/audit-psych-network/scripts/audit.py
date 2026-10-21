"""Offline audit of exported undirected weighted networks. Python 3.10+."""
import argparse
import csv
import json
import math
import re
from pathlib import Path


def audit(folder):
    folder = Path(folder)
    findings = []
    def add(level, code, evidence):
        findings.append(dict(level=level, code=code, evidence=evidence))
    config = json.loads((folder / 'manifest.json').read_text(encoding='utf-8-sig'))
    nodes = config.get('nodes')
    if not isinstance(nodes, list) or not nodes or any(not isinstance(n, str) or not n for n in nodes) or len(set(nodes)) != len(nodes):
        raise ValueError('manifest.nodes must contain unique nonempty strings')
    tolerance = config.get('tolerance', 0.001)
    if isinstance(tolerance, bool) or not isinstance(tolerance, (float, int)) or not math.isfinite(tolerance) or not 0 <= tolerance <= 0.01:
        raise ValueError('tolerance must be finite and between 0 and 0.01')
    with (folder / 'adjacency.csv').open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))
    if len(rows) != len(nodes) + 1 or any(len(r) != len(nodes) + 1 for r in rows):
        raise ValueError('adjacency.csv must be square with row and column labels')
    if rows[0][1:] != nodes or [r[0] for r in rows[1:]] != nodes:
        add('ERROR', 'LABEL_ORDER', 'Matrix row/column labels must exactly match manifest.nodes; calculation skipped.')
        return findings
    matrix = [[float(x) for x in r[1:]] for r in rows[1:]]
    if any(not math.isfinite(x) for r in matrix for x in r):
        raise ValueError('Matrix contains non-finite weights')
    valid = True
    for i in range(len(nodes)):
        if abs(matrix[i][i]) > 1e-8:
            add('ERROR', 'DIAGONAL', f'{nodes[i]}: diagonal must be zero (supply adjacency, not correlation matrix).')
            valid = False
        for j in range(i):
            if abs(matrix[i][j] - matrix[j][i]) > 1e-8:
                add('ERROR', 'ASYMMETRY', f'{nodes[i]} / {nodes[j]}: unequal reciprocal weights.')
                valid = False
    groups = config.get('communities')
    if not isinstance(groups, dict) or set(groups) != set(nodes) or any(not isinstance(v, str) or not v for v in groups.values()) or len(set(groups.values())) < 2:
        groups = None
        add('REVIEW', 'BEI_SKIPPED', 'Provide a community string for every node and at least two communities.')
    centrality = folder / 'centrality.csv'
    if not centrality.exists():
        add('REVIEW', 'CENTRALITY_MISSING', 'No reported centrality file; EI/BEI comparison skipped.')
    elif valid:
        with centrality.open(encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != ['node', 'EI', 'BEI']:
                raise ValueError('centrality.csv header must be node,EI,BEI')
            records = list(reader)
        if len(records) != len(nodes) or {r['node'] for r in records} != set(nodes):
            add('ERROR', 'CENTRALITY_NODES', 'Missing, extra or duplicate centrality node.')
        else:
            lookup = {r['node']: r for r in records}
            for i, node in enumerate(nodes):
                expected = {'EI': sum(matrix[i])}
                if groups:
                    expected['BEI'] = sum(w for j, w in enumerate(matrix[i]) if groups[node] != groups[nodes[j]])
                for metric, value in expected.items():
                    reported = float(lookup[node][metric])
                    if not math.isfinite(reported):
                        raise ValueError(f'{node} {metric}: non-finite reported value')
                    if abs(reported - value) > tolerance + 1e-12:
                        add('ERROR', metric + '_MISMATCH', f'{node}: reported={reported:g}; computed={value:.8g}; tolerance={tolerance:g}.')
    stages = config.get('sample_sizes')
    if not isinstance(stages, dict) or not stages:
        add('REVIEW', 'N_MISSING', 'No sample-size records supplied.')
    else:
        if any(type(n) is not int or n <= 0 for n in stages.values()):
            raise ValueError('sample_sizes values must be positive integers')
        if len(set(stages.values())) > 1:
            add('REVIEW', 'N_DIFFERS', f'Stage sample sizes differ: {stages}. Explain exclusions/missingness; difference is not automatically an error.')
    if not isinstance(config.get('missing_data'), str) or not config['missing_data'].strip():
        add('REVIEW', 'MISSINGNESS_UNDOCUMENTED', 'Missing-data handling is not documented.')
    draft = folder / 'draft.txt'
    if draft.exists():
        pattern = r'导致|因果|证明|最有效|caus\w*|prov(?:e|es|en)|most effective'
        for number, line in enumerate(draft.read_text(encoding='utf-8-sig').splitlines(), 1):
            if re.search(pattern, line, re.I):
                add('REVIEW', 'CAUSAL_WORDING', f'draft.txt:{number}: {line.strip()}')
    else:
        add('REVIEW', 'DRAFT_MISSING', 'No draft.txt supplied; wording screen skipped.')
    add('INFO', 'SCOPE', 'Checked supplied exports only. Raw signed one-step EI/BEI, all nodes included. No model refit, z scores, normalized/two-step centrality, stability validation or causal certification. Wording matches require human review, including negations.')
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    parser.add_argument('--out', type=Path, default=Path('audit-output'))
    args = parser.parse_args()
    try:
        findings = audit(args.folder)
    except (ValueError, OSError, TypeError, KeyError, csv.Error) as exc:
        findings = [dict(level='ERROR', code='INPUT_INVALID', evidence=str(exc))]
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'report.json').write_text(json.dumps(findings, ensure_ascii=False, indent=2), encoding='utf-8')
    lines = ['# Network export audit', '', 'Findings apply only to supplied files; absence of errors is not scientific validation.', '']
    lines += [f"- **{r['level']} / {r['code']}**: {r['evidence']}" for r in findings]
    (args.out / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    errors = sum(r['level'] == 'ERROR' for r in findings)
    print(f'{errors} error(s); reports: {args.out.resolve()}')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
