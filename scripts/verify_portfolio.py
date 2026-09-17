"""Verify the public directory and byte-preserved academic imports, offline."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads((ROOT / "portfolio.json").read_text())
expected = ["consulting-career", "writing", "art", "gaming"]
assert [item["id"] for item in catalog["collections"]] == expected
gaming = catalog["collections"][3]["projects"]
assert [item["id"] for item in gaming] == ["third-strike", "ddr", "smash", "game-development"]
assert [item["id"] for item in gaming[2]["children"]] == ["melee", "ultimate"]

def check_entry(entry):
    path = ROOT / entry["path"]
    assert path.is_relative_to(ROOT) and (path / "README.md").is_file(), entry["path"]
    for child in entry.get("children", []):
        check_entry(child)
    for child in entry.get("projects", []):
        check_entry(child)

for entry in catalog["collections"] + catalog["shared"]:
    check_entry(entry)
manifest = json.loads((ROOT / "consulting-career/academic/import-manifest.json").read_text())
total = 0
for project in manifest["projects"]:
    for source in project["files"]:
        path = ROOT / project["destination"] / source["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"], str(path)
        total += 1
# Check new navigation, excluding preserved historical source documentation.
paths = [ROOT / "README.md"] + [ROOT / entry["path"] / "README.md" for entry in catalog["collections"] + catalog["shared"]]
for path in paths:
    for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
        if "://" not in target and not target.startswith("#"):
            assert (path.parent / target.split("#")[0]).exists(), (path, target)
print(f"PASS: four business lines, four Gaming areas, two Smash games, {total} exact academic files.")
