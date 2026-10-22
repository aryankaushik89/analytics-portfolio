"""Check saved execution evidence and record the files reviewed for release."""

from pathlib import Path
from datetime import datetime
from datetime import timezone
import hashlib
import json
import platform
import numpy
import pandas
import scipy
import matplotlib

ROOT = Path(__file__).resolve().parents[1]
notebook = json.loads((ROOT / 'experiment_analysis.ipynb').read_text())
code_cells = [cell for cell in notebook['cells'] if cell['cell_type'] == 'code']
stdout = ''.join(''.join(output['text']) for cell in code_cells for output in cell['outputs']
                 if output['output_type'] == 'stream')
checks = pandas.read_csv(ROOT / 'outputs/data_checks.csv')
browser = json.loads((ROOT / 'outputs/browser_verification.json').read_text())
reproduction = json.loads((ROOT / 'outputs/reproducibility.json').read_text())

verified = {
    'all_structural_checks': bool(checks['passed'].all()),
    'eleven_cells_executed': len(code_cells) == 11 and all(cell['execution_count'] for cell in code_cells),
    'no_notebook_error_outputs': not any(output['output_type'] == 'error' for cell in code_cells for output in cell['outputs']),
    'notebook_script_stdout_equal': stdout == (ROOT / 'outputs/matching_script_run.txt').read_text(),
    'source_regeneration_byte_identical': reproduction['regeneration_byte_identical'],
    'python_tests': 'Ran 22 tests' in (ROOT / 'outputs/python_tests.txt').read_text() and '\nOK\n' in (ROOT / 'outputs/python_tests.txt').read_text(),
    'javascript_oracles': '54 filter selections' in (ROOT / 'outputs/dashboard_tests.txt').read_text(),
    'browser_verification': all(browser[key] for key in ['five_views', 'quality_gate_survives_filters',
        'summary_download_matches_filters_and_python', 'blocked_download_withholds_effect_and_money',
        'example_download_matches_search', 'html_analysis_readable']),
    'temporary_qa_page_removed': not (ROOT / 'dist/layout-check.html').exists(),
    'screenshot_present': (ROOT / 'docs/dashboard_overview.jpg').stat().st_size > 1000
}
print(pandas.DataFrame(verified.items(), columns=['release_check', 'passed']).to_string(index=False))
if not all(verified.values()):
    raise ValueError('Saved verification evidence does not support release.')

excluded = {'.git', '.openai', '__pycache__', '.pytest_cache', '.venv'}
files = []
for path in sorted(ROOT.rglob('*')):
    relative = path.relative_to(ROOT)
    if not path.is_file() or any(part in excluded for part in relative.parts):
        continue
    if relative.as_posix() == 'outputs/release_verification.json':
        continue
    files.append({'path': relative.as_posix(), 'bytes': path.stat().st_size,
                  'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
manifest = {'checked_at': datetime.now(timezone.utc).isoformat(), 'checks': verified,
            'versions': {'python': platform.python_version(), 'numpy': numpy.__version__,
                         'pandas': pandas.__version__, 'scipy': scipy.__version__,
                         'matplotlib': matplotlib.__version__},
            'files': files, 'public_exclusions': sorted(excluded),
            'limits': ['Synthetic experiments only; Criteo benchmark deferred.',
                       'Pointwise intervals and fixed financial assumptions.',
                       '390px iframe layout check, no mobile device hardware test.',
                       'Direct namespace notebook execution, no external Jupyter kernel.']}
(ROOT / 'outputs/release_verification.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(f'{len(files)} reviewed files; {sum(row["bytes"] for row in files):,} bytes.')
