# Thirty-cycle native memory control and staged cleanup

Retained engine252 completed30 native AROS/QEMU x64 browser cycles:63 child entry/exit pairs,60 renderer retirements, no native fault. This uses the old SDK/OS and does not qualify source267 or the fresh-master build.

Memory does not plateau: whole-guest usage grows240.435MiB from cycles10 to30 (linear fit12.074MiB/cycle). Post-host usage is1301.06MiB. These are whole-guest measurements, not per-app RSS. Live PA backing is324.25MiB with163MiB alignment slack; this does not identify every live allocation. FieldTrialAllocator retains65 references but only256KiB backing, so it is not established as the cause of the total growth.

The273 cleanup patch is STAGED ONLY, not part of the production patches. Actual extracted registry/functions/CEF lifetime guard pass a host ASan/UBSan two-owner reuse test; real x64 and ARM objects compile. Dependencies in the host fixture are mocked. Native integration, teardown safety and memory effect remain unverified. Active267 builds remain unchanged.

The ledger audit initially retained an old output-directory name. It had already stopped the correct VM before failing. Extraction was resumed only after verifying that VM had exited; the original252 evidence remains untouched. The audit-path correction record preserves this harness failure.
