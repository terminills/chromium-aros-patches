# Chromium 156 AROS migration snapshot

Snapshot **724** targets Chromium **156.0.8078.96 / CEF 8078**. It is in progress,
not an RC. The repository root queues retain Chromium 124.

The manifest contains patches for 22 modified repositories, including Chromium,
CEF, V8 and FFmpeg. Each patch was replayed against its exact recorded commit in
an independent Git index. SHA-256 values and resulting Git trees are recorded.
Unchanged dependencies follow Chromium DEPS; CEF is an additional src/cef checkout.

Apply each manifest patch in its corresponding recorded repository. Do not layer
the Chromium 124 queues or historical Chromium delta patches over this snapshot.
The separately documented AROS OS prerequisites still apply; they are not part
of these Chromium repository patches.

This snapshot adds the native FFmpeg task adapter and configuration, preserves
AROS static large-model flags, and makes the CDM module local to each logical
native process with exit cleanup. It retains the shared engine code image and
2 MiB PartitionAlloc superpages. See [current media evidence](../evidence/media729/README.md)
for tested build identities and unresolved DRM/session failures.

Only matched companion modules should be loaded. QEMU tests do not establish
physical-device qualification or commercial streaming-service compatibility.
