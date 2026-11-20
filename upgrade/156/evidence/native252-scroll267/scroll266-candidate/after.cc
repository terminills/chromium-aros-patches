
#include <atomic>
#include <thread>
#include <cassert>
#include <cstdio>
#define BUILDFLAG(x) 1
#define CORE_EXPORT
#define STACK_ALLOCATED()
#define CHECK(x) assert(x)
#define CHECK_EQ(a,b) assert((a)==(b))
namespace blink {
class Frame {public: bool outer=true; bool IsOutermostMainFrame(){return outer;} bool IsDetached(){return false;}};
class LocalFrameMetricsAggregator {public: enum {kPossibleSynchronizedScrollCount2}; int count=0; void RecordCountSample(int,int n){count+=n;}};
class LocalFrameView {public: LocalFrameMetricsAggregator metrics; LocalFrameMetricsAggregator* GetMetricsAggregator(){return &metrics;}};
class LocalFrame:public Frame {public:LocalFrameView view;LocalFrameView* View(){return &view;}};
template<class T>T* DynamicTo(Frame*p){return static_cast<T*>(p);}
}
// Copyright 2023 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef THIRD_PARTY_BLINK_RENDERER_CORE_PAGE_SCROLLING_SYNC_SCROLL_ATTEMPT_HEURISTIC_H_
#define THIRD_PARTY_BLINK_RENDERER_CORE_PAGE_SCROLLING_SYNC_SCROLL_ATTEMPT_HEURISTIC_H_


namespace blink {

class Frame;

// SyncScrollAttemptHeuristic handles detecting cases where a page attempts to
// synchronize an effect with scrolling (eg, using JavaScript to implement a
// parallax scroller). While a vended Scope instance exists, the heuristic
// observes when script accesses scroll position and then also modifies inline
// style or scroll offset in order to estimate when script is attempting to
// synchronize content with scrolling (these style/scroll-offset updates may
// not actually be implementing a sync-scroll effect, so this can be
// inaccurate).
//
// This is complicated somewhat by rAF. It can happen that a scroll handler
// will use rAF to realize the update. Our heuristic is imprecise in this case.
// We consider it to be a sync scroll attempt if
//   a) a rAF callback was scheduled via a scroll handler and,
//   b) any rAF callback then mutates inline style or scroll position.
// I.e., we do not distinguish the rAF callback scheduled during the scroll
// handler from any other rAF callback, which can lead to incorrectly flagging a
// rAF-induced mutation as a sync scroll attempt.
//
// More precisely,
//   - A Scope |A| is created before step 6.9 of the html processing model[1]
//     and it is destroyed before step 6.10. This scope is always active.
//   - We then create a Scope |B| before step 6.14 that is destroyed before step
//     6.15 [1]. This scope is only active (i.e., listening for updates), if
//     a rAF callback was scheduled during Scope |A|'s lifetime.
// If, while Scopes |A| and |B| are active, scroll offset was accessed and
// either inline style or scroll position was modified, the heuristic considers
// this to have been an attempt at creating a scroll-synchronized effect.
//
// We only attempt to detect sync scroll attempts if the given frame is the
// outermost main frame and UKM is not recorded when the given frame is remote.
//
// [1] https://html.spec.whatwg.org/#event-loop-processing-model
//
// TODO(crbug.com/1499981): This should be removed once synchronized scrolling
// impact is understood.
class CORE_EXPORT SyncScrollAttemptHeuristic final {
  STACK_ALLOCATED();

 public:
  explicit SyncScrollAttemptHeuristic(Frame* frame);
  SyncScrollAttemptHeuristic(const SyncScrollAttemptHeuristic&) = delete;
  SyncScrollAttemptHeuristic& operator=(const SyncScrollAttemptHeuristic&) =
      delete;
  ~SyncScrollAttemptHeuristic();

  class Scope {
    STACK_ALLOCATED();

