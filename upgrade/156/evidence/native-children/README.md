# Native resident-engine children: development evidence

The matching aros-web development commit is `be82ac7`. CEFHost's explicit
`--native-children` diagnostic mode launches the small CEFSubprocess helper via
the existing native AROS process/MessagePort implementation. Each helper opens
the resident libraries and executes its real child arguments.

## Verified boundaries

- Host/helper/browser-client cross-builds pass for x86-64 and AArch64.
- The first process-state candidate passes x64 complete archive and native
  module linking, normal SDK strip, and section-name compaction.
- Native x64 run 90 launches GPU, utility and renderer helpers. Parsed host,
  GPU and utility records share the same allocator/free addresses. Some later
  serial records interleave, so the machine-readable child list is incomplete.
- Run 90 advances beyond the prior histogram and extension-client singleton
  failures, then fails at `trace_startup_config.cc:97`: the tracing configuration
  is still shared across native processes. Its screenshot is a failed test,
  not a browser first-paint result.
- The snapshot now additionally scopes tracing startup configuration and its
  initialization flag to each process. Both complete CEF archive builds pass
  with that change. Run 91 clears tracing startup and exposes shared heap-profiler
  and HTTP-cache initialization state. Run 92 clears those checks after those
  values were scoped to their native owner.
- Run 92 then traps in PartitionAlloc logging and recurses through allocator
  dispatch. Exact installed ELF symbols identify duplicate hook insertion: the
  resident dispatch node becomes self-linked before the observer-hook check.
  Each parsed child matches its preceding host allocator addresses across three
  reboots. This is failed runtime evidence, with no first paint.
- The current snapshot serializes resident dispatcher installation with a native
  AROS lock before either observer mutation or hook insertion. Subsequent
  initialization returns under the documented first-initialization-wins contract.
  Both complete archives and native x64 linking pass. Run 93 clears this
  boundary and stops at the still-global memory-pressure listener registry.
  The allocation fast path has no new lock, and allocator checks remain intact.

`source-manifests.json` distinguishes the run-90 source tree from the later
tracing candidate. The candidate manifest was captured before archive completion;
the retained `cef-tracing-state-*-full1.log` files record subsequent successful
archive completion. `cef-host90-inputs.json` includes binary, source and fixture
hashes. Raw logs remain in the private job evidence; these public text copies
normalize CRLF and trailing whitespace only.

## Implementation and remaining work

Monotonic native CommandLine-owner identities keep workers with their owner and
separate native children. Histogram allocators, recorders and callbacks;
extension clients, permissions, manifests and feature metadata; and tracing
startup configuration now use that identity. Existing duplicate-initialization
and storage-partition checks are retained. No SDK, MMU or scheduler change is
part of this patch, and 2 MiB PartitionAlloc superpages remain unchanged.

The AROS histogram macro currently resolves through the owning recorder instead
of reusing a shared-image static pointer. That is a correctness-first path with
additional lookup cost, not a completed performance optimization. Process-local
registry entries currently retain engine-lifetime storage, matching upstream
NoDestructor usage; reclamation across repeated native child lifetimes still
needs qualification. Full Perfetto multi-process trace attribution is also not
qualified by a startup test.

Two-browser storage isolation, B continuing after A exits, callback draining,
child retirement, host shutdown, and ARM native-child runtime acceptance remain
open. Host session-only lifetime and earlier single-process browser/worker
results are separate evidence and do not establish those outcomes.

The run-92 input manifest pins the preceding cache/profiler candidate. The
current snapshot manifest pins the later allocator candidate; their runtime
claims are deliberately distinct. Run-92 address comparison is grouped by
preceding host because each guest reboot relocates its libraries.

## Memory-routing candidate

Run 93 fails at `memory_pressure_listener_registry.cc:96` before browser first
paint. Host, GPU and utility helpers share allocator addresses. Its screenshot
is retained privately; the public serial/result/input files pin the failure.
The result was saved before screenshot capture encountered an open QMP file;
the VM was paused and a separate capture then succeeded. This is no runtime pass.

The current snapshot scopes the memory-pressure listener registry, memory
consumer registry, and main-thread-default handle to each native process.
It also corrects child shutdown state, renderer main-task-runner storage, and
last-resort GC policy ownership found in the same audit. These prevent one
child from replacing or shutting down a sibling's state. Both complete archive
builds and native x64 link pass. Run 94 reaches host READY and then fails the
performance-scenario observer initialization check. All existing ownership
and duplicate-registration checks remain.

The current snapshot also scopes Blink main/compositor thread wrappers and main
heap storage to the native owner. Release heap access keeps the task-local fast
path. Performance scenario observer lists, mapping handles and their locks are
owner-local; the global scenario backing data stays shared. Both complete x64
and AArch64 CEF archive builds pass. Native library links and run 95 runtime
acceptance are pending. Existing initialization checks remain enabled.

