# Native resident CEF host — 2026-11-18

Source: aros-web `19673b1`. Native x64 replay86 passed; ARM libraries and clients
cross-link, with ARM runtime20 evaluated separately. No SDK or kernel changes.

CEFHost owns initialization and the normal native AROS CEF message loop.
The resident cef.library version-3 transport serializes posting and withdrawal
with an Exec semaphore. The host captures an explicit CEF UI task runner and
posts through that object: generic CEFPostTask deliberately selects an engine
through the caller's owner/parent chain and cannot route independent apps.
Existing version-2 vectors are unchanged. cef.library v3 requires cef-blink v3.

Replay86 verifies three distinct native application tasks use the same engine
owner. A and B overlap; A exits while B remains connected; both exit; C connects
to the same still-running owner. Duplicate host startup is rejected without
shutting down the existing engine. Invalid protocol, invalid profile name,
foreign-session close and stop-while-active checks pass. Only the explicit final
diagnostic stop with zero sessions shuts down CEF, and shutdown returns.
The screenshot displays these results; the serial and exact input hashes are
retained. Some concurrent serial messages interleave, so the foreground console
also records the final stop result. The launch scripts used a stack slightly
above 1 MiB; this is not a stack-size optimization measurement.

This qualifies session lifetime and cross-task transport, not browser callback
unloading, persistent-profile durability, crash recovery, sandbox security, or
complete Chromium/CEF conformance. Protocol 1 requires orderly client teardown.
Actual browser clients are a separate subsequent integration step.

Failed initial fixtures are retained privately: missing PROFILE: caused a DOS
requester during initialization; after correcting the fixture, generic task
posting returned unavailable from independent tasks. The explicit runner fixes
the latter without weakening owner isolation. The x64 engine retains the prior
section-name compaction and 2 MiB superpages. ARM retains compact-image packaging.
