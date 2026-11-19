#include <cassert>
#include <new>
#include <cstdio>
#include <thread>
#include <unordered_set>
#include "third_party/blink/renderer/platform/wtf/std_lib_extras.h"
namespace base::aros { thread_local uint64_t owner=1; uint64_t CurrentProcessIdentity(){return owner;} }
namespace blink {
template<class T> using HashSet=std::unordered_set<T>;
class WorkerThread { public:
static base::Lock& ThreadSetLock();
static unsigned WorkerThreadCount();
static HashSet<WorkerThread*>& InitializingWorkerThreads();
static HashSet<WorkerThread*>& WorkerThreads();
};
base::Lock& WorkerThread::ThreadSetLock() {
  DEFINE_THREAD_SAFE_STATIC_LOCAL(base::Lock, lock, ());
  return lock;
}
unsigned WorkerThread::WorkerThreadCount() {
  base::AutoLock locker(ThreadSetLock());
  return InitializingWorkerThreads().size() + WorkerThreads().size();
}
HashSet<WorkerThread*>& WorkerThread::InitializingWorkerThreads() {
#if BUILDFLAG(IS_AROS)
  // A resident engine contains multiple logical renderer processes.
  // Count and enumerate only this renderer's workers; worker tasks inherit
  // the same monotonic owner identity as their creating renderer.
  struct InitializingWorkersOwnerTag;
  return base::aros::ProcessLocalValue<HashSet<WorkerThread*>, InitializingWorkersOwnerTag>();
#else
  DEFINE_THREAD_SAFE_STATIC_LOCAL(HashSet<WorkerThread*>, threads, ());
  return threads;
#endif
}
HashSet<WorkerThread*>& WorkerThread::WorkerThreads() {
#if BUILDFLAG(IS_AROS)
  // A resident engine contains multiple logical renderer processes.
  // Count and enumerate only this renderer's workers; worker tasks inherit
  // the same monotonic owner identity as their creating renderer.
  struct ActiveWorkersOwnerTag;
  return base::aros::ProcessLocalValue<HashSet<WorkerThread*>, ActiveWorkersOwnerTag>();
#else
  DEFINE_THREAD_SAFE_STATIC_LOCAL(HashSet<WorkerThread*>, threads, ());
  return threads;
#endif
}
}
int main(){using W=blink::WorkerThread;W a,b;int checks=0;
auto check=[&](bool v){if(!v){std::fprintf(stderr,"FAIL %d\n",checks+1);return false;}++checks;return true;};
W::InitializingWorkerThreads().insert(&a);assert(check(W::WorkerThreadCount()==1));
base::aros::owner=2;assert(check(W::WorkerThreadCount()==0));
W::WorkerThreads().insert(&b);assert(check(W::WorkerThreadCount()==1));
base::aros::owner=1;assert(check(W::WorkerThreadCount()==1 && W::WorkerThreads().empty()));
std::thread worker([&]{base::aros::owner=1;base::AutoLock lock(W::ThreadSetLock());W::InitializingWorkerThreads().erase(&a);W::WorkerThreads().insert(&a);});worker.join();
assert(check(W::InitializingWorkerThreads().empty() && W::WorkerThreads().count(&a)==1));
W::WorkerThreads().erase(&a);assert(check(W::WorkerThreadCount()==0));
base::aros::owner=2;assert(check(W::WorkerThreadCount()==1 && W::WorkerThreads().count(&b)==1));
base::aros::owner=3;assert(check(W::WorkerThreadCount()==0));
std::printf("PASS %d registry ownership checks\n",checks);
}
