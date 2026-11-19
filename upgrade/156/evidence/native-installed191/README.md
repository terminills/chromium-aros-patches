# Installed native browser191 and remaining renderer failure

The native x64 icon launches Chromium with `Developer:` removed and resources under `SYS:System/CEF`. First New Tab and four New Tabs paint correctly. Resource packs match the former location byte for byte. Companion `6499b2e` adds the installed resource path; both architecture helpers cross-link.

Navigating the fourth tab to `chrome://version` then fails a compositor vector bounds check (index 4294967295, size14). This run is **not** full interactive acceptance. The exact engine and stack symbols are retained. The screenshot named version shows the aborted renderer; it does not show a successful version page.

The complete21-repository source191 snapshot replays onto its recorded bases. It includes task-local CEReactionsScope, which passes a fail-before/pass-after host concurrency test and gets past the initial constructor fault in this run.

Four separately tested **unapplied** candidates are included as deltas for the subsequent197 build: custom-element construction nesting, scoped event queue, active style scope and paint-tree sequence. Their host evidence identifies the tested boundaries; mocks and the paint-sequence model are not native compositor qualification. Both architectures compile each isolated candidate object. The197 pipeline waits for the frozen ARM71 binary and staged input manifest before applying these changes.

No release candidate is published. Memory plateau, final lifecycle/isolation, ARM acceptance and final packaging remain required.
