#!/usr/bin/env python3
"""Replay patches in temporary indexes without changing checkout files or refs."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('chromium_src', type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
source = args.chromium_src.resolve()
results = []
for entry in json.loads((root / 'EXPORT.json').read_text())['repositories']:
    name = entry['path']
    repo = source if name == 'src' else source / name
    with tempfile.TemporaryDirectory(prefix='aros-queue-') as temp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temp) / 'index'))
        def git(*command):
            return subprocess.check_output(['git', '-C', str(repo), *command], env=env, text=True).strip()
        git('read-tree', entry['base'])
        patches = (root / name / 'series').read_text().splitlines()
        if len(patches) != entry['patch_count']:
            raise SystemExit(f'{name}: patch count differs from EXPORT.json')
        for patch in patches:
            git('apply', '--cached', '--whitespace=nowarn', str(root / name / patch))
        tree = git('write-tree')
        match = tree == entry['export_tree']
        results.append(match)
        print(f'{name}: {len(patches)} patches; tree {tree}; {"PASS" if match else "MISMATCH"}', flush=True)
raise SystemExit(0 if all(results) else 1)
