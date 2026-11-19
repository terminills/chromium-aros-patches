from pathlib import Path
import subprocess,json
E=Path(__file__).parent;D=E/'scheduler-cleanup215-draft';rel='third_party/blink/renderer/platform/scheduler/main_thread/main_thread_scheduler_impl.cc'
def extract(text,signature):
 start=text.index(signature);pos=text.index('{',start);depth=1;end=pos+1
 while depth:
  depth+=(text[end]=='{')-(text[end]=='}');end+=1
 return text[start:end]
prefix='''#include <functional>
#include <memory>
#include <utility>
#include <cstdio>
#define BUILDFLAG(x) 1
namespace base {using TimeTicks=int;struct OnceClosure {std::function<void()> f;OnceClosure()=default;OnceClosure(std::function<void()> g):f(std::move(g)){}explicit operator bool()const{return bool(f);}void Run(){auto g=std::move(f);g();}};}
struct State{bool clock_alive=true,isolate_alive=true,queues_closed=false;int invalid_handles=0,invalid_clock=0,retired=0;};
struct ThreadSchedulerBase{void Shutdown(){}};
struct MainThreadSchedulerImpl:ThreadSchedulerBase {
State state;bool was_shutdown_=false;
struct Metrics {void OnRendererShutdown(int){}};
struct Observers{void Clear(){}};
struct Data{Metrics metrics_helper;void*message_pump=nullptr;Observers rail_mode_observers;}data;
Data& main_thread_only(){return data;}
struct Helper{State*p;void Shutdown(){p->clock_alive=false;}}helper_{&state};
struct Idle{void Shutdown(){}}idle_helper_;
void*sequence_manager_=nullptr;std::unique_ptr<int> owned_sequence_manager_;
base::TimeTicks NowTicks(){return 1;}
void ShutdownAllQueues(){if(!state.isolate_alive)++state.invalid_handles;state.queues_closed=true;}
void Retire(){if(!state.clock_alive)++state.invalid_clock;if(!state.queues_closed)++state.invalid_handles;state.isolate_alive=false;++state.retired;}
void Shutdown();void ShutdownWithCleanup(base::OnceClosure cleanup);
};
'''
results={}
for v in ['before','candidate']:
 text=(D/v/rel).read_text()
 if v=='before':body=extract(text,'void MainThreadSchedulerImpl::Shutdown() {');invoke='s.Shutdown();s.Retire();';repeat='s.Shutdown();'
 else:
  body=extract(text,'void MainThreadSchedulerImpl::ShutdownWithCleanup(base::OnceClosure cleanup) {').replace('\n#endif\n','\n',1);invoke='s.ShutdownWithCleanup(base::OnceClosure([&]{s.Retire();}));';repeat='s.ShutdownWithCleanup(base::OnceClosure([&]{s.Retire();}));'
 code=prefix+body+'\nint main(){MainThreadSchedulerImpl s;'+invoke+repeat+'''printf("invalid_handles=%d invalid_clock=%d retirements=%d final_clock_alive=%d\\n",s.state.invalid_handles,s.state.invalid_clock,s.state.retired,s.state.clock_alive);return s.state.invalid_handles==0&&s.state.invalid_clock==0&&s.state.retired==1&&!s.state.clock_alive?0:42;}'''
 p=D/(v+'-test.cc');p.write_text(code);subprocess.run(['c++','-std=c++20','-fsanitize=address,undefined',str(p),'-o',str(D/(v+'-test'))],check=True);r=subprocess.run([str(D/(v+'-test'))],capture_output=True,text=True);results[v]={'exit_code':r.returncode,'output':r.stdout+r.stderr};assert r.returncode==(42 if v=='before' else 0),results
(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Actual scheduler shutdown body, mocked queue destruction/clock/retirement. Verifies queue deletes before retirement, live clock during retirement, helpers close after, repeated shutdown does not retire twice. Not native Oilpan finalizer qualification.'},indent=2)+'\n');print(results)
