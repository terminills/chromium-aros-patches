# Additional per-renderer ownership regressions

These are tested source candidates, not a qualified release. Candidate219 separates the interpolation wrapper whose embedded Persistent root was invisible to the generic Persistent singleton trait. Candidate220 separates isolated-world origin/name/embedder metadata, the main-thread non-main-world count, and DevTools world-ID allocation.

Focused actual-method host fixtures reproduce wrong ownership with the original source and pass the candidates. Both architecture translation-unit compiles pass. The world-ID fixture uses a two-ID mock range: exhausting renderer A must not exhaust renderer B. The world-count change has source review and cross compilation only. None of these fixtures establishes native extension security or browser acceptance.

Build221 is queued behind immutable217 binaries/full symbols and installed217 input capture. The native217 candidate fixes the two teardown/reopen failures captured in203; its acceptance is still pending. The two supplied browser pages have syntax and exact local HTTP readback checks only; native paired execution remains pending.

ARM73 activated the installed launcher through input.device and opened the native Chromium window. Painting is still in progress. This does not qualify QEMU USB input. Earlier register snapshots mistakenly sampled CPU0 repeatedly; the retained correction explains the explicit cpu-index method. Current readings and the boot log show two active guest cores, with CPU2 and CPU3 parked. No kernel change or stall root cause is claimed.
