#!/usr/bin/env python3
"""Build the focused native fixture. Run the result on AROS, not the host.
Usage: script SOURCE GN_OUTPUT SDK CROSS_GCC OUTPUT_DIRECTORY
The supplied GN output must already contain chromium_sqlite3.ninja.
"""
import pathlib
import shlex
import subprocess
import sys

src, gn, sdk, compiler, out = map(pathlib.Path, sys.argv[1:])
out.mkdir(parents=True, exist_ok=True)
settings = (gn / 'obj/third_party/sqlite/chromium_sqlite3.ninja').read_text()
defines = settings.splitlines()[0].split(' = ', 1)[1]
# ICU collation is outside this VFS fixture. Production retains ICU unchanged.
defines = [arg for arg in shlex.split(defines) if arg != '-DSQLITE_ENABLE_ICU']
base = [str(compiler), '-O2', '-I' + str(src), '--sysroot=' + str(sdk)]
sqlite = src / 'third_party/sqlite'
subprocess.run(base + defines + ['-c', str(sqlite / 'sqlite3_shim.c'),
                               '-o', str(out / 'sqlite.o')], check=True)
names = ['chromiumArosLockOpen', 'chromiumArosLock', 'chromiumArosLockLevel',
         'chromiumArosUnlock', 'chromiumArosReserved', 'chromiumArosLockClose']
renames = ['-D' + name + '=' + name + '2' for name in names]
subprocess.run(base + renames + ['-c', str(sqlite / 'sqlite3_aros_locks.c'),
                               '-o', str(out / 'second-engine-locks.o')], check=True)
subprocess.run(base + [str(pathlib.Path(__file__).with_name('native-sqlite-aros.c')),
                      str(out / 'sqlite.o'), str(out / 'second-engine-locks.o'),
                      str(sqlite / 'sqlite3_aros_vfs.c'),
                      str(sqlite / 'sqlite3_aros_locks.c'),
                      '-lutility', '-lpthread', '-ldebug', '-lm',
                      '-o', str(out / 'NativeSqliteAros')], check=True)
print('Native fixture linked. Native execution is required for a test result.')
