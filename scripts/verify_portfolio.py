"""Verify mirrored pillars, navigation and unchanged academic artifacts offline."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--navigation-only', action='store_true', help='For partial local checkouts only; CI performs the full hash check.')
args = parser.parse_args()
structure = json.loads((ROOT / 'structure.json').read_text())
catalog = json.loads((ROOT / 'portfolio.json').read_text())
assert structure['pillars'] == ['personal', 'business', 'berkeley-education', 'control']
assert [x['path'] for x in catalog['pillars']] == structure['pillars']
assert [x['id'] for x in catalog['collections']] == structure['businessLines']
assert [x['path'] for x in catalog['collections']] == ['business/' + x for x in structure['businessLines']]
gaming = catalog['collections'][3]['projects']
assert [x['id'] for x in gaming] == ['third-strike', 'ddr', 'smash', 'game-development']
assert [x['id'] for x in gaming[2]['children']] == ['melee', 'ultimate']

def safe(value):
    p = Path(value)
    assert not p.is_absolute() and '..' not in p.parts, value
    resolved = (ROOT / p).resolve()
    assert resolved.is_relative_to(ROOT), value
    return resolved

def check(entry):
    assert (safe(entry['path']) / 'README.md').is_file(), entry['path']
    for child in entry.get('projects', []) + entry.get('children', []):
        check(child)

seen = set()
for entry in structure['paths']:
    assert entry['path'] not in seen, entry['path']
    seen.add(entry['path'])
    check(entry)
for entry in catalog['collections'] + catalog['shared'] + catalog['education']:
    check(entry)
for old, new in catalog['legacyPaths'].items():
    assert (safe(old) / 'README.md').is_file(), old
    assert (safe(new) / 'README.md').is_file(), new
manifest = json.loads((ROOT / 'berkeley-education/import-manifest.json').read_text())
immutable = set()
count = 0
for project in manifest['projects']:
    for item in project['files']:
        path = safe(project['destination'] + '/' + item['path'])
        immutable.add(path)
        if not args.navigation_only:
            assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256'], str(path)
            count += 1
navigation = {ROOT / 'README.md'}
navigation.update(safe(x['path']) / 'README.md' for x in structure['paths'])
navigation.update(safe(x) / 'README.md' for x in catalog['legacyPaths'])
for path in navigation - immutable:
    for href in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if '://' in href or href.startswith(('#', 'mailto:')):
            continue
        resolved = (path.parent / href.split('#')[0]).resolve()
        assert resolved.is_relative_to(ROOT) and resolved.exists(), (path, href)
print(f'PASS: {len(seen)} mirrored categories, four business lines, Gaming nesting, and {len(catalog["legacyPaths"])} compatibility pages.')
print('Academic hash checks skipped for partial local checkout.' if args.navigation_only else f'PASS: {count} exact academic source files.')
