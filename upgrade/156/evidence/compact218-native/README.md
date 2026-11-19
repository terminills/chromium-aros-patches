# Compact engine native browser evidence

The compact image derived from source217 launches through the installed native AROS icon, paints New Tab and navigates to chrome://version in an isolated x64 QEMU guest. The image retains the known source217 renderer shutdown failure: this is initial browser qualification only, not RC acceptance. Source226 builds contain the subsequent shutdown correction and require separate native testing.

Whole-guest memory was 38.15 MiB before host startup and 1889.0 MiB at the 240-second sample. These RAM-profile samples are not a matched comparison against the disk-profile noncompact test. The earlier matched bare-engine loading comparison is separate.

Read-only allocator snapshots resolve the resident image through two library vectors and walk 402 allocation records. Exec backing totals 477614080 bytes, exposed spans total 269688832 bytes, and retained alignment slack totals 207925248 bytes. These are allocator spans, not total browser live heap or a proven recoverable memory saving. Partial frees remain intentionally avoided. Multiple native child entries use the same facade/allocator/free pointers; this demonstrates shared address-space engine use, not a security sandbox.

The separate AROS source worktree merged upstream master b6dcaeeaa2724bbe4f6d9510c1ada4b8f69789fb cleanly as 89fa9bedd2dbc1bde55853eddad2799719cabc15. It has not yet been rebuilt or booted. Existing source226 builds keep their original frozen SDK/runtime inputs. The private two-core ARM boot control is recorded separately and is not represented as upstream behavior.
