# Native debug-flag reads and source749

The shared AROS engine now reads both Widevine diagnostic flags with DOS GetVar into a stack buffer. This preserves dynamic debug controls for resident-engine clients without calling the shared libc environment cache on each decoder operation. It changes Chromium only; no generic SDK interface changes are required.

Runtime742's exact-image stack and disassembly identify its failing getenv call. The native libc cache frees and reallocates the same value storage on repeated lookups, so concurrent diagnostic checks can race. [Graphics748](../graphics748/README.md) retains that failure and the independent graphics fix.

The updated snapshot also includes opt-in numeric pipe/decode watchdogs and the opt-in native-video-decoder experiment. Both are disabled by default. Diagnostics never emit keys, session identifiers, license payloads or decrypted buffers. The experiment still encounters NoKey on encrypted video and is not the production decoder path.

## Validation

- Source749 exports and exactly replays22 repositories against their pinned upstream commits.
- Media746 x86-64 archive, native final link and packaging pass. Installed library SHA256: `eb4a791842e73c8cb2563091d362c827fd013572e365c476a090484ce921508e`.
- [Native flag probe](../../tests/debug-flag746-probe.cpp): eight cases,7,001 reads, zero failures on native AROS. It covers absent, empty, zero, one, longer values and a newline suffix.
- ARM751 now passes its full archive and native link; see [playback760](../playback760/README.md). The native ARM local H.264/AAC play, seek and replay regression also passes; network and audio output remain unqualified.
- Runtime747 now completes an uninterrupted encrypted 733.999-second replay with audio enabled; [playback760](../playback760/README.md) records the bounded result and screenshots. Cache errors and broader stability qualification remain open.

This remains an in-progress source snapshot, not an RC. The external proprietary CDM is not included.
