"""Keep the portable notebook in sync and execute it without repo file access."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import os
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_contact_center_notebook import build, source_only, TARGET


class NotebookTests(unittest.TestCase):
    def test_generated_sources_match(self):
        actual = json.loads(TARGET.read_text(encoding='utf-8'))
        self.assertEqual(source_only(actual), source_only(build()))

    def test_runs_without_repository_files(self):
        notebook = json.loads(TARGET.read_text(encoding='utf-8'))
        scope = {'__name__': '__main__'}
        output = io.StringIO()
        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                with contextlib.redirect_stdout(output):
                    for cell in notebook['cells']:
                        if cell['cell_type'] == 'code':
                            exec(compile(''.join(cell['source']), '<notebook>', 'exec'), scope)
            finally:
                os.chdir(original_cwd)
        self.assertEqual(scope['weighted_aht'], 450)
        self.assertEqual(scope['zero_imputed_aht'], 495)
        self.assertEqual(scope['incomplete']['fcr_pct'], 66.67)
        self.assertIn('All notebook assertions passed.', output.getvalue())


if __name__ == '__main__':
    unittest.main()
