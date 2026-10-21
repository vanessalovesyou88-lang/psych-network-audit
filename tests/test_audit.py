import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('audit', ROOT / 'skills/audit-psych-network/scripts/audit.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name) / 'input'
        shutil.copytree(ROOT / 'examples/clean', self.folder)

    def codes(self):
        return {r['code'] for r in module.audit(self.folder)}

    def test_clean_signed_values(self):
        self.assertEqual(self.codes(), {'SCOPE'})

    def test_known_issues(self):
        codes = {r['code'] for r in module.audit(ROOT / 'examples/issues')}
        self.assertEqual(codes, {'EI_MISMATCH', 'N_DIFFERS', 'CAUSAL_WORDING', 'SCOPE'})

    def test_reordered_labels(self):
        p = self.folder / 'adjacency.csv'
        p.write_text(p.read_text().replace('node,A,B,C', 'node,B,A,C'))
        self.assertEqual(self.codes(), {'LABEL_ORDER'})

    def test_nan_rejected(self):
        p = self.folder / 'adjacency.csv'
        p.write_text(p.read_text().replace('0.2', 'nan'))
        with self.assertRaises(ValueError):
            self.codes()

    def test_missing_optional_file(self):
        (self.folder / 'centrality.csv').unlink()
        self.assertIn('CENTRALITY_MISSING', self.codes())

    def test_asymmetric(self):
        p = self.folder / 'adjacency.csv'
        p.write_text(p.read_text().replace('A,0,0.2', 'A,0,0.3'))
        self.assertIn('ASYMMETRY', self.codes())

    def test_duplicate_centrality(self):
        (self.folder / 'centrality.csv').write_text('node,EI,BEI\nA,.1,-.1\nA,.1,-.1\nC,.2,.2\n')
        self.assertIn('CENTRALITY_NODES', self.codes())

    def test_missing_community(self):
        p = self.folder / 'manifest.json'
        cfg = json.loads(p.read_text())
        cfg['communities'].pop('A')
        p.write_text(json.dumps(cfg))
        self.assertIn('BEI_SKIPPED', self.codes())


if __name__ == '__main__':
    unittest.main()
