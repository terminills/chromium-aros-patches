# Native auxiliary tracing task retirement

Source319 / engine320 completes ten native x64 cycles with all pages passing, independent zero-exit child ledger,22 completed and0 deferred renderer retirements. Task count stays112 for cycles2–10 and falls to44 after host exit, against69 in baseline318. Native reserved task stacks no longer grow by4MiB per later cycle.

Whole-guest used memory: cycle2 1499.22MiB, cycle10 1526.48MiB, host exit 984.86MiB. Growth remains; this is not a memory plateau or RC. The larger post-host reduction must not all be attributed to trace stacks: baseline318 had one deferred isolate retirement whereas323 has none. Task counts and stack reservations are the direct evidence for the targeted fix.

The implementation joins auxiliary owner trace threads after AtExit and child ThreadPool completion, preserving the engine-global muxer runner and backend/TLS object lifetimes. The source319 snapshot replays across21 repositories. Both native320 engine links pass; ARM runtime validation still uses earlier288.

ARM322 now opens the engine after the GL/Vulkan dependencies were installed, but reaches a missing PROFILE assign requester before initialization completes. Its failure is retained.327 Mesa runtime now builds;328 fresh guest adds the persistent profile assign. Separately staged329 fixes the tracing registry to use monotonic owner IDs and prevents absent PROFILE detection from opening a requester;330 build and longer native test are pending.

No RC binaries or security-sandbox claims. Previous UI/isolation/profile evidence retains its original source287 identity and must be rerun where needed after newer source changes.
