# Native cache602 retirement and regression evidence

Source602 changes only the AROS lifetime of Blink's SmallStringCache relative to snapshot585. Native TLS cleanup now destroys and frees each child main task's cache. Other platforms and other Blink thread-specific objects retain their existing behavior.

Offline inspection of run588 identified 100 retained 256 KiB caches (25 MiB): every populated entry matched the exact production layout, Fibonacci hash, length and padding. Both full CEF archives602 and native libraries603 link successfully. The exported snapshot replays against all 21 repository pins.

## Matched x64 100-session control604

The OS, host, clients and V8 baseline are unchanged from588; only CEF changes to603. All100 pages and renderer retirements pass, with zero deferred retirements and full host shutdown. The child-owned DOS ledger contains102 matching zero-result entry/exit pairs. The strict serial parser reports failure because utility83's entry is absent; its exit is present. Independent83.enter/83.exit files provide the missing evidence. The original failed report and raw serial log are retained beside the explicit reconciliation.

| Whole-guest sample | Run604 |
| --- | ---: |
| Cycle30 |1222.46 MiB|
| Cycle100 |1294.33 MiB|
| After host exit |1135.25 MiB|
| Growth cycles30–100 |71.88 MiB|

Run604 uses40.06 MiB less whole-guest memory at cycle100 and40.02 MiB less after host exit than588. The final allocator sample has **zero allocated256 KiB slots** across all four verified roots. PartitionAlloc retains144.22 MiB Exec backing and113.72 MiB exposed mappings, versus184.22/139.72 MiB previously. Direct cache reclamation and arena reuse both contribute; whole-guest values are not process RSS. **Memory still grows; no plateau or RC is claimed.**

## Other matched603 controls

- ARM605: full New Tab and About AROS paint on the retained583b OS.
- X64 sibling606: independent storage/DOM/workers, app B survives app A closure, both renderers retire, full host exit and four zero child-ledger pairs.
- X64 coldboot607: synthetic cookies and localStorage survive full host shutdown and VM restart; native volume flush passes.
- Installed608 layouts: native icon metadata passes both architectures. X64 runtime609 icon launch, close and relaunch paint full UI with one host opening. ARM610 installed icon launch paints full UI using native input.device injection; USB and physical Pi are unqualified.

## Current-master rebuild separation

These controls use preserved matching OS/SDK inputs. A subsequent merge of upstreamca69713a into private0072a061 changes Task/Process ABI and requires new engines and clients. Refresh611–621 artifacts are excluded: configure ran under /bin/sh, returned0 but dropped Bash += architecture assignments. Fresh622 builds use CONFIG_SHELL=/bin/bash and explicit Bash configure, with generated ISA flags validated before compilation. SDK623/engines624/native625 qualification remains pending.

CPU Lavapipe Vulkan/WebGL qualification is historical and separate from hardware RADV/NVK. Widevine end-to-end, real account sign-in, Node/Electron/Zune consumers and final release packaging remain unqualified. This is a source and evidence update, not a binary release.

The diagnostic scripts retain original private paths and require matching local artifacts, symbols and guest captures. They are evidence references, not a standalone downloadable test environment. Full guest memory is retained privately; its compressed hash is in the QMP record.
