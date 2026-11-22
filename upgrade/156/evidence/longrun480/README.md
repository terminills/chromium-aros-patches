# Hundred-cycle baseline: source444 / native445

All100 pages and renderer retirements completed, none deferred, with no native fault and all terminal markers present. The independent disk ledger contains102 matching child entry/zero-exit pairs. Original strict results failed because the serial DETAIL record for child1426 was split between digits142 and6 by an unrelated line; the parser inferred a phantom142. The separate corrected audit retains the exact fragment and raw serial hash and reconciles it with complete E/X1426 records and the native disk files. Original failed results remain unchanged. The failure prevented the post-host full-memory dump; the earlier allocator snapshot was retained.

Memory plateau fails. Whole native QEMU guest use is1062.683MiB atcycle10,1099.369MiB atcycle30 and1260.684MiB atcycle100. After host exit it remains1114.195MiB. Growth30→100 is161.315MiB. This is not browser RSS.

The post-host allocator snapshot contains73 reservations backed by284.219MiB of Exec memory, exposing141.719MiB. Thirty-cycle438 and465 snapshots are included only as different-generation context, not a matched optimization comparison. Native task snapshots show three added Chromium workers fromcycle30 to100 with6MiB of stack address extents; this does not explain all guest growth or establish physically committed stack size.

These results apply to source444/native445, not current source462/native463 or the private source468/native469 cleanup candidate. No RC acceptance is implied.
