from pathlib import Path
import json,hashlib,difflib
E=Path(__file__).parent;D=E/'scheduler-cleanup215-draft';S=Path('/mnt/short-term/job0254-01a1e62b/src');D.mkdir(exist_ok=True);m={'files':{}};patch=''
paths=['third_party/blink/public/platform/scheduler/web_thread_scheduler.h','third_party/blink/renderer/platform/scheduler/common/web_thread_scheduler.cc','third_party/blink/renderer/platform/scheduler/main_thread/main_thread_scheduler_impl.h','third_party/blink/renderer/platform/scheduler/main_thread/main_thread_scheduler_impl.cc','content/renderer/render_thread_impl.cc']
for rel in paths:
 before=(S/rel).read_text();after=before
 if rel.endswith('public/platform/scheduler/web_thread_scheduler.h'):
  after=after.replace('#include "base/message_loop/message_pump.h"','#include "base/functional/callback.h"\n#include "base/message_loop/message_pump.h"')
  old='  virtual void Shutdown() = 0;';after=after.replace(old,old+'''\n#if BUILDFLAG(IS_AROS)
  // Release queued owners first, then run synchronous isolate cleanup while
  // scheduler clocks and helpers remain available to Oilpan finalizers.
  virtual void ShutdownWithCleanup(base::OnceClosure cleanup);
#endif''')
 elif rel.endswith('common/web_thread_scheduler.cc'):
  old='WebThreadScheduler::~WebThreadScheduler() = default;';after=after.replace(old,old+'''\n
#if BUILDFLAG(IS_AROS)
void WebThreadScheduler::ShutdownWithCleanup(base::OnceClosure cleanup) {
  NOTREACHED();  // Only the renderer main scheduler supports isolate cleanup.
}
#endif''')
 elif rel.endswith('main_thread_scheduler_impl.h'):
  old='  void Shutdown() override;';after=after.replace(old,old+'''\n#if BUILDFLAG(IS_AROS)
  void ShutdownWithCleanup(base::OnceClosure cleanup) override;
#endif''')
 elif rel.endswith('main_thread_scheduler_impl.cc'):
  old='void MainThreadSchedulerImpl::Shutdown() {';after=after.replace(old,'''void MainThreadSchedulerImpl::Shutdown() {
#if BUILDFLAG(IS_AROS)
  ShutdownWithCleanup(base::OnceClosure());
}

void MainThreadSchedulerImpl::ShutdownWithCleanup(base::OnceClosure cleanup) {
#endif''')
  old='  ShutdownAllQueues();\n\n  // Shut down |helper_| first';assert after.count(old)==1;after=after.replace(old,'''  ShutdownAllQueues();
#if BUILDFLAG(IS_AROS)
  if (cleanup)
    std::move(cleanup).Run();
#endif

  // Shut down |helper_| first''')
 else:
  old='''    main_thread_scheduler_->Shutdown();
    LOG(INFO) << "[Chromium:shutdown] AROS renderer scheduler stopped";
    // Queue teardown destroys deferred extension ScriptContexts and their V8
    // handles. Retire only after those deletes, while the scheduler object
    // and compositor still exist for synchronous Oilpan finalizers.
    blink::RetireMainThreadIsolateForAros();'''
  assert old in after;after=after.replace(old,'''    main_thread_scheduler_->ShutdownWithCleanup(base::BindOnce([] {
      // Queue deletion must precede isolate retirement; clocks and helper
      // state must survive the synchronous Oilpan finalizers it triggers.
      blink::RetireMainThreadIsolateForAros();
    }));
    LOG(INFO) << "[Chromium:shutdown] AROS renderer scheduler stopped";''')
 assert after!=before,rel
 for v,t in [('before',before),('candidate',after)]:
  p=D/v/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t)
 m['files'][rel]={'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()};patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
(D/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');(D/'candidate.patch').write_text(patch)
