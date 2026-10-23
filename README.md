# Chromium for AROS — patch queues

This repository carries the AROS port of **Chromium 124.0.6367.0** as ordered
Git patches for Chromium, V8, CEF and their dependencies. It contains the port,
not a complete Chromium checkout or a browser binary.

The October 21, 2026 export includes native Intuition/Ozone integration,
AROSTCP networking, AHI audio, VHI camera capture, memory-management changes,
and the ANGLE GL backend work. Chromium itself is still version 124; user-agent
compatibility settings do not upgrade the engine. The Chromium upgrade and
broader shared-engine consolidation are later work.

The companion [aros-web](https://github.com/terminills/aros-web) repository
contains the AROS libraries, runtime adapters, build tooling and launchers.

## What is here

| Path | Purpose |
| --- | --- |
| `PINS` | Upstream URL and exact base commit for each repository |
| `EXPORT.json` | Source tips, source/export Git trees and patch counts for this export |
| `src/series` | Ordered patches for the Chromium `src` repository |
| `v8/`, `cef/`, `third_party/`, `net/` | Queues for separate dependency repositories |
| `wip/` | Uncommitted development snapshots, separate from the queues |
| `apply.sh` | Apply the committed queues to a prepared checkout |

The source queue now has 689 patches, ending at source commit
`c15a9e09b9` (the last executable capture change is `ee28c35907`). See
[the export manifest](EXPORT.json) for full hashes and dependency revisions.

## Prepare and apply

Use a Linux host with Git, Bash, Chromium's `depot_tools`, adequate disk space,
and the ADT AROS cross-toolchain/SDK for the eventual build. First prepare a
Chromium checkout at the `src` base in `PINS`, including its dependency
repositories and build tools. A patch queue alone does not download Chromium's
DEPS, CIPD packages or GN/Ninja tools.

```sh
git clone https://github.com/terminills/chromium-aros-patches.git
cd chromium-aros-patches
./apply.sh /absolute/path/to/chromium/src
```

Use a dedicated checkout. The script checks every repository before applying:
tracked edits, an in-progress Git operation, or an existing `aros` branch cause
it to stop. It creates an `aros` branch at each pinned base, then runs `git am`
in `series` order. Missing base objects are fetched from the listed upstream.
On a patch failure, inspect that repository's `git status`; the script leaves
the interrupted `git am` available for inspection or `git am --abort`.
It does not roll back repositories already applied.

Replaying patches creates new commit IDs. Compare Git **tree** IDs with
`EXPORT.json` to check source equivalence against `export_tree`. The Chromium queue intentionally
omits `test-artifacts/` (private development logs and screenshots), as did the
original export; `excluded_paths` records this distinction from `source_tree`.
`aros-web/build/chromium.pin` records
the original development commit IDs and may warn about a replayed checkout.
Do not run `gclient sync` blindly after patching: it can restore dependency
checkouts to the unpatched DEPS revisions.

The script deliberately does **not** apply `wip/*.diff`. Read
[the snapshot notes](wip/README.md) before using those deltas. A queue-only tree
must not be described as a byte-for-byte reproduction of the tested binary.

## Build and run

Follow the companion [build guide](https://github.com/terminills/aros-web/blob/main/build/README.md).
The native browser and CEF archive use different GN configurations; a successful
browser build does not prove that the Electron/CEF configuration also builds.
Keep the SDK, compiler, V8 library and browser revisions matched.

The tested browser configuration uses software rendering and single-process
mode. It is a development port; process sandboxing and full application
isolation are not established by the current shared-library implementation.

### AArch64 target

`target_cpu = "arm64"` builds for AArch64 AROS with the AROS LLVM toolchain
(clang `--target=aarch64-unknown-aros`, linked through `collect-aros`)
instead of GCC. Set `aros_clang_root` to the directory holding `clang`,
`clang++` and the `llvm-*` tools, `aros_tool_dir` to the directory holding
`collect-aros` (an AROS build's `bin/<host>/tools`), and `aros_sysroot` to
the AArch64 SDK (`bin/<target>/AROS/Developer`). Standalone V8 builds and
runs JavaScript on AArch64 AROS with this toolchain (jitless); Blink, CEF
and the browser have not been built for arm64.

## Camera and microphone status

Native ADT AROS Chromium captured a real UGREEN Camera 2K through VHI and its
48 kHz stereo microphone through AHI in QEMU USB passthrough. Five combined
sessions and four stop/reopen cycles passed, as did missing-camera reporting
and a separate video-with-audio playback check. The OS must also contain the
matching UVC/VHI, USB audio, JPEG and xHCI components; browser patches alone
cannot provide those drivers.

Preview performance remains low and variable: a longer session displayed
175 frames over 226 seconds (about 0.77 fps). This is functional capture proof,
not smooth streaming, Twitch, A/V synchronization or bare-metal validation.
See [the dated status](https://github.com/terminills/aros-web/blob/main/docs/status.md)
for the exact scope and artifact hash.

## Maintaining the queues

Keep each dependency's patches in its own directory. Append changes exported
with `git format-patch --start-number <next> <old-tip>..<new-tip>` and update its
`series`; update `EXPORT.json` with the base, source tip and resulting tree.
Replay the full series against the pinned base before publishing:

```sh
python3 tools/verify-queues.py /absolute/path/to/chromium/src
```

This uses temporary Git indexes and compares the resulting trees with the
manifest. It requires the base objects locally and writes reconstructed Git
objects, but does not change checkout files, branches or the normal index.
Do not mix
uncommitted local changes into a committed-source export without identifying
them separately.

## Licensing

Original source and patches retain their upstream copyright and license
notices. Chromium and its dependencies have multiple licenses; this repository
does not relicense them. Review the corresponding upstream source licenses
and redistribution requirements when building a package. Proprietary media
components are not provided here.
