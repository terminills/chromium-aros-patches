from pathlib import Path
import subprocess,json,difflib,hashlib
E=Path(__file__).parent;D=E/'event-queue194-draft';D.mkdir(exist_ok=True);S=Path('/mnt/short-term/job0254-01a1e62b/src');rel=Path('third_party/blink/renderer/core/dom/events/scoped_event_queue');manifest={'files':{}};patch=[]
for ext in ['.cc','.h']:
 before=(S/(str(rel)+ext)).read_text();token='ScopedEventQueue* ScopedEventQueue::instance_ = nullptr;' if ext=='.cc' else '  static ScopedEventQueue* instance_;';after=before.replace(token,'#if defined(__AROS__)\n'+('thread_local '+token if ext=='.cc' else token.replace('static ','static thread_local '))+'\n#else\n'+token+'\n#endif');assert after!=before
 for label,s in [('before',before),('candidate',after)]:
  p=D/label/(str(rel)+ext);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
 manifest['files'][str(rel)+ext]={'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()};patch+=difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+str(rel)+ext,tofile='b/'+str(rel)+ext)
(D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(D/'candidate.patch').write_text(''.join(patch))
M=D/'mocks';M.mkdir(exist_ok=True);(M/'mock.h').write_text('''#pragma once
#include <vector>
#include <memory>
#include <cassert>
#define CORE_EXPORT
#define USING_FAST_MALLOC(x)
#define STACK_ALLOCATED()
#define DCHECK(x) assert(x)
namespace base{template<class T>std::unique_ptr<T> WrapUnique(T* p){return std::unique_ptr<T>(p);}}
namespace blink{extern thread_local int owner;extern int wrong,dispatched;class Node{};struct EventTarget{Node node;Node* ToNode(){return &node;}};struct Event{int creator;EventTarget target;explicit Event(int n):creator(n){}EventTarget* RawTarget(){return &target;}};template<class T>struct Member{T* p;Member(T& x):p(&x){}T& operator*(){return *p;}};template<class T>using GCedHeapVector=std::vector<T>;template<class T>using HeapVector=std::vector<T>;template<class T>class Persistent{T* p;public:Persistent(T* x):p(x){}~Persistent(){delete p;}T* operator->(){return p;}T& operator*(){return *p;}};template<class T>T* MakeGarbageCollected(){return new T;}struct EventDispatcher{static void DispatchEvent(Node&,Event& e){++dispatched;if(e.creator!=owner)++wrong;}};}
''')
for name in ['third_party/blink/renderer/core/core_export.h','third_party/blink/renderer/core/dom/events/event.h','third_party/blink/renderer/platform/heap/collection_support/heap_vector.h','third_party/blink/renderer/platform/heap/persistent.h','third_party/blink/renderer/platform/wtf/vector.h','base/memory/ptr_util.h','third_party/blink/renderer/core/dom/events/event_dispatcher.h','third_party/blink/renderer/core/dom/events/event_target.h']:
 p=M/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('#include "mock.h"\n')
(D/'test.cc').write_text('''#include "third_party/blink/renderer/core/dom/events/scoped_event_queue.h"
#include <mutex>
#include <condition_variable>
#include <thread>
#include <cstdio>
namespace blink{thread_local int owner=0;int wrong=0,dispatched=0;}
std::mutex m;std::condition_variable cv;int phase=0;void set(int n){std::lock_guard<std::mutex> l(m);phase=n;cv.notify_all();}void wait(int n){std::unique_lock<std::mutex> l(m);cv.wait(l,[&]{return phase>=n;});}
int main(){using namespace blink;ScopedEventQueue *a=nullptr,*b=nullptr;Event ea(1),eb(2);std::thread ta([&]{owner=1;a=ScopedEventQueue::Instance();{EventQueueScope scope;a->EnqueueEvent(ea);set(1);wait(2);}});std::thread tb([&]{wait(1);owner=2;b=ScopedEventQueue::Instance();b->EnqueueEvent(eb);set(2);});ta.join();tb.join();bool isolated=a!=b;delete a;if(isolated)delete b;printf("separate_queues=%d wrong_renderer_dispatches=%d total_dispatches=%d\\n",isolated,wrong,dispatched);return isolated&&wrong==0&&dispatched==2?0:42;}
''')
results={}
for variant in ['before','candidate']:
 root=D/variant;args=['c++','-std=c++20','-D__AROS__','-fsanitize=address,undefined','-pthread','-g','-I'+str(root),'-I'+str(M),str(root/(str(rel)+'.cc')),str(D/'test.cc'),'-o',str(D/(variant+'-test'))];r=subprocess.run(args,capture_output=True,text=True);(D/(variant+'-build.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
 r=subprocess.run([str(D/(variant+'-test'))],capture_output=True,text=True);(D/(variant+'-run.log')).write_text(r.stdout+r.stderr);results[variant]={'exit_code':r.returncode,'output':r.stdout+r.stderr};assert r.returncode==(42 if variant=='before' else 0),results
(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Actual ScopedEventQueue source/header with mocked DOM and GC dependencies; deterministic host interleaving proves event queued/dispatched on wrong renderer. Does not qualify native GC lifetime or browser runtime. Candidate remains unapplied.'},indent=2)+'\n');print(results)
