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

Snapshot468 closes renderer-owned extension/Chrome resources while their native scheduler and V8 isolate are still alive, after owner views/workers drain. Both native469 links pass. X64 sibling473 isolation and profile475 synthetic close/reopen pass. Thirty-cycle474 failed at cycle16 in memory-instrumentation startup. ARM479 visibly renders New Tab/About AROS (../evidence/arm495); full lifecycle and memory acceptance fail. See ../evidence/renderer481. No RC is released.

The engine retains one shared code image and 2 MiB PartitionAlloc superpages.
Bounded QEMU results do not establish release readiness, full browser/media/DRM
coverage, accelerated graphics or physical-device qualification. Only modules
from the same build may be loaded. See ../evidence/native-children for exact
inputs, retained failures, harness corrections, screenshots and test limits.
