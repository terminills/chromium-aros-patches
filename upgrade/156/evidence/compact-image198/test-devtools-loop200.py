from pathlib import Path
import subprocess,json,hashlib,difflib,re
E=Path(__file__).parent;D=E/'devtools-loop200-draft';D.mkdir(exist_ok=True);S=Path('/mnt/short-term/job0254-01a1e62b/src');rel=Path('third_party/blink/renderer/core/exported/web_dev_tools_agent_impl.cc');before=(S/rel).read_text()
a='  static ClientMessageLoopAdapter* instance_;';b='ClientMessageLoopAdapter* ClientMessageLoopAdapter::instance_ = nullptr;'
after=before.replace(a,'#if defined(__AROS__)\n  // The debugger and nested loop belong to this native renderer main task.\n  static thread_local ClientMessageLoopAdapter* instance_;\n#else\n'+a+'\n#endif').replace(b,'#if defined(__AROS__)\nthread_local '+b+'\n#else\n'+b+'\n#endif');assert before!=after
for variant,s in [('before',before),('candidate',after)]:
 p=D/variant/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
(D/'manifest.json').write_text(json.dumps({'files':{str(rel):{'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()}}},indent=2)+'\n');(D/'candidate.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+str(rel),tofile='b/'+str(rel))))
def method(anchor):
 start=before.index(anchor);pos=before.index('{',start);depth=1;end=pos+1
 while depth:
  depth+=(before[end]=='{')-(before[end]=='}');end+=1
 return before[start:end]
methods='\n'.join(method(a) for a in ['  ~ClientMessageLoopAdapter() override {','  static void EnsureMainThreadDebuggerCreated(v8::Isolate* isolate) {','  static void ContinueProgram() {'])
prefix='''#include <cassert>
#include <memory>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <cstdio>
#define DCHECK(x) assert(x)
namespace v8 {struct Isolate {int unused;};}
struct Platform {struct NestedMessageLoopRunner {int quits=0;void QuitNow(){++quits;}};static Platform* Current(){static thread_local Platform p;return &p;}std::unique_ptr<NestedMessageLoopRunner> CreateNestedMessageLoopRunner(){return std::make_unique<NestedMessageLoopRunner>();}};
struct MainThreadDebugger {struct ClientMessageLoop {virtual ~ClientMessageLoop()=default;};std::unique_ptr<ClientMessageLoop> loop;static MainThreadDebugger* Instance(v8::Isolate*){static thread_local MainThreadDebugger d;return &d;}void SetClientMessageLoop(std::unique_ptr<ClientMessageLoop> v){loop=std::move(v);}};
class ClientMessageLoopAdapter : public MainThreadDebugger::ClientMessageLoop {public:
'''
suffix='''
void QuitNow(){message_loop_->QuitNow();}int quits(){return message_loop_->quits;}
explicit ClientMessageLoopAdapter(std::unique_ptr<Platform::NestedMessageLoopRunner> p):message_loop_(std::move(p)){}
std::unique_ptr<Platform::NestedMessageLoopRunner> message_loop_;int running_for_debug_break_kind_=0;enum {kInstrumentationPause=1};
'''
main='''
std::mutex mutex;std::condition_variable cv;int phase=0;void set(int x){std::lock_guard<std::mutex> l(mutex);phase=x;cv.notify_all();}void wait(int x){std::unique_lock<std::mutex> l(mutex);cv.wait(l,[&]{return phase>=x;});}
int main(){bool second_created=false,first_created=false,reused=false;int quits=0;std::thread a([&]{v8::Isolate i;ClientMessageLoopAdapter::EnsureMainThreadDebuggerCreated(&i);auto*d=MainThreadDebugger::Instance(&i);first_created=bool(d->loop);auto*old=d->loop.get();ClientMessageLoopAdapter::EnsureMainThreadDebuggerCreated(&i);reused=d->loop.get()==old;set(1);wait(2);d->loop.reset();set(3);});std::thread b([&]{wait(1);v8::Isolate i;ClientMessageLoopAdapter::EnsureMainThreadDebuggerCreated(&i);auto*d=MainThreadDebugger::Instance(&i);second_created=bool(d->loop);set(2);wait(3);ClientMessageLoopAdapter::ContinueProgram();if(d->loop)quits=static_cast<ClientMessageLoopAdapter*>(d->loop.get())->quits();d->loop.reset();});a.join();b.join();printf("first=%d second=%d repeated_creation_reuses=%d sibling_continue_after_first_destroy=%d\\n",first_created,second_created,reused,quits);return first_created&&second_created&&reused&&quits==1?0:42;}
'''
results={}
for variant in ['before','candidate']:
 tls='thread_local ' if variant=='candidate' else '';code=prefix+methods+suffix+'static '+tls+'ClientMessageLoopAdapter* instance_;\n};\n'+tls+b+'\n'+main;p=D/(variant+'-test.cc');p.write_text(code)
 r=subprocess.run(['c++','-std=c++20','-fsanitize=address,undefined','-pthread','-g',str(p),'-o',str(D/(variant+'-test'))],capture_output=True,text=True);(D/(variant+'-build.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
 r=subprocess.run([str(D/(variant+'-test'))],capture_output=True,text=True);results[variant]={'exit_code':r.returncode,'output':r.stdout+r.stderr};(D/(variant+'-run.log')).write_text(r.stdout+r.stderr);assert r.returncode==(42 if variant=='before' else 0),results
(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Verbatim production EnsureMainThreadDebuggerCreated, ContinueProgram and destructor with mocked debugger, platform and nested loop; deterministic two-host-thread creation and destruction interleaving. Not a full DevTools or native test.'},indent=2)+'\n');print(results)
