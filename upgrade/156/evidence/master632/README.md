# Current-master AROS prerequisites

This is the complete private AROS delta for Chromium 156/CEF8078 against upstream **ca69713ae7f4d0c8de632f9552e74b7b59c58140**. Applying it reproduces tree **2f696ea69bc20965ca1f91413d25e598be3fb468**, corresponding to private commit **0072a0613f224ce91aaad46e2aaf351b45c0b706**. The patch was replayed into an independent index and its tree compared exactly.

Apply `aros-prerequisites.patch` once to that clean upstream commit. Do not stack the older master229, credentials, LinuxSO or other historical prerequisite patches on top. This consolidated delta already includes them and the retained ARM boot and loader prerequisites. The separate Chromium snapshot and matching aros-web source are still required.

## Configure and ABI requirements

Invoke configure explicitly with `/bin/bash` and export `CONFIG_SHELL=/bin/bash` and `SHELL=/bin/bash`. Pass `SHELL=/bin/bash` to make as well. The pinned upstream configure contains Bash append assignments: invoking it through `/bin/sh` can return success while losing architecture flags. A successful configure exit code alone is insufficient.

Verify the generated x86 flags include `-m32 -march=i486`, x86-64 flags include `-m64 -mcmodel=large`, and AArch64 flags include `-mcmodel=large` and the supported `-mno-outline-atomics` feature. Fresh622 configuration validates these settings before compilation.

The upstream Task/Process layout changed. Rebuild the SDK, engines, libraries, native applications and drivers together; do not overlay old native modules into the new OS. The attached compile-derived ABI measurements show the exact old/current sizes and offsets for both architectures.

The ARM test build uses `AROS_BOOT_CPU_LIMIT=2`; its QEMU RAM setup is a separate harness setting. No scheduler fix or physical Raspberry Pi qualification is implied.

## Validation boundary

This publication is a source prerequisite and exact replay result, not an RC binary release. The fresh ARM SDK/kernel/production boot targets have passed. Full desktop completion, frozen SDKs, engine rebuilds, fresh drivers and matched browser runtime qualification remain in progress. Earlier native603 browser controls use their retained matching OS and do not qualify this newer ABI.

LinuxSO is retained for the prior x86-64 Widevine path. Its presence is not proof of CDM playback or an ARM Linux-object loader. Chromium-local memory allocation remains in the Chromium snapshot; no general SDK mmap implementation is introduced here.
