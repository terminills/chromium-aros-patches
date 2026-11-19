#include <cassert>
#include <new>
#include <cstdio>
#include <unordered_set>
#include "third_party/blink/renderer/platform/wtf/std_lib_extras.h"
#define EXCLUSIVE_LOCKS_REQUIRED(...)
namespace base::aros { thread_local uint64_t owner=1; uint64_t CurrentProcessIdentity(){return owner;} }
namespace v8 { enum class MemoryPressureLevel { kCritical };
struct Isolate { enum class Priority { kUserBlocking, kUserVisible, kBestEffort };
 Priority priority=Priority::kUserBlocking;bool battery=false,memory=false;int pressures=0;
 void SetPriority(Priority p){priority=p;}void SetBatterySaverMode(bool b){battery=b;}
 void SetMemorySaverMode(bool b){memory=b;}void MemoryPressureNotification(MemoryPressureLevel){++pressures;}
};}
namespace blink {
template<class T> struct HashSet:std::unordered_set<T>{bool Contains(T v){return this->count(v)!=0;}};
class WorkerBackingThread {public:
static void MemoryPressureNotificationToWorkerThreadIsolates(v8::MemoryPressureLevel);
static void SetWorkerThreadIsolatesPriority(v8::Isolate::Priority);
static void SetBatterySaverModeForWorkerThreadIsolates(bool);
static void SetMemorySaverModeForWorkerThreadIsolates(bool);
};
base::Lock& IsolatesLock() {
  DEFINE_THREAD_SAFE_STATIC_LOCAL(base::Lock, lock, ());
  return lock;
}
HashSet<v8::Isolate*>& Isolates() EXCLUSIVE_LOCKS_REQUIRED(IsolatesLock()) {
  DEFINE_THREAD_SAFE_STATIC_LOCAL(HashSet<v8::Isolate*>, isolates, ());
  return isolates;
}
HashSet<v8::Isolate*>& ForegroundedIsolates()
    EXCLUSIVE_LOCKS_REQUIRED(IsolatesLock()) {
  DEFINE_THREAD_SAFE_STATIC_LOCAL(HashSet<v8::Isolate*>, foregrounded_isolates,
                                  ());
  return foregrounded_isolates;
}
v8::Isolate::Priority& IsolateCurrentPriority()
    EXCLUSIVE_LOCKS_REQUIRED(IsolatesLock()) {
  DEFINE_THREAD_SAFE_STATIC_LOCAL(v8::Isolate::Priority,
                                  isolate_current_priority,
                                  (v8::Isolate::Priority::kUserBlocking));
  return isolate_current_priority;
}
bool& BatterySaverModeEnabled() EXCLUSIVE_LOCKS_REQUIRED(IsolatesLock()) {
  DEFINE_THREAD_SAFE_STATIC_LOCAL(bool, battery_saver_mode_enabled, ());
  return battery_saver_mode_enabled;
}
bool& MemorySaverModeEnabled() EXCLUSIVE_LOCKS_REQUIRED(IsolatesLock()) {
  DEFINE_THREAD_SAFE_STATIC_LOCAL(bool, memory_saver_mode_enabled, ());
  return memory_saver_mode_enabled;
}
void AddWorkerIsolate(v8::Isolate* isolate) {
  base::AutoLock locker(IsolatesLock());
  isolate->SetPriority(IsolateCurrentPriority());
  if (BatterySaverModeEnabled()) {
    isolate->SetBatterySaverMode(true);
  }
  if (MemorySaverModeEnabled()) {
    isolate->SetMemorySaverMode(true);
  }
  Isolates().insert(isolate);
}
void RemoveWorkerIsolate(v8::Isolate* isolate) {
  base::AutoLock locker(IsolatesLock());
  Isolates().erase(isolate);
}
void AddForegroundedWorkerIsolate(v8::Isolate* isolate) {
  base::AutoLock locker(IsolatesLock());
  ForegroundedIsolates().insert(isolate);
}
void RemoveForegroundedWorkerIsolate(v8::Isolate* isolate) {
  base::AutoLock locker(IsolatesLock());
  ForegroundedIsolates().erase(isolate);
}
void WorkerBackingThread::MemoryPressureNotificationToWorkerThreadIsolates(
    v8::MemoryPressureLevel level) {
  base::AutoLock locker(IsolatesLock());
  for (v8::Isolate* isolate : Isolates())
    isolate->MemoryPressureNotification(level);
}
void WorkerBackingThread::SetWorkerThreadIsolatesPriority(
    v8::Isolate::Priority priority) {
  base::AutoLock locker(IsolatesLock());
  IsolateCurrentPriority() = priority;
  for (v8::Isolate* isolate : Isolates()) {
    if (!ForegroundedIsolates().Contains(isolate)) {
      isolate->SetPriority(priority);
    }
  }
}
void WorkerBackingThread::SetBatterySaverModeForWorkerThreadIsolates(
    bool battery_saver_mode_enabled) {
  base::AutoLock locker(IsolatesLock());

  for (v8::Isolate* isolate : Isolates()) {
    isolate->SetBatterySaverMode(battery_saver_mode_enabled);
  }
  BatterySaverModeEnabled() = battery_saver_mode_enabled;
}
void WorkerBackingThread::SetMemorySaverModeForWorkerThreadIsolates(
    bool memory_saver_mode_enabled) {
  base::AutoLock locker(IsolatesLock());

  for (v8::Isolate* isolate : Isolates()) {
    isolate->SetMemorySaverMode(memory_saver_mode_enabled);
  }
  MemorySaverModeEnabled() = memory_saver_mode_enabled;
}
}
int main(){using namespace blink;using W=WorkerBackingThread;using P=v8::Isolate::Priority;
v8::Isolate a,b,c;int checks=0;auto check=[&](bool v){if(!v){std::fprintf(stderr,"FAIL %d\n",checks+1);return false;}++checks;return true;};
AddWorkerIsolate(&a);W::SetWorkerThreadIsolatesPriority(P::kBestEffort);W::SetBatterySaverModeForWorkerThreadIsolates(true);W::SetMemorySaverModeForWorkerThreadIsolates(true);
assert(check(a.priority==P::kBestEffort && a.battery && a.memory));
base::aros::owner=2;AddWorkerIsolate(&b);assert(check(b.priority==P::kUserBlocking && !b.battery && !b.memory));
assert(check(Isolates().size()==1 && Isolates().Contains(&b)));
W::SetWorkerThreadIsolatesPriority(P::kUserVisible);assert(check(a.priority==P::kBestEffort && b.priority==P::kUserVisible));
AddForegroundedWorkerIsolate(&b);W::SetWorkerThreadIsolatesPriority(P::kBestEffort);assert(check(b.priority==P::kUserVisible));
base::aros::owner=1;assert(check(ForegroundedIsolates().empty()));
W::MemoryPressureNotificationToWorkerThreadIsolates(v8::MemoryPressureLevel::kCritical);assert(check(a.pressures==1 && b.pressures==0));
RemoveWorkerIsolate(&a);assert(check(Isolates().empty()));AddWorkerIsolate(&c);assert(check(c.battery && c.memory && c.priority==P::kBestEffort));
base::aros::owner=2;assert(check(Isolates().Contains(&b) && ForegroundedIsolates().Contains(&b)));
RemoveForegroundedWorkerIsolate(&b);RemoveWorkerIsolate(&b);assert(check(Isolates().empty() && ForegroundedIsolates().empty()));
base::aros::owner=3;assert(check(!BatterySaverModeEnabled() && !MemorySaverModeEnabled() && IsolateCurrentPriority()==P::kUserBlocking));
std::printf("PASS %d worker isolate ownership checks\n",checks);}