   public:
    explicit Scope(bool enable_observation);
    ~Scope();

   private:
    bool enable_observation_ = false;
  };

  [[nodiscard]] static Scope GetScrollHandlerScope();
  [[nodiscard]] static Scope GetRequestAnimationFrameScope();
  static void DidAccessScrollOffset();
  static void DidSetScrollOffset();
  static void DidSetStyle();
  static void DidRequestAnimationFrame();

 private:
  static void EnableObservation();
  static void DisableObservation();

  Frame* frame_ = nullptr;
  SyncScrollAttemptHeuristic* last_instance_ = nullptr;
  bool did_access_scroll_offset_ = false;
  bool did_set_scroll_offset_ = false;
  bool did_set_style_ = false;
  bool did_request_animation_frame_ = false;
  bool is_observing_ = false;
};

}  // namespace blink

#endif  // THIRD_PARTY_BLINK_RENDERER_CORE_PAGE_SCROLLING_SYNC_SCROLL_ATTEMPT_HEURISTIC_H_
// Copyright 2023 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.



namespace blink {

namespace {

// Each native AROS renderer has its own main Exec task. This pointer tracks
// stack scopes on that task; sharing it across renderer tasks corrupts the
// nesting chain when another renderer starts or finishes a frame.
#if BUILDFLAG(IS_AROS)
thread_local SyncScrollAttemptHeuristic* g_sync_scroll_attempt_heuristic = nullptr;
#else
SyncScrollAttemptHeuristic* g_sync_scroll_attempt_heuristic = nullptr;
#endif

}  // namespace

SyncScrollAttemptHeuristic::SyncScrollAttemptHeuristic(Frame* frame)
    : frame_(frame), last_instance_(g_sync_scroll_attempt_heuristic) {
  if (frame_ && frame_->IsOutermostMainFrame()) {
    g_sync_scroll_attempt_heuristic = this;
  } else {
    g_sync_scroll_attempt_heuristic = nullptr;
  }
}

SyncScrollAttemptHeuristic::~SyncScrollAttemptHeuristic() {
  if (frame_ && frame_->IsOutermostMainFrame()) {
    CHECK_EQ(g_sync_scroll_attempt_heuristic, this);
  }
  g_sync_scroll_attempt_heuristic = last_instance_;
  const bool saw_possible_sync_scrolling_attempt =
      did_access_scroll_offset_ && (did_set_style_ || did_set_scroll_offset_);
  if (saw_possible_sync_scrolling_attempt && frame_ &&
      frame_->IsOutermostMainFrame() && !frame_->IsDetached()) {
    // This will not cover cases where |frame_| is remote.
    if (LocalFrame* local_frame = DynamicTo<LocalFrame>(frame_)) {
      if (local_frame->View()) {
        if (LocalFrameMetricsAggregator* metrics_aggregator =
                local_frame->View()->GetMetricsAggregator()) {
          metrics_aggregator->RecordCountSample(
              LocalFrameMetricsAggregator::kPossibleSynchronizedScrollCount2,
              1);
        }
      }
    }
  }
}

SyncScrollAttemptHeuristic::Scope::Scope(bool enable_observation)
    : enable_observation_(enable_observation) {
  if (enable_observation_) {
    SyncScrollAttemptHeuristic::EnableObservation();
  }
}

SyncScrollAttemptHeuristic::Scope::~Scope() {
  if (enable_observation_) {
    SyncScrollAttemptHeuristic::DisableObservation();
  }
}

SyncScrollAttemptHeuristic::Scope
SyncScrollAttemptHeuristic::GetScrollHandlerScope() {
  return Scope(g_sync_scroll_attempt_heuristic);
}

SyncScrollAttemptHeuristic::Scope
SyncScrollAttemptHeuristic::GetRequestAnimationFrameScope() {
  // We only want to observe rAF if one was requested during a scroll
  // handler. If that's the case, |did_request_animation_frame_| should be
  // true.
  return Scope(g_sync_scroll_attempt_heuristic &&
               g_sync_scroll_attempt_heuristic->did_request_animation_frame_);
}

void SyncScrollAttemptHeuristic::DidAccessScrollOffset() {
  if (g_sync_scroll_attempt_heuristic &&
      g_sync_scroll_attempt_heuristic->is_observing_) [[unlikely]] {
    g_sync_scroll_attempt_heuristic->did_access_scroll_offset_ = true;
  }
}

void SyncScrollAttemptHeuristic::DidSetScrollOffset() {
  // We only want to record a mutation if we've already accessed the scroll
  // offset.
  if (g_sync_scroll_attempt_heuristic &&
      g_sync_scroll_attempt_heuristic->is_observing_ &&
      g_sync_scroll_attempt_heuristic->did_access_scroll_offset_) [[unlikely]] {
    g_sync_scroll_attempt_heuristic->did_set_scroll_offset_ = true;
  }
}

void SyncScrollAttemptHeuristic::DidSetStyle() {
  // We only want to record a mutation if we've already accessed the scroll
  // offset.
  if (g_sync_scroll_attempt_heuristic &&
      g_sync_scroll_attempt_heuristic->is_observing_ &&
      g_sync_scroll_attempt_heuristic->did_access_scroll_offset_) [[unlikely]] {
    g_sync_scroll_attempt_heuristic->did_set_style_ = true;
  }
}

void SyncScrollAttemptHeuristic::DidRequestAnimationFrame() {
  if (g_sync_scroll_attempt_heuristic &&
      g_sync_scroll_attempt_heuristic->is_observing_) [[unlikely]] {
    g_sync_scroll_attempt_heuristic->did_request_animation_frame_ = true;
  }
}

void SyncScrollAttemptHeuristic::EnableObservation() {
  if (g_sync_scroll_attempt_heuristic) [[unlikely]] {
    CHECK(!g_sync_scroll_attempt_heuristic->is_observing_);
    g_sync_scroll_attempt_heuristic->is_observing_ = true;
  }
}

void SyncScrollAttemptHeuristic::DisableObservation() {
  if (g_sync_scroll_attempt_heuristic) [[unlikely]] {
    CHECK(g_sync_scroll_attempt_heuristic->is_observing_);
    g_sync_scroll_attempt_heuristic->is_observing_ = false;
  }
}

}  // namespace blink

