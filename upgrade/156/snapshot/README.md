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

Snapshot 564 includes native ANGLE Vulkan integration and native descriptor locking for the GPU persistent cache. Both full CEF archives compile. Native x64 image 566 passes two full Chromium sessions, WebGL 1/2 readback and host exit using a writable FAT profile. The persistent GPU cache passes a host integrity check on a disposable copy. ARM image 566 passes RAM/FAT alias-lock probes and full New Tab rendering in run 568. See ../evidence/cache564/README.md. Matched image 527 passes 100 browser sessions and 102 native child entry/exit pairs, but memory still grows.

The engine retains one shared code image and 2 MiB PartitionAlloc superpages.
Bounded QEMU results do not establish release readiness, full browser/media/DRM
coverage, accelerated graphics or physical-device qualification. Only modules
from the same build may be loaded. See ../evidence/native-children for exact
inputs, retained failures, harness corrections, screenshots and test limits.
