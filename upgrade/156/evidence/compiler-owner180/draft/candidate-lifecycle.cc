
#include <cstdlib>
#include <cstdio>
#include <vector>
#define V8_OS_AROS 1
#define DCHECK_EQ(a,b) do { if((a)!=(b)) std::abort(); } while(0)
struct Pool { bool alive=true; int creates=0; int cancels=0; };
Pool* current;
struct Isolate {};
struct OptimizingCompileTaskExecutor {
 Pool* owner=nullptr;
 void EnsureStarted(){if(!owner){owner=current;++owner->creates;}}
 void Stop(){if(owner){if(!owner->alive){std::puts("STALE_POOL_CANCELLATION");std::exit(23);}++owner->cancels;owner=nullptr;}}
};
struct OptimizingCompileDispatcher {
 Isolate* isolate_;
 OptimizingCompileTaskExecutor* task_executor_;
 std::vector<int> output_queue_;
 OptimizingCompileDispatcher(Isolate*,OptimizingCompileTaskExecutor*);
 ~OptimizingCompileDispatcher();
};
OptimizingCompileDispatcher::OptimizingCompileDispatcher(
    Isolate* isolate, OptimizingCompileTaskExecutor* task_executor)
    : isolate_(isolate), task_executor_(task_executor) {
#if V8_OS_AROS
  // A resident V8 image serves independent native process owners. The group's
  // first isolate may retire its worker pool while other isolates remain.
  // Keep compiler jobs within the isolate's owning pool and lifetime; shared
  // executable code and read-only group data remain in the resident engine.
  task_executor_ = new OptimizingCompileTaskExecutor;
  task_executor_->EnsureStarted();
#endif
}
OptimizingCompileDispatcher::~OptimizingCompileDispatcher() {
  DCHECK_EQ(output_queue_.size(), 0);
#if V8_OS_AROS
  task_executor_->Stop();
  delete task_executor_;
#endif
}
void StartGroup(OptimizingCompileTaskExecutor* optimizing_compile_task_executor_){
#if !V8_OS_AROS
  optimizing_compile_task_executor_->EnsureStarted();
#endif
}

int main(){
 Pool a,b;Isolate ia,ib;OptimizingCompileTaskExecutor shared;
 current=&a;StartGroup(&shared);auto* da=new OptimizingCompileDispatcher(&ia,&shared);
 current=&b;StartGroup(&shared);auto* db=new OptimizingCompileDispatcher(&ib,&shared);
 current=&a;delete da;a.alive=false;
 current=&b;delete db;shared.Stop();b.alive=false;
 if(a.creates!=1||b.creates!=1||a.cancels!=1||b.cancels!=1)return 24;
 std::puts("PASS: independent job ownership and cancellation before each pool retires");
}
