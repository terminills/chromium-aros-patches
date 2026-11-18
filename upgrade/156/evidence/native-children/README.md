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
  Both complete archives pass; native link and runtime 93 are pending.
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
