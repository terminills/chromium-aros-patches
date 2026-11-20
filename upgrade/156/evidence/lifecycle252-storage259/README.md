# Lifecycle candidate252 and SQLite storage fix259

This is development evidence, not an RC release. Candidate252 contains the complete replay-checked 21-repository source snapshot. Its x64 controlled rebuild and ARM new-SDK rebuild are still in progress at publication. Candidate259 is a separate, unapplied SQLite adapter; it is not included in source252.

After the ten-cycle226 baseline revealed retained renderer metrics, retirement candidate239 exposed cached histogram pointers. Candidate249 scopes the V8 accumulator per logical renderer and moves retirement until after delegate and thread-local teardown. Native249 still faults on its second renderer in `blink::CustomCountHistogram::CountMicroseconds`. Candidate252 scopes these static wrappers per logical renderer. Focused host regressions and x64/ARM object compiles pass; full native acceptance is pending. Earlier226 lifecycle success must not be attributed to252.

The isolated native SQLite255 test passes ordinary database writes, backup and reopen on RAM and FAT. Enabling Chromium's TRUNCATE journal mode in257 reproduces the browser's exact SQLite778 / errno1219 failure on FAT, with zero inserted rows; RAM succeeds. A pretruncate cursor clamp258 passes. The production-form SQLite-only259 adapter also passes native260 with alternating write sizes, backup and reopen, preserving all16 rows on RAM and FAT. Its VFS object compiles for both architectures. These probes use Chromium's actual SQLite and native lock/path adapters, with ICU disabled. They are not a full browser profile replay.

The workaround moves SQLite's descriptor cursor inside the new extent before shrinking. SQLite's Unix VFS seeks explicitly for subsequent reads and writes. No SDK function is replaced. The retained source analysis identifies a FAT/posixc cursor interaction; general OS semantics remain outside this local workaround.

Fresh master x64 boots to its desktop independently. The full new-SDK ARM engine build is underway; no fresh-master browser completion is claimed. The companion production compact linker is published at aros-web commit77a301c523ed37b2140264e564cd24f29389c2ba.

The static ELF TLS inventory is not a runtime leak measurement. It must not be used to explain the measured resident memory growth without further evidence. See release-candidate-gates.json for remaining qualification limits.
