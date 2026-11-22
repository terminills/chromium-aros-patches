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

Snapshot444 closes owner-local Blink views, then drains their asynchronous
worker cleanup callbacks through the native renderer task pump before scheduler
shutdown. The wait is bounded; the existing isolate-retirement safety guard
remains if a worker cannot finish. Both native445 links pass. Sibling446 passes
independent app state, app B survival after app A closes, all four child exit
records, and both isolate retirements with none deferred.

The preceding source442/native443 passed thirty-cycle438 and profile440. Its
memory still grew36.71MiB between cycles10 and30. The current hundred-cycle450
memory test and ARM448 browser visual test are running. See ../evidence/workers451
and ../evidence/retirement447 for exact identities and limits. No RC is released.

The engine retains one shared code image and 2 MiB PartitionAlloc superpages.
Bounded QEMU results do not establish release readiness, full browser/media/DRM
coverage, accelerated graphics or physical-device qualification. Only modules
from the same build may be loaded. See ../evidence/native-children for exact
inputs, retained failures, harness corrections, screenshots and test limits.
