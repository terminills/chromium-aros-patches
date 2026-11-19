# Private compact x86 image experiment and ownership audit

Native cold-load and host relocation checks pass. This is not an RC binary
or full browser qualification.
The immutable input is the retained native191 engine, which still fails
multi-tab navigation. That failure remains recorded in native-installed191.

A matched diskless native AROS test now loads both original and packed build 191
successfully. Whole-guest memory after the probe closes its library references
is **871.59 MiB original versus 646.89 MiB packed**, a **224.70 MiB reduction**.
Both VMs start at 25.17 MiB and use one CPU and 4 GiB, the same OS, V8/facade libraries
and probe. Input hashes differ only for the engine module and startup label.
This measures cold-load resident memory, not a browser page, peak consumption
or a fix for the ten-cycle growth. Both exact VMs were stopped after evidence
capture; no profile disk was attached.


The first two final links fail strict relocation-value verification in unwind
records. Renaming the input .eh_frame section to .aros_unwind before final
linking preserves its original layout and passes verification of every retained
absolute/relative relocation. No verifier check was removed. The packed module
has six sections, a 535,320,800-byte image and 763,135,912 file bytes. File sizes
are not RAM measurements. A small synthetic fixture also executes relative
calls/data references and a relocated function pointer on a Linux host CPU.
The small fixture does not reproduce the full image unwind mismatch or test
exception dispatch. Original full symbols remain retained for diagnosis.

The scripts retain private workspace paths as experimental evidence; they are
not a supported distribution build interface. A fresh compact image from197 is
queued separately, after its immutable symbol archive exists.

DevTools draft200 makes its main-task message-loop pointer task-local on AROS.
Verbatim production creation/destruction/continue methods with mocked platform
and debugger dependencies fail a controlled two-thread test before the patch
and pass afterward; actual source compiles on x86-64 and AArch64. The draft is
not applied to197 and has no native DevTools qualification yet.

Both architecture credits files were generated with Chromium's upstream license
scanner against the actual CEF GN dependencies. The included manifest records
those packaging inputs; it does not establish complete companion-library
notices. No release archive has been uploaded.
