
#include <cassert>
#include <map>
#include <mutex>
#include <memory>
#include <vector>
#include <thread>
#include <barrier>
#include <cstdio>
#define CHECK(x) assert(x)
namespace base {
struct CommandLine { static thread_local CommandLine* current;
 static bool InitializedForCurrentProcess(){return current!=nullptr;}
 static CommandLine* ForCurrentProcess(){assert(current);return current;}
 static void Reset();
};
thread_local CommandLine* CommandLine::current=nullptr;
thread_local std::vector<int> order;
void CommandLine::Reset(){assert(current);order.push_back(7);current=nullptr;}
using Lock=std::mutex; using AutoLock=std::lock_guard<Lock>;
template<class T> struct NoDestructor {T value;T* operator->(){return &value;}};
struct FeatureList {CommandLine* owner=CommandLine::current;~FeatureList();};
struct FieldTrialList {CommandLine* owner=CommandLine::current;static FieldTrialList* GetInstance();~FieldTrialList();};
struct FeatureListProcessRegistry {
  Lock lock;
  std::map<const CommandLine*, FeatureList*> instances;
};

FeatureList*& GetFeatureListForCurrentProcess() {
  const CommandLine* const process_identity =
      CommandLine::InitializedForCurrentProcess()
          ? CommandLine::ForCurrentProcess()
          : nullptr;
  thread_local const CommandLine* cached_identity = nullptr;
  thread_local FeatureList** cached_instance = nullptr;
  if (cached_instance && cached_identity == process_identity) {
    return *cached_instance;
  }

  static NoDestructor<FeatureListProcessRegistry> registry;
  AutoLock lock(registry->lock);
  cached_identity = process_identity;
  cached_instance = &registry->instances[process_identity];
  return *cached_instance;
}

struct FieldTrialListProcessRegistry {
  Lock lock;
  std::map<const CommandLine*, FieldTrialList*> lists;
};

FieldTrialList*& GetFieldTrialListForCurrentProcess() {
  const CommandLine* const process_identity =
      CommandLine::InitializedForCurrentProcess()
          ? CommandLine::ForCurrentProcess()
          : nullptr;
  thread_local const CommandLine* cached_identity = nullptr;
  thread_local FieldTrialList** cached_list = nullptr;
  if (cached_list && cached_identity == process_identity) {
    return *cached_list;
  }

  static NoDestructor<FieldTrialListProcessRegistry> registry;
  AutoLock lock(registry->lock);
  cached_identity = process_identity;
  cached_list = &registry->lists[process_identity];
  return *cached_list;
}


#define g_feature_list_instance GetFeatureListForCurrentProcess()
FeatureList::~FeatureList(){assert(owner==CommandLine::current);assert(!g_feature_list_instance);order.push_back(5);}
FieldTrialList* FieldTrialList::GetInstance(){return GetFieldTrialListForCurrentProcess();}
FieldTrialList::~FieldTrialList(){assert(owner==CommandLine::current);assert(!g_feature_list_instance);assert(GetInstance()==this);GetFieldTrialListForCurrentProcess()=nullptr;order.push_back(6);}
extern "C" void aros_base_retire_child_features() {
  // Workers and child TLS consumers have finished. Detach only this logical
  // owner's feature list; testing reset helpers also alter resident state.
  FeatureList* retired = g_feature_list_instance;
  g_feature_list_instance = nullptr;
  delete retired;
}
extern "C" void aros_base_retire_child_field_trials() {
  // FeatureList contains references into this list and must be retired first.
  // Its destructor clears this owner's registry slot and shared-memory handle.
  delete FieldTrialList::GetInstance();
}
}
using base::aros_base_retire_child_features;using base::aros_base_retire_child_field_trials;
void aros_base_drain_child_tls(){assert(base::CommandLine::current);base::order.push_back(2);}
void aros_blink_retire_child_histograms(){assert(base::CommandLine::current);base::order.push_back(3);}
void aros_base_retire_child_histograms(){assert(base::CommandLine::current);base::order.push_back(4);}
void run_guard(){
  struct NativeCommandLineLifetime {
    ~NativeCommandLineLifetime() {
      // ContentMain, its workers and the delegate have unwound. Keep the
      // logical owner identity alive until owner-scoped metrics and feature trials are gone.
      aros_base_drain_child_tls();
      aros_blink_retire_child_histograms();
      aros_base_retire_child_histograms();
      aros_base_retire_child_features();
      aros_base_retire_child_field_trials();
      base::CommandLine::Reset();
      CHECK(!base::CommandLine::InitializedForCurrentProcess());
    }
  } command_line_lifetime;

struct Delegate{~Delegate(){assert(base::CommandLine::current);base::order.push_back(1);}} delegate;
}
int main(){
 base::CommandLine a,b;
 std::barrier sync(2);
 auto lane=[&](base::CommandLine* owner){
  for(int i=0;i<100;i++){
   base::CommandLine::current=owner;base::order.clear();
   assert(!base::GetFeatureListForCurrentProcess());assert(!base::FieldTrialList::GetInstance());
   auto* features=new base::FeatureList;auto* trials=new base::FieldTrialList;
   base::GetFeatureListForCurrentProcess()=features;base::GetFieldTrialListForCurrentProcess()=trials;
   sync.arrive_and_wait();
   assert(base::GetFeatureListForCurrentProcess()==features);assert(base::FieldTrialList::GetInstance()==trials);
   run_guard();
   assert(!base::CommandLine::InitializedForCurrentProcess());
   assert(base::order==std::vector<int>({1,2,3,4,5,6,7}));
   sync.arrive_and_wait();
  }
 };
 std::thread x(lane,&a),y(lane,&b);x.join();y.join();
 puts("PASS: actual registry, retirement functions and CEF guard preserve two concurrent owners over100 reuse cycles; feature-before-trial-before-owner cleanup. Dependencies mocked; native behavior remains unverified.");
}
