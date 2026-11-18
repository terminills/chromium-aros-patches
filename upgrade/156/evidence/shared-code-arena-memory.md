# Shared V8 code arena sizing

The AROS shared CodeRange used the architecture maximum even when gin requested 64 MiB. Honor the computed requested_size when creating the first shared arena. Its capacity stays fixed for its lifetime; later isolates share allocations within it, and the last user owns its retirement. This does not change the SDK, the platform allocator, or PartitionAlloc 2 MiB superpages.

Native QEMU first-paint whole-guest memory (Exec AvailMem):

| Architecture | Baseline MiB | Candidate MiB | Observed saving MiB |
|---|---:|---:|---:|
| x86-64 | 2053.69 | 1593.73 | 459.97 |
| AArch64 | 1397.98 | 1188.91 | 209.06 |

These are within-architecture comparisons with identical local HTML, CEF engine and client. Structural code-arena reductions are 448 MiB and 192 MiB respectively; whole-guest deltas also include timing and other allocations. Different viewports and OS builds prohibit treating the architecture difference as an optimization comparison. ARM candidate used a shorter post-paint hold.

Both candidate V8 source/native builds pass, and both runtime candidates paint and return from full CEFShutdown. x64 baseline67 also returns normally. ARM baseline14 stalls during teardown in task.resource TaskListSpinLock; earlier baseline13 returns normally. The retained OS failure is not fixed or explained by this patch.

x64 fixture71 creates two dedicated WebWorkers, each with 5000 Function objects, terminates A and verifies B still executes its own function and retains its identity. Actual screenshot displays AROS_SHARED_WORKERS_PASS; full teardown returns. This tests two worker isolates, not SharedWorker API or complete cross-application isolation. ARM equivalent fixture16 also displays and logs AROS_SHARED_WORKERS_PASS; it then closes and returns from full CEFShutdown. The retained screenshot includes About AROS identifying aarch64-raspi. The URL is supplied from a DOS file because the native shell truncates the original long command. aros-web dac5c1d implements this test-client input.

Evidence JSON records native library hashes and lifecycle samples. The engine remains resident after CEFShutdown; after-close whole-guest memory is not a standalone leak measurement.
