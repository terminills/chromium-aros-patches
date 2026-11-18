# Native CEF request-context isolation — 2026-11-18

Probe source: aros-web4ecf9e2, libs/cef/test_cef_contexts.c; target workbench-libs-cef-test-contexts-quick. Both x86-64 and AArch64 cross-builds pass. All context operations use the public native cef.library facade and the existing shared engine; no embedded engine or SDK change.

Native x64 run79 PASS:
- Initialize CEF once; create two independent in-memory request contexts.
- Set the same secure cookie name at https://context-isolation.invalid/ to A and B in their respective contexts. No network request or real credential is involved.
- Assert different context identities, no sharing, exactly one matching cookie per context, and the distinct values.
- Release all client-held manager/context references to A, pump queued work, then verify B still returns only B.
- Release B; full CEF shutdown returns, followed by the PASS marker.

The refcount probe does not independently acknowledge that every internal A object has been destroyed. It qualifies same-origin in-memory cookie separation and client-reference lifetime under one engine, not persistent-profile storage, independent app tasks, browser renderer isolation or sandboxing.

Prototype78 failed because its identity comparison consumed the retained wrapper reference for the other context. The next comparison unwrapped a freed wrapper. CEF's generated cpptoc_ref_counted.h Unwrap explicitly releases the reference transferred by a refptr_same parameter. The corrected client adds a reference before each comparison; self remains borrowed. The engine was unchanged. Failed runtime78 ISO and raw log remain retained; the public log is normalized only for line endings/trailing whitespace.

ARM runtime19 is pending separately; its cross-build is not presented as a runtime pass.
