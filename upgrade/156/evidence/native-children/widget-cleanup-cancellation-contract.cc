#include <memory>
#include <tuple>
#include <cstdio>
struct State { bool manager_alive=true; bool view_saw_live_manager=false; bool scheduler_stopped=false; };
struct Scheduler { State& state; void Shutdown(){state.scheduler_stopped=true;} };
struct Manager { State& state; ~Manager(){state.manager_alive=false;} };
struct View { State& state; ~View(){state.view_saw_live_manager=state.manager_alive;} };
struct Ordered {
 std::unique_ptr<Scheduler> scheduler;
 std::unique_ptr<Manager> manager;
 std::unique_ptr<View> view;
 ~Ordered(){view.reset();manager.reset();}
};
int main(){
 State old;
 { auto bound=std::tuple(std::make_unique<Scheduler>(old),std::make_unique<Manager>(old),std::make_unique<View>(old)); }
 State cancelled;
 { auto bound=std::make_unique<Ordered>(std::make_unique<Scheduler>(cancelled),std::make_unique<Manager>(cancelled),std::make_unique<View>(cancelled)); }
 State invoked;
 { auto bound=std::make_unique<Ordered>(std::make_unique<Scheduler>(invoked),std::make_unique<Manager>(invoked),std::make_unique<View>(invoked));bound->view.reset();bound->manager.reset();bound->scheduler->Shutdown(); }
 bool pass=!old.view_saw_live_manager && cancelled.view_saw_live_manager && !cancelled.scheduler_stopped && invoked.view_saw_live_manager && invoked.scheduler_stopped;
 std::printf("old_cancel_view_has_manager=%d ordered_cancel=%d ordered_invoke=%d scheduler_cancel=%d scheduler_invoke=%d %s\n",old.view_saw_live_manager,cancelled.view_saw_live_manager,invoked.view_saw_live_manager,cancelled.scheduler_stopped,invoked.scheduler_stopped,pass?"PASS":"FAIL");
 return pass?0:1;
}
