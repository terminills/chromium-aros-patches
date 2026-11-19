# Renderer scope and shutdown correction candidates

Native x64 installed197 passed five icon metadata checks and launched from the actual drawer icon, then faulted during the first New Tab. The retained address resolves to `LayoutShiftTracker::ReattachHookScope::NotifyAttach`. Both layout-shift active stack pointers were image-global despite referring to renderer stack objects. Extracted production constructors/destructors reproduce sibling ownership corruption on the host; AROS-only task-local pointers pass ownership and nested restoration checks. Both architecture object compiles pass.

ARM71 painted the local JavaScript/Wasm/worker PASS page, but final shutdown failed. The captured stack is `SafeBuiltins::Reset` through queued `ScriptContext` deletion during scheduler shutdown, after the main isolate had been destroyed. Candidate202 retires the isolate after queue cleanup, with the scheduler object and compositor still alive. Focused host cases and both cross objects pass; native qualification remains pending.

The replay-checked `source` snapshot combines the197 baseline with DevTools200, shutdown202 and layout203 corrections. Full native builds and interactive tests are in progress. It is not an RC. Earlier failed native results are retained unchanged.

Drafts204 through210 are separate and NOT included in source203. They cover render guards, custom-layout scope ownership, DOM range updates, delayed scroll clamping, style mutation delivery, fullscreen/visibility and XML document ownership. Host tests execute extracted production scope code with mocked dependencies and controlled host-thread ordering; they do not establish native browser correctness. Before controls fail and candidates pass. Cross-compilation results are included only where completed.

Compact198 cold-load savings and long-run growth remain separate measurements. This snapshot does not claim a memory plateau, Vulkan/CDM qualification or physical Raspberry Pi validation.
