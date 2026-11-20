# Feature-provider lifetime and native regressions

Source344 includes the Skia directory reservation correction338 and releases process-local feature provider maps through AtExit. The 21-repository snapshot replays successfully; native345 x64 links successfully.

Native346 passes 30 page cycles, 62 complete renderer retirements with none deferred, full host return and independent child entry/exit accounting. Native347 passes two-app storage/DOM/worker isolation and surviving-app behavior after the other closes.

Retained heap evidence supports the cleanup: FeatureProvider vtable candidates fall from252 to0, and the generic partition reports roughly1.05MiB less allocated memory after host exit. Vtable scans include possible freed slots and are not a live-object census. Whole-guest memory still grows about5.07MiB/cycle over cycles10–30, versus5.02 in331; no plateau or overall memory improvement is claimed.

ARM341 uses source338/native339 and still faults before first paint. Matching machine code and retained guest fields establish that renderer host4 was retiring with a null channel while its liveness predicate still returned true. A correction is staged privately; this published snapshot does not contain an accepted fix.

No RC release. These are native QEMU results, not physical hardware or security sandbox qualification. Earlier UI/profile and credentials results retain their original source/build identities.
