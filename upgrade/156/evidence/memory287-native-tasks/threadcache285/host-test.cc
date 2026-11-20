
#include <cassert>
#include <cstdint>
#include <mutex>
#include <vector>
#include <thread>
#include <new>
#include <cstdio>
#define FLAG_IS_WIN 0
#define FLAG_THREAD_CACHE_FAST_TLS 1
#define PA_BUILDFLAG(x) FLAG_##x
#define PA_CONFIG(x) FLAG_##x
#define PA_UNSAFE_TODO(x) x
thread_local std::vector<int> events;
namespace partition_alloc::internal {
constexpr size_t kMaxThreadCacheIndex=2,kThreadCacheTombstoneIndex=0;
struct ThreadCache;
thread_local ThreadCache* g_thread_caches[2]={};
thread_local void* value=nullptr;
int g_thread_cache_key=1;bool g_thread_cache_key_created=true;
struct ThreadCacheRegistry {static std::mutex& GetLock(){static std::mutex m;return m;}};
using ScopedGuard=std::lock_guard<std::mutex>;
void* PartitionTlsGet(int){return value;}
void PartitionTlsSet(int,void* v){value=v;}
struct ThreadCache {
 void* root_=this;
 static constexpr uintptr_t kTombstone=1;
 static bool IsValidPtr(void* p){return (reinterpret_cast<uintptr_t>(p)&~uintptr_t(1))!=0;}
 ~ThreadCache(){events.push_back(2);}
 static void operator delete(void* p){events.push_back(3);::operator delete(p);}
 static void Delete(void*);static void DeleteForCurrentNativeTask();
};
void ThreadCache::Delete(void* thread_caches_ptr) {
  auto* tcaches = static_cast<ThreadCache*>(thread_caches_ptr);
  if (!IsValidPtr(tcaches)) {
    return;
  }
  internal::PartitionTlsSet(internal::g_thread_cache_key, nullptr);

  for (size_t i = 0; i < internal::kMaxThreadCacheIndex; i++) {
#if PA_CONFIG(THREAD_CACHE_FAST_TLS)
    PA_UNSAFE_TODO(internal::g_thread_caches[i]) = nullptr;
#endif
    ThreadCache* tcache = PA_UNSAFE_TODO(tcaches + i);
    if (tcache->root_) {
      tcache->~ThreadCache();
    }
  }
  // Operator new is overloaded to route to internal partition.
  operator delete(tcaches);

#if PA_BUILDFLAG(IS_WIN)
  // On Windows, allocations do occur during thread/process teardown, make sure
  // they don't resurrect the thread cache.
  //
  // Don't MTE-tag, as it'd mess with the sentinel value.
  //
  // TODO(lizeb): Investigate whether this is needed on POSIX as well.
  internal::PartitionTlsSet(internal::g_thread_cache_key,
                            reinterpret_cast<void*>(kTombstone));
#if PA_CONFIG(THREAD_CACHE_FAST_TLS)
  // This is sufficient to prevent re-creation, because IsTombstone() is called
  // before Create() and IsTombstone() only checks this index.
  PA_UNSAFE_TODO(
      internal::g_thread_caches[internal::kThreadCacheTombstoneIndex]) =
      reinterpret_cast<ThreadCache*>(kTombstone);
#endif

#endif  // PA_BUILDFLAG(IS_WIN)
}
void ThreadCache::DeleteForCurrentNativeTask() {
  {
    internal::ScopedGuard lock(ThreadCacheRegistry::GetLock());
    if (!g_thread_cache_key_created)
      return;
  }
  // This callback runs on the exiting task after its Chromium TLS consumers.
  // Keep deletion outside the registry lock: the destructor unregisters here.
  Delete(internal::PartitionTlsGet(internal::g_thread_cache_key));
  // Late CRT/owner cleanup can still allocate. Prevent cache resurrection;
  // those operations must use the shared root directly instead.
  internal::PartitionTlsSet(internal::g_thread_cache_key,
                            reinterpret_cast<void*>(kTombstone));
#if PA_CONFIG(THREAD_CACHE_FAST_TLS)
  PA_UNSAFE_TODO(internal::g_thread_caches[internal::kThreadCacheTombstoneIndex]) =
      reinterpret_cast<ThreadCache*>(kTombstone);
#endif
}
}
namespace partition_alloc {struct ThreadCache{static void OnNativeTaskExit(){internal::ThreadCache::DeleteForCurrentNativeTask();}};}
namespace base::internal {
struct PlatformThreadLocalStorage {using TLSKey=int;static constexpr int TLS_KEY_OUT_OF_INDEXES=-1;};
struct Key {int load(int){return 1;}} g_native_tls_key;
struct TlsVectorEntry{};
enum class TlsVectorState{kUninitialized,kInUse,kDestroying,kDestroyed};
thread_local TlsVectorState state=TlsVectorState::kInUse;
TlsVectorState GetTlsVectorStateAndValue(int,TlsVectorEntry**){return state;}
void OnNativeTaskExit();
void OnThreadExitInternal(TlsVectorEntry*){state=TlsVectorState::kDestroying;OnNativeTaskExit();assert(partition_alloc::internal::value!=reinterpret_cast<void*>(1));events.push_back(1);state=TlsVectorState::kDestroyed;}
void OnNativeTaskExit() {
  const PlatformThreadLocalStorage::TLSKey key =
      g_native_tls_key.load(0);
  if (key != PlatformThreadLocalStorage::TLS_KEY_OUT_OF_INDEXES) {
    TlsVectorEntry* vector = nullptr;
    const TlsVectorState state = GetTlsVectorStateAndValue(key, &vector);
    // Reentrant destruction must leave the allocator available to the outer
    // destructor pass. Repeated completed notifications are harmless.
    if (state == TlsVectorState::kDestroying)
      return;
    if (state == TlsVectorState::kInUse)
      OnThreadExitInternal(vector);
  }
  partition_alloc::ThreadCache::OnNativeTaskExit();
}
}
void task(bool with_base_tls){
 using namespace partition_alloc::internal;
 events.clear();value=::operator new(sizeof(ThreadCache)*2);
 auto* caches=static_cast<ThreadCache*>(value);for(size_t i=0;i<2;i++){new(caches+i)ThreadCache;g_thread_caches[i]=caches+i;}
 base::internal::state=with_base_tls?base::internal::TlsVectorState::kInUse:base::internal::TlsVectorState::kUninitialized;
 base::internal::OnNativeTaskExit();
 auto expected=with_base_tls?std::vector<int>{1,2,2,3}:std::vector<int>{2,2,3};assert(events==expected);
 assert(value==reinterpret_cast<void*>(1));assert(g_thread_caches[0]==reinterpret_cast<ThreadCache*>(1));assert(!g_thread_caches[1]);
 base::internal::OnNativeTaskExit();assert(events==expected);
}
int main(){
 std::thread a([]{for(int i=0;i<100;i++)task(true);}),b([]{for(int i=0;i<100;i++)task(false);});a.join();b.join();
 partition_alloc::internal::g_thread_cache_key_created=false;events.clear();base::internal::state=base::internal::TlsVectorState::kUninitialized;base::internal::OnNativeTaskExit();assert(events.empty());
 puts("PASS: actual native hook/cache deletion bodies, two task slots,200 exits, destructor reentry, missing base TLS, repeated exit, and no allocator initialization. Host dependencies mocked; native memory effects unverified.");
}
