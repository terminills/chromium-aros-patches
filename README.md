# chromium-aros-patches

The changes that make Chromium 124.0.6367.0 build and run on AROS, as a patch
queue: one directory per repository in the Chromium checkout (`src` is the
checkout itself; `v8`, `cef`, `third_party/...` are its sub-repositories).

- `PINS` — repository path, upstream URL, and the upstream commit its queue
  applies to.
- `<path>/series` — the order to apply that directory's patches in.
- `<path>/*.patch` — one change each, in `git format-patch` form.
- `wip/` — edits not yet turned into patches.
- `apply.sh <chromium-src>` — checks out every pinned commit and applies the
  queues with `git am`.

## Changing a patch

Apply the queue, make the change as a commit on the `aros` branch of the
repository concerned, regenerate that directory with
`git format-patch <base>..aros -o <path>` and update `series`. Keep one change
per patch; describe what it fixes and why AROS needs it.

The AROS libraries that use this tree live in
[aros-web](https://github.com/terminills/aros-web), which records the exact
commits it builds against in `build/chromium.pin`.
