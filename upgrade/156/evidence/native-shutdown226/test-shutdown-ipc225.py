from pathlib import Path
import hashlib,json,difflib,subprocess
E=Path(__file__).parent;D=E/'shutdown-ipc225-draft';D.mkdir(exist_ok=True);S=Path('/mnt/short-term/job0254-01a1e62b/src');rel='third_party/blink/renderer/platform/scheduler/main_thread/main_thread_task_queue.cc';before=(S/rel).read_text();needle="""  // We use the frame_scheduler_ to track metrics so as to ensure that metrics
  // are not tied to individual task queues.
  on_ipc_task_posted_callback_handle_ = task_queue_->AddOnTaskPostedHandler(""";assert before.count(needle)==1
after=before.replace(needle,"""#if BUILDFLAG(IS_AROS)
  // Native renderer retirement runs Oilpan finalizers after queued V8 owners
  // have been deleted. Removing the last PageScheduler can enable IPC tracking
  // again, but a shut-down queue cannot accept a new task-posted handler.
  if (!task_queue_)
    return;
#endif
"""+needle)
for v,t in [('before',before),('candidate',after)]:
 p=D/v/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t)
(D/'manifest.json').write_text(json.dumps({'files':{rel:{'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()}}},indent=2)+'\n');(D/'candidate.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)))
def method(t):
 a=t.index('void MainThreadTaskQueue::SetOnIPCTaskPosted(');b=t.index('{',a);n=1;i=b+1
 while n:n+=(t[i]=='{')-(t[i]=='}');i+=1
 return t[a:i]
prefix="""#include <functional>
#include <utility>
#include <cstdio>
#include <stdexcept>
#define BUILDFLAG(v) 1
namespace base {template<class T>using RepeatingCallback=std::function<T>;namespace sequence_manager{struct Task{};}}
struct Queue {int calls=0;int AddOnTaskPostedHandler(base::RepeatingCallback<void(const base::sequence_manager::Task&)> callback){++calls;return calls;}};
struct CheckedPointer {Queue* p;explicit operator bool()const{return p;}Queue*operator->(){if(!p)throw std::runtime_error("null queue accessed after shutdown");return p;}};
struct MainThreadTaskQueue {CheckedPointer task_queue_;int on_ipc_task_posted_callback_handle_=0;void SetOnIPCTaskPosted(base::RepeatingCallback<void(const base::sequence_manager::Task&)>);};
"""
test="""int main(){Queue queue;MainThreadTaskQueue wrapper{{&queue}};int errors=0;wrapper.SetOnIPCTaskPosted({});wrapper.SetOnIPCTaskPosted({});if(queue.calls!=2||wrapper.on_ipc_task_posted_callback_handle_!=2)++errors;wrapper.task_queue_.p=nullptr;try{wrapper.SetOnIPCTaskPosted({});}catch(const std::runtime_error&){++errors;}if(queue.calls!=2)++errors;printf("closed-queue handler errors=%d\\n",errors);return errors?42:0;}
"""
results={}
for v,t in [('before',before),('candidate',after)]:
 p=D/(v+'.cc');p.write_text(prefix+method(t)+test);exe=D/(v+'-test');subprocess.run(['c++','-std=c++20','-fsanitize=address,undefined',str(p),'-o',str(exe)],check=True);r=subprocess.run([str(exe)],capture_output=True,text=True);results[v]={'exit_code':r.returncode,'output':r.stdout+r.stderr};assert r.returncode==(42 if v=='before' else 0),results
(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Actual IPC handler setter with checked fake queue pointer. Normal live registration/replacement preserved, finalizer-time registration after queue reset rejected. Host-only focused regression; native217 fault is exact SetOnIPCTaskPosted null dereference, both affected stacks retained.'},indent=2)+'\n');print(results)
