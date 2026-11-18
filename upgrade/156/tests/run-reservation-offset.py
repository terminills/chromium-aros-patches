#!/usr/bin/env python3
"""Host sanitizer test of production PA headers using AROS generated flags."""
import argparse
import pathlib
import resource
import subprocess
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument("source", type=pathlib.Path)
parser.add_argument("output", type=pathlib.Path)
args = parser.parse_args()
here = pathlib.Path(__file__).resolve().parent

def no_core():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

with tempfile.TemporaryDirectory(prefix="aros-reservation-test-") as tmp:
    exe = pathlib.Path(tmp) / "test"
    subprocess.run([
        "g++", "-std=c++20", "-O2", "-g", "-fsanitize=address,undefined",
        "-D__AROS__", "-include", str(here / "reservation-host-check.h"),
        "-I" + str(args.source / "base/allocator/partition_allocator/src"),
        "-I" + str(args.output / "gen/base/allocator/partition_allocator/src"),
        str(here / "reservation-offset-regression.cc"),
        str(args.source / "base/allocator/partition_allocator/src/partition_alloc/reservation_offset_table.cc"),
        "-o", str(exe),
    ], check=True)
    subprocess.run([str(exe)], check=True, preexec_fn=no_core)
    result = subprocess.run([str(exe), "out-of-range"], preexec_fn=no_core)
    assert result.returncode == -6, result.returncode
    print("PASS: out-of-range write rejected before accessing the table")
