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

Snapshot462 additionally releases each owner's extension permission registry through native AtExit. Both native463 links pass. X64 single-core two-app isolation476, synthetic profile466 close/reopen and thirty-cycle465 pass; all30 retirements complete. Memory still grows36.705MiB between cycles10 and30. See ../evidence/permissions478 for exact identities, the corrected harness audit and remaining limits.

Prior ARM448 rendering belongs to source444/native445. ARM463 runtime acceptance remains open. No RC is released.

The engine retains one shared code image and 2 MiB PartitionAlloc superpages.
Bounded QEMU results do not establish release readiness, full browser/media/DRM
coverage, accelerated graphics or physical-device qualification. Only modules
from the same build may be loaded. See ../evidence/native-children for exact
inputs, retained failures, harness corrections, screenshots and test limits.
