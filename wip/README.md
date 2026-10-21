# Development snapshots

These raw diffs are separate from the committed patch queues. `apply.sh` does
not apply them. Existing snapshots are retained for provenance, not promoted
to tested production changes as part of this publication.

`v8.diff` was refreshed from the saved October 21 capture-build baseline. It
applies after V8 source commit `6d2e20ee4379` and includes the resident-platform
selection and allocator-related changes present during that validation. Other
diffs are historical snapshots from the previous public export; their presence
does not establish that they apply to every current configuration.

Filenames encode repository paths with underscores (for example,
`net_third_party_quiche_src.diff`). `third_party_boringssl_src.diff` and
`third_party_sqlite_src.diff` target repositories without a committed queue in
`PINS`; prepare those from Chromium's DEPS before reviewing their snapshots.
`src.diff` is empty and retained from the original export.

Before applying a selected snapshot, inspect it and check it in the intended
repository with `git apply --check /path/to/snapshot.diff`. Do not apply all
snapshots blindly. The source queues plus these files are not a new full-stack
rebuild certification; the recorded runtime result belongs to the exact
October 21 artifact identified in the companion status document.
