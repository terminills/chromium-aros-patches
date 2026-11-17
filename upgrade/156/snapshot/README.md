# Chromium 156 AROS migration snapshot

This directory contains the in-progress Chromium 156.0.8078.96 / CEF 8078 migration. It is not a release-ready engine. The repository root patch queues and PINS still describe the retained Chromium 124 baseline.

`PINS` and `manifest.json` record the exact upstream commits for this snapshot. Each patch was replayed against its base in an isolated Git index; the manifest records its SHA-256 and resulting Git tree. Patches include the required current CEF upstream changes as well as AROS adaptations.

To reproduce the source snapshot, obtain the Chromium checkout and dependencies at these pins, then run `git apply` with the corresponding patch inside each repository listed in the manifest. Do not apply the root Chromium 124 queue on top. Unchanged dependencies follow Chromium DEPS. The CEF repository is an additional checkout under src/cef.

Validation so far includes cross-compilation of the base library for AArch64, the native CEF library ABI wrappers for x86-64, and a GCC 16.2 C++23 runtime probe on native x86-64 AROS. The full CEF compile/link, browser runtime, graphics, profile isolation and AArch64 runtime gates remain open. See adjacent upgrade evidence for the individual checks; none substitutes for full engine acceptance.
