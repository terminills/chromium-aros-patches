from pathlib import Path
import hashlib,difflib,json,subprocess
E=Path(__file__).parent;D=E/'isolate-order202-draft';D.mkdir(exist_ok=True);S=Path('/mnt/short-term/job0254-01a1e62b/src');rel=Path('content/renderer/render_thread_impl.cc');before=(S/rel).read_text();needle='  if (main_thread_scheduler_)\n    blink::RetireMainThreadIsolateForAros();\n';assert before.count(needle)==1;after=before.replace(needle,'')
needle='    LOG(INFO) << "[Chromium:shutdown] AROS renderer scheduler stopped";\n'
assert after.count(needle)==1;after=after.replace(needle,needle+'''    // Queue teardown destroys deferred extension ScriptContexts and their V8
    // handles. Retire only after those deletes, while the scheduler object
    // and compositor still exist for synchronous Oilpan finalizers.
    blink::RetireMainThreadIsolateForAros();
''')
for variant,source in [('before',before),('candidate',after)]:
 p=D/variant/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(source)
(D/'manifest.json').write_text(json.dumps({'files':{str(rel):{'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()}},'native_evidence':'arm71-fault-symbols.txt: SafeBuiltins::Reset <- ScriptContext::~ScriptContext <- queued DeleteHelper destruction <- ShutdownAllQueues after completed isolate retirement.'},indent=2)+'\n')
(D/'candidate.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+str(rel),tofile='b/'+str(rel))))
prefix='''#include <memory>
#include <cstdio>
#include <cassert>
#define BUILDFLAG(x) 1
struct Sink {template<class T> Sink& operator<<(T&&){return *this;}} sink;
#define LOG(x) sink
struct State {bool isolate_live=true,pending_page=false,scheduler_alive=true,compositor_alive=true;int contexts=1,invalid_resets=0,retired=0;} state;
namespace blink {void LogStatsDuringShutdown(){} bool RetireMainThreadIsolateForAros(){assert(state.scheduler_alive&&state.compositor_alive);if(state.pending_page)return false;state.isolate_live=false;++state.retired;return true;}void ShutdownCompositorThread(){assert(state.contexts==0);state.compositor_alive=false;}}
struct Scheduler {void Shutdown(){if(!state.isolate_live)state.invalid_resets+=state.contexts;state.contexts=0;state.pending_page=false;}~Scheduler(){state.scheduler_alive=false;}};
struct GPU {~GPU(){++state.contexts;}};
struct ChildThreadImpl {void Shutdown(){}};
struct RenderThreadImpl:ChildThreadImpl {std::unique_ptr<Scheduler> main_thread_scheduler_=std::make_unique<Scheduler>();std::unique_ptr<GPU> gpu_=std::make_unique<GPU>();bool blink_platform_impl_=true;bool IsSingleProcess(){return false;}void Shutdown();};
'''
main='''
int main(){bool good=true;for(bool pending:{false,true}){state=State{};state.pending_page=pending;{RenderThreadImpl r;r.Shutdown();printf("pending_page=%d invalid_handle_resets=%d retired=%d scheduler_object_alive=%d\\n",pending,state.invalid_resets,state.retired,state.scheduler_alive);good&=state.invalid_resets==0&&state.retired==1&&state.scheduler_alive;}assert(!state.scheduler_alive);}return good?0:42;}
'''
results={}
for variant,source in [('before',before),('candidate',after)]:
 start=source.index('void RenderThreadImpl::Shutdown() {');end=source.index('\nbool RenderThreadImpl::ShouldBeDestroyed()',start);method=source[start:end];p=D/(variant+'-test.cc');p.write_text(prefix+method+main)
 r=subprocess.run(['c++','-std=c++20','-fsanitize=address,undefined','-g',str(p),'-o',str(D/(variant+'-test'))],capture_output=True,text=True);(D/(variant+'-build.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
 r=subprocess.run([str(D/(variant+'-test'))],capture_output=True,text=True);results[variant]={'exit_code':r.returncode,'output':r.stdout+r.stderr};(D/(variant+'-run.log')).write_text(r.stdout+r.stderr);assert r.returncode==(42 if variant=='before' else 0),results
(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Actual RenderThreadImpl::Shutdown body with mocked GPU, scheduler queue deletes, isolate and compositor. Tests pending extension handles and pending page release; does not prove all Oilpan finalizers tolerate a stopped scheduler. Native replay required.'},indent=2)+'\n');print(results)
