# Renderer isolation and retirement follow-up

This is development evidence, not a release candidate. Source421 is replay-checked across21 repositories and includes414 observer ordering and child IPC cleanup plus an owner-local render-frame observer map. x64 archive422 passes; native422 and runtime425 are pending.

Both414 native engine links pass. Thirty page cycles and all32 child exits complete, but all30 renderer isolate retirements defer because one page remains alive. Whole-guest memory rises from1484.27MiB at cycle10 to1732.14MiB at cycle30. Two-app isolation and survivor behavior pass; retirement fails.

The independent post-host memory capture verifies32 child IPC handles cleared; only the owner1 broker remains, with the exact native414 Node vtable. This confirms the IPC cleanup without claiming a memory plateau.

Browser418 fails before profile write at a null ExtensionFrameHelper lookup. The retained shared tracker map contains three frame entries with null values. Source421 scopes each tracker map and its AtExit cleanup to the logical renderer owner. The precise timing of the failing map destruction is not proven; native regression is required.

The lifecycle log enters fast shutdown before every deferred page retirement. A separate424 candidate makes AROS decline FastShutdownIfPossible so normal frame deletion can complete. It is staged privately and is not part of this snapshot. The live-page retirement guard remains intact.

ARM417 was paused before boot because its inspector helper was missing. The helper and guarded RAM-map setup were restored, the original failed observer result retained, and the VM resumed. The current screenshot shows the ARM desktop and About AROS while Chromium loads. Historical production379 full New Tab evidence remains in production415.

[Current release gates](release-candidate-gates.json)
