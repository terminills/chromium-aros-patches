# Native credentials validation on fresh master

Both native x64 and AArch64 AROS tests pass with the rebuilt credentials library:
synthetic storage round trips, collection separation, read-only enforcement,
explicit lock/unlock, and preservation of an intentionally corrupt seed.
Each test uses disposable RAM storage through its own ENVARC assignment. No
browser profiles or real account material are used. The private VMs were stopped
after retaining the results. Chromium profile integration remains pending.

The matching host crypto comparison against OpenSSL and name-isolation tests
also pass with address and undefined-behavior sanitizers. Host tests do not
substitute for the native results above.

## SDK prerequisite

Generate and build these targets before exporting an AROS SDK for Chromium:

```
make -j1 workbench-libs-credentials-includes
make -j1 workbench-libs-credentials
```

The minimal SDK exports retained the public credentials header but omitted the
generated prototype/inline headers and import library. The preflight failure is
retained. Build 303 supplies those prerequisites from AROS commit
`4565772181852b838c67dac94186d7788585f64f`.

Completion 304 paused the exact active compiler trees, verified every original
SDK file against its recorded hash (20,583 x64 files and 19,531 ARM files), added
seven missing files to each sysroot, passed both header preflights, then resumed
the same compiler processes. No original SDK file or Chromium source was
changed. Existing sysroot paths were retained so valid completed objects could
be reused. The original public header was kept byte-for-byte; the initial guard
refusal and recovery are recorded.

The package inventory now requires credentials.library and verifies its target
ELF architecture. Existing AROS runtime notices match fresh master byte-for-byte.
These tests establish the existing native keyring API behavior; they do not
establish a new security boundary or complete browser sign-in qualification.
See the [RC gates](release-candidate-gates.json); no RC release is implied.
