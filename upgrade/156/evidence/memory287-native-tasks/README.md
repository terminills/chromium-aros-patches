# Native task cache lifetime correction

The retained252 engine completed a second30-cycle native x64 QEMU run:30 pages,63 child entry/exit pairs,60 complete renderer heap retirements, and no native fault. After the host returned, the actual PartitionAlloc registry still held1,229 cache records with14,938,112 cached bytes. Whole-guest memory remained higher; cache bytes are not an explanation for all retained memory.

The existing AROS pthread-key implementation stores raw Exec task slots in task.resource, but does not execute their key destructors. Chromium already drained its own base TLS vector on native task exit; its allocator uses a separate key. Source285 adds explicit PA cache destruction after base TLS consumers finish, then marks the task cache retired to prevent resurrection during late CRT cleanup. Existing pthread-created thread destructor behavior is preserved. No SDK change is made.

Actual extracted cleanup bodies pass host ASan/UBSan tests for200 exits across two task slots, reentrant and repeated exit, absent base TLS, and uninitialized allocator. Actual x64/ARM objects compile. Dependencies in the host fixture are mocked; this is not native acceptance.

Source287 integrates285 and the separately tested273 feature/trial cleanup atop267. The complete21-repository snapshot replays successfully. Fresh-master288 engine builds and subsequent289 clients/credentials and290 browser/profile validation are pending. Both V8 archives revalidate unchanged. No RC release is claimed.
