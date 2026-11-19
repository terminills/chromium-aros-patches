# Native teardown and calculation ownership follow-up

Native203 passes actual icon launch, complete New Tab, four tabs and chrome://version. All four browser close callbacks drain and a second client reconnects to the same resident engine owner. It nevertheless FAILS native acceptance: two renderer tasks then fault in `base::LazyNow::Now`, called by `PageSchedulerImpl::UpdateWakeUpBudgetPools`. Reopening faults in `CalculationValueHandleMap::DecrementCount`. That stripped-engine section was matched byte-for-byte to the retained full-symbol ELF; do not infer the same section number after stripping.

Candidate215 adds an AROS renderer-scheduler cleanup callback after queued owners are deleted but before clocks/helpers and the sequence manager disappear. Candidate216 makes the wrapper containing the calculation map Persistent belong to its logical renderer. The generic Persistent-only singleton trait could not detect this embedded heap root. Both changes reproduce their failure conditions in focused host fixtures and pass the corresponding candidates; both architecture object compiles pass. These are mocked-dependency host checks, not native Oilpan qualification.

The complete21-repository217 snapshot includes the separately tested204–210 scope corrections plus215/216. Partial212 build outputs were retained; its exact build processes exited before217 source application. Full217 builds are in progress. No RC is published. The source snapshot has replay checks; use its PINS and manifest rather than the historical root124 queue.

ARM72 passes five native icon metadata checks and displays the installed drawer. Injected QEMU USB mouse events have no visible effect, so72 does not establish icon activation or browser startup. The separately compiled native input.device diagnostic in73 tests a different input boundary; it does not qualify USB. Earlier ARM browser/worker evidence remains separately labelled.

The supplied renderer-scope stress page has JavaScript syntax validation only so far. It is intended for simultaneous A/B renderer tests; no native result is claimed.