int main(){using namespace blink; std::atomic<int> step{0};LocalFrame a,b;
std::thread worker([&]{while(step.load()!=1)std::this_thread::yield();{
 SyncScrollAttemptHeuristic outer(&b);step.store(2);while(step.load()!=3)std::this_thread::yield();
 {auto scope=SyncScrollAttemptHeuristic::GetScrollHandlerScope();SyncScrollAttemptHeuristic::DidAccessScrollOffset();SyncScrollAttemptHeuristic::DidSetScrollOffset();}
}step.store(4);});
{
 SyncScrollAttemptHeuristic outer(&a);
 {Frame inner;inner.outer=false;SyncScrollAttemptHeuristic nested(&inner);auto scope=SyncScrollAttemptHeuristic::GetScrollHandlerScope();}
 {auto scope=SyncScrollAttemptHeuristic::GetScrollHandlerScope();SyncScrollAttemptHeuristic::DidAccessScrollOffset();SyncScrollAttemptHeuristic::DidSetStyle();SyncScrollAttemptHeuristic::DidRequestAnimationFrame();}
 {auto scope=SyncScrollAttemptHeuristic::GetRequestAnimationFrameScope();SyncScrollAttemptHeuristic::DidAccessScrollOffset();}
 step.store(1);while(step.load()!=2)std::this_thread::yield();
}
step.store(3);worker.join();assert(step==4);assert(a.view.metrics.count==1&&b.view.metrics.count==1);puts("PASS independent renderer-task scope nesting and observation, including nested disabled scope and rAF");}
