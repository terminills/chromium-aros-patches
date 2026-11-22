# Chromium 156 AROS migration snapshot

This is the in-progress Chromium 156.0.8078.96 / CEF 8078 source snapshot. It is not
release-ready. The repository root queues retain the Chromium 124 baseline;
use this directory for the 156 branch.

A live inventory checked 169 Git repositories. The manifest covers all 21 modified
repositories, including Chromium, CEF, V8 and patched dependencies. Each patch
was replayed against its exact recorded commit in an independent Git index;
SHA-256 values and resulting Git trees are recorded. Unchanged dependencies
follow Chromium DEPS. CEF is an additional checkout at src/cef.

Obtain the recorded sources, then apply each manifest patch in its corresponding
repository. Do not layer the Chromium 124 root queues or the explanatory patches
in ../aros on top: this snapshot already includes their current changes.

Source489/native490: both native links pass; x64 thirty-cycle492 corrected serial audit and profile493 pass. Sibling491 page isolation passes but host shutdown stalls in system resolver worker. ARM494 visually renders. Memory plateau and RC gates remain open. See ../evidence/candidate508/status.json for source-matched results and retained failures.

The engine retains one shared code image and 2 MiB PartitionAlloc superpages.
Bounded QEMU results do not establish release readiness, full browser/media/DRM
coverage, accelerated graphics or physical-device qualification. Only modules
from the same build may be loaded. See ../evidence/native-children for exact
inputs, retained failures, harness corrections, screenshots and test limits.