## Direct-browser regression control

The direct browser using its default context passes on the memory-routing
candidate: page paint, same-origin cookie/localStorage checks, DOM and Worker
state checks through 60 seconds, browser close, and CEF shutdown all succeed.
`cef-direct94-control-*` pins that successful native x64 control (ISO run 97).
The preceding host/custom-context control (ISO run 96) was invalid for this
purpose: it hits the already known single-process storage-partition restriction.
Its failed result is retained and must not be called a new routing regression.

The direct control reports whole-guest use of 138.80 MiB before opening CEF,
879.88 MiB after opening it, 1550.92 MiB at first paint, and 1495.69 MiB after
closing CEF. These are whole-guest snapshots, not isolated browser RSS, and
closing a library is not proof of expunging resident engine allocations.
This control proves neither two-app isolation nor long-term memory reclamation.

Run 94's GPU free-pointer text was interleaved with other serial output; its
full address comparison is indeterminate. The parseable utility record matches
the host. A malformed log field must not be reported as an allocator mismatch.


## Scenario candidate runtime 95 and ARM control 23

Both native engine links pass for the scenario/Blink candidate published in
`ddcf15f`. Native x64 run 95 clears scenario initialization, starts renderers,
and fails the child memory coordinator singleton check at
`content/child/memory_coordinator/child_memory_coordinator.cc:24`.
All four parseable child records (GPU, utility and two renderers) use the host's
allocator/free addresses. This is not a two-browser isolation pass. The input
manifest pins the scenario source snapshot and installed binaries.

ARM control 23 uses the same scenario candidate and local JS/Wasm worker fixture.
It times out while opening CEF, before a worker result or teardown. It logs no
Chromium fatal or native alert. The 112.48 MiB sample is before opening CEF,
not browser memory use. ARM stall diagnosis is deferred; earlier worker passes
remain separate evidence and do not qualify this candidate.


## Child coordinator and WTF follow-up candidate

The current source snapshot scopes ChildMemoryCoordinator to its native owner,
retaining construction/destruction assertions. WTF initialization now uses the
existing monotonic process identity instead of a reusable CommandLine address.
An Exec-backed base lock serializes the complete engine-wide initialization;
each renderer still establishes main-thread TLS before that shared initialization.
Complete x64 and AArch64 archive builds pass. Native engine links and runtime 98
are pending. The compositor scheduler and WebRTC logging audit follow-ups are
not part of this snapshot, and repeated child lifetime reclamation is still open.


ARM 23 later completed after the bounded watcher ended: the retained
`cef-direct-arm23-late-*` evidence shows JS/Wasm workers PASS, painted/closed
cleanly and CEF teardown returned. The original timeout is preserved. First
paint uses 1185.19 MiB whole guest, after CEF close 1151.71 MiB; neither is
isolated RSS or proof of expunging the resident engine. The browser screenshot
was missed after the watcher ended, and guest shell RC was not routed to serial.
This late result qualifies the local worker exercise, not network or multi-app
behavior, and does not diagnose the long CEF-open interval.


## Child coordinator runtime 98

Both native links pass for the child-coordinator/WTF candidate. Run 98 clears
the prior child-coordinator assertion, then fails the FilesystemProxy containment
check: `/T:/CEFHostProfiles/Default/Login Data` and the Reporting/NEL database
cannot be made relative to `T:CEFHostProfiles`. The input manifest pins this
candidate and the result preserves the failure. Two-app acceptance remains open.

The cause is the older `sql::Database::ArosPathForSqlite` conversion, which
rewrites a native assign path for a Unix VFS workaround. The current AROS local
SQLite VFS already resolves DOS locks; the sandboxed VFS preserves the supplied
path for comparison with its root. The current snapshot removes the conversion
for database open and ATTACH and retains the root containment assertion.


The current snapshot also scopes the compositor scheduler pointer to each native
owner, matching the already owner-local thread wrappers and preserving existing
constructor/destructor checks. Both complete archive builds pass. Native links
and runtime 99 remain pending.

ARM run 24 passes with the preceding child-coordinator/WTF candidate: local
JS/Wasm workers, page paint, browser close, CEF teardown and explicit script RC0.
The rendered PNG was visually reviewed; the first-paint image was only a blank
cyan frame and is not used as worker proof. Whole-guest memory is 112.35 MiB
before CEF, 524.78 MiB after library open, 1185.15 MiB at first paint and
1151.89 MiB after CEF close. These measurements are not isolated browser RSS.
The browser covers most of About AROS in the screenshot. This is a native CEF
worker exercise, not full Chrome UI, network, or multi-app acceptance.

![Native ARM JS/Wasm worker pass](cef-direct-arm24-rendered.png)
