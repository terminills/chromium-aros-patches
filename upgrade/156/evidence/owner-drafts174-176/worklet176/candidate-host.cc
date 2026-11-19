#include <cassert>
#include <new>
#include <cstdio>
#include <memory>
#include <functional>
#include <vector>
std::vector<std::function<void()>> queued;
void DrainTasks(){while(!queued.empty()){auto f=queued.front();queued.erase(queued.begin());f();}}
#include "third_party/blink/renderer/platform/wtf/std_lib_extras.h"
#define GUARDED_BY(...)
#define FROM_HERE 0
namespace base::aros {thread_local uint64_t owner=1;uint64_t CurrentProcessIdentity(){return owner;}}
namespace base { struct WaitableEvent { bool ready=false;void Wait(){DrainTasks();assert(ready);}void Signal(){ready=true;} }; }
namespace blink {
bool IsMainThread(){return true;}
struct ThreadCreationParams {};
struct WorkerBackingThreadStartupData {static int CreateDefault(){return 0;}};
int initialized=0,stopped=0,destroyed=0;
struct WorkerBackingThread {
 uint64_t owner=base::aros::owner;explicit WorkerBackingThread(const ThreadCreationParams&){}
 ~WorkerBackingThread(){++destroyed;}
 struct Runner{int runner=0;int* GetTaskRunner(){return &runner;}} runner;
 Runner& BackingThread(){return runner;}
 void InitializeOnBackingThread(int){assert(owner==base::aros::owner);++initialized;}
 void ShutdownOnBackingThread(){assert(owner==base::aros::owner);++stopped;}
};
template<class T>T* CrossThreadUnretained(T* p){return p;}
template<class F,class...A>auto CrossThreadBindOnce(F f,A...a){return [=]{std::invoke(f,a...);};}
template<class F>void PostCrossThreadTask(int&,int,F f){queued.push_back(f);}
}
namespace blink {

// WorkletThreadHolder is a template class which is designed for per-process
// singleton instance of DerivedWorkletThread (i.e. AnimationWorkletThread,
// AudioWorkletThread).
template <class DerivedWorkletThread>
class WorkletThreadHolder {
 public:
  static WorkletThreadHolder<DerivedWorkletThread>* GetInstance() {
    base::AutoLock locker(HolderInstanceLock());
    return HolderInstance();
  }

  static void EnsureInstance(const ThreadCreationParams& params) {
    DCHECK(IsMainThread());
    base::AutoLock locker(HolderInstanceLock());
    if (HolderInstance())
      return;
    HolderInstance() = new WorkletThreadHolder<DerivedWorkletThread>;
    HolderInstance()->Initialize(
        std::make_unique<WorkerBackingThread>(params));
  }

  static void ClearInstance() {
    DCHECK(IsMainThread());
    base::AutoLock locker(HolderInstanceLock());
    if (HolderInstance()) {
      HolderInstance()->ShutdownAndWait();
      delete HolderInstance();
      HolderInstance() = nullptr;
    }
  }

  WorkerBackingThread* GetThread() { return thread_.get(); }

 private:
  WorkletThreadHolder() = default;
  ~WorkletThreadHolder() = default;

  static WorkletThreadHolder<DerivedWorkletThread>*& HolderInstance() {
#if BUILDFLAG(IS_AROS)
    // The resident engine shares code, not a backing thread across renderers.
    struct HolderOwnerTag;
    return base::aros::ProcessLocalValue<
        WorkletThreadHolder<DerivedWorkletThread>*, HolderOwnerTag>();
#else
    return thread_holder_instance_;
#endif
  }

  static base::Lock& HolderInstanceLock() {
    DEFINE_THREAD_SAFE_STATIC_LOCAL(base::Lock, holder_lock, ());
    return holder_lock;
  }

  void Initialize(std::unique_ptr<WorkerBackingThread> backing_thread) {
    thread_ = std::move(backing_thread);
    PostCrossThreadTask(
        *thread_->BackingThread().GetTaskRunner(), FROM_HERE,
        CrossThreadBindOnce(&WorkletThreadHolder::InitializeOnWorkletThread,
                            CrossThreadUnretained(this)));
  }

  void InitializeOnWorkletThread() {
    base::AutoLock locker(HolderInstanceLock());
    thread_->InitializeOnBackingThread(
        WorkerBackingThreadStartupData::CreateDefault());
  }

  void ShutdownAndWait() {
    DCHECK(IsMainThread());
    base::WaitableEvent waitable_event;
    PostCrossThreadTask(
        *thread_->BackingThread().GetTaskRunner(), FROM_HERE,
        CrossThreadBindOnce(&WorkletThreadHolder::ShutdownOnWorkletThread,
                            CrossThreadUnretained(this),
                            CrossThreadUnretained(&waitable_event)));
    waitable_event.Wait();
  }

  void ShutdownOnWorkletThread(base::WaitableEvent* waitable_event) {
    thread_->ShutdownOnBackingThread();
    waitable_event->Signal();
  }

  std::unique_ptr<WorkerBackingThread> thread_;

  static WorkletThreadHolder<DerivedWorkletThread>* thread_holder_instance_;
};

template <class DerivedWorkletThread>
WorkletThreadHolder<DerivedWorkletThread>*
    WorkletThreadHolder<DerivedWorkletThread>::thread_holder_instance_
        GUARDED_BY(
            WorkletThreadHolder<DerivedWorkletThread>::HolderInstanceLock()) =
            nullptr;

}  // namespace blink


struct Audio{};struct Paint{};
int main(){using A=blink::WorkletThreadHolder<Audio>;using P=blink::WorkletThreadHolder<Paint>;int checks=0;
auto check=[&](bool v){if(!v){std::fprintf(stderr,"FAIL %d\n",checks+1);return false;}++checks;return true;};
blink::ThreadCreationParams params;A::EnsureInstance(params);DrainTasks();auto*a=A::GetInstance();assert(check(a && blink::initialized==1));
A::EnsureInstance(params);DrainTasks();assert(check(A::GetInstance()==a && blink::initialized==1));
base::aros::owner=2;assert(check(A::GetInstance()==nullptr));A::EnsureInstance(params);DrainTasks();auto*b=A::GetInstance();assert(check(b && b!=a && blink::initialized==2));
P::EnsureInstance(params);DrainTasks();assert(check(P::GetInstance() && blink::initialized==3));
base::aros::owner=1;assert(check(A::GetInstance()==a && P::GetInstance()==nullptr));A::ClearInstance();assert(check(!A::GetInstance() && blink::stopped==1 && blink::destroyed==1));
base::aros::owner=2;assert(check(A::GetInstance()==b && b->GetThread()->owner==2));A::ClearInstance();P::ClearInstance();assert(check(blink::stopped==3 && blink::destroyed==3));
base::aros::owner=3;assert(check(!A::GetInstance() && !P::GetInstance()));
std::printf("PASS %d worklet holder ownership checks\n",checks);}
