# Renderer resource teardown: source468 / native469

Renderer-bound extension dispatcher, V8 schema handles, Chrome observer, cache, logging, spellcheck and related resources now close after owner views/workers drain and before scheduler/isolate retirement. They previously survived until AtExit, where the scheduler/isolate were already unavailable and objects were deliberately retained. The existing bounded worker timeout keeps its safe-retention fallback.

Both x86_64 and AArch64 native links pass. On x64 QEMU, sibling473 passes every two-app storage/DOM/worker isolation gate, B surviving A closure, all four child entry/exit pairs and both completed retirements with none deferred. Profile475 passes synthetic cookie/localStorage write, close, reopen and read without native faults. Logs show resource release preceding isolate retirement.

![Profile read after reopening](master475-profileread.png)

Thirty-cycle474 **failed at the start of cycle16** with a native fatal assertion at ClientProcessImpl::CreateInstance (client_process_impl.cc:86). The first15 retirements completed, but lifecycle acceptance fails. Crash evidence is retained. The AROS memory-instrumentation registry still uses CommandLine allocation addresses as owner keys; address reuse is being investigated. ARM479 now visibly renders New Tab/About AROS; see ../arm495. Full lifecycle and memory acceptance remain failed. No memory saving, RC or physical-device qualification is claimed. Native484 was cancelled; source489/native490 adds the monotonic-owner correction and raster-pool cleanup, and is not this snapshot.
