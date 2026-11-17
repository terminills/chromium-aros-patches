#!/usr/bin/env python3
"""Build a native AROS Rust probe with Chromium's pinned Rust toolchain."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--chromium', type=Path, required=True)
p.add_argument('--sdk', type=Path, required=True)
p.add_argument('--cc', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
here = Path(__file__).resolve().parent
rust = a.chromium.resolve() / 'third_party/rust-toolchain'
std = rust / 'lib/rustlib/src/rust'
sdk = a.sdk.resolve()
out = a.out.resolve()
cc = a.cc.resolve()
revision = '1edd55dcfcd573872c727fa3e086369a71661ee0'
version = subprocess.check_output([str(rust / 'bin/rustc'), '-Vv'], text=True)
if 'commit-hash: ' + revision not in version:
    raise SystemExit('Wrong Rust compiler revision; use Chromium 156.0.8078.96 toolchain')
files = json.loads((here / 'files.json').read_text())
def matches(field):
    for item in files:
        path = std / item['path']
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
        if actual != item[field]:
            return False
    return True
if not matches('after_sha256'):
    if not matches('before_sha256'):
        raise SystemExit('Rust sources differ from both pinned baseline and patched state')
    subprocess.run(['git', 'apply', '--check', str(here / 'std-aros.patch')], cwd=std, check=True)
    subprocess.run(['git', 'apply', str(here / 'std-aros.patch')], cwd=std, check=True)
assert matches('after_sha256')
out.mkdir(parents=True, exist_ok=True)
shutil.copytree(here / 'probe', out / 'probe', dirs_exist_ok=True)
# Cargo does not reliably invalidate externally patched build-std sources.
# Key its target directory by every source/glue input, not only Cargo.toml.
digest = hashlib.sha256()
for path in sorted(here.rglob('*')):
    if path.is_file():
        digest.update(str(path.relative_to(here)).encode())
        digest.update(path.read_bytes())
target = out / ('target-' + digest.hexdigest()[:16])
env = dict(os.environ, RUSTC_BOOTSTRAP='1', RUSTC=str(rust / 'bin/rustc'), CARGO_TARGET_DIR=str(target))
subprocess.run([str(rust / 'bin/cargo'), 'build', '-Zjson-target-spec', '-Zbuild-std=std,panic_abort', '--release', '--locked', '--target', str(here / 'x86_64-unknown-aros.json'), '--manifest-path', str(out / 'probe/Cargo.toml')], env=env, check=True)
objects = []
for source in sorted((out / 'probe/glue').glob('*.c')):
    obj = source.with_suffix('.o')
    subprocess.run([str(cc), '--sysroot=' + str(sdk), '-O2', '-Wall', '-Wextra', '-Werror', '-I' + str(sdk / 'include/aros/posixc'), '-I' + str(sdk / 'include/aros/stdc'), '-I' + str(sdk / 'include'), '-c', str(source), '-o', str(obj)], check=True)
    objects.append(str(obj))
archive = target / 'x86_64-unknown-aros/release/libaros_std156_probe.a'
exe = out / 'Rust156Probe'
subprocess.run([str(cc), '--sysroot=' + str(sdk), '-B' + str(sdk / 'lib') + '/', *objects, str(archive), '-lpthread', '-o', str(exe)], check=True)
print('Native compile/link PASS:', exe)
print('sha256:', hashlib.sha256(exe.read_bytes()).hexdigest())
print('Run Rust156Probe on AROS; compilation is not runtime validation.')
