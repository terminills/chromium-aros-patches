# Native shutdown226 candidate

Installed217 renders New Tab, four tabs and chrome://version from the native Wanderer icon. It fails after all browser callbacks close: two renderer tasks fault in MainThreadTaskQueue::SetOnIPCTaskPosted because the underlying task queue has already been reset. The captured stack contains removal of an SVG PageScheduler. The scheduler-clock lifetime fix moved retirement to a point with a live clock, but that point is after queue destruction. Reopening was not attempted after these faults.

Candidate225 makes the AROS handler setter ignore registration on a closed queue. Focused actual-method host checks fail before and pass after; both architecture objects compile. Source226 also includes219/220 renderer ownership fixes. Its complete21-repository source replay passes; full native builds are underway. Native acceptance is pending, not a release claim.

ARM73 native icon metadata and activation through input.device pass, but full browser paint is incomplete. That VM was stopped after retaining exact logs/registers and the offline disk digest. Earlier CPU sampling interpretation was corrected. ARM74 will use226 and a native keymap/input diagnostic for navigation; this does not qualify the USB input path.

The release inventory checks22 allowlisted installed x64 files including native icons, library/helper architecture, resources and upstream credits. It omits profiles and test startup files. Companion notices and final candidate packaging are still pending. The supplied paths refer to retained private evidence/build trees; binary artifacts are not in this source publication.
