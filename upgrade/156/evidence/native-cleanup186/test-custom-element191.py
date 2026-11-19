from pathlib import Path
import subprocess,json,hashlib,shutil
E=Path(__file__).parent; D=E/'custom-element191';D.mkdir(exist_ok=True)
S=Path('/mnt/short-term/job0254-01a1e62b/src');rel=Path('third_party/blink/renderer/core/html/custom/ce_reactions_scope')
for suffix in ['.cc','.h']:
 p=S/(str(rel)+suffix);dst=D/'before'/(str(rel)+suffix);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
mock='''#pragma once
#include <cassert>
#define CORE_EXPORT
#define STACK_ALLOCATED()
#define DCHECK(x) assert(x)
namespace v8 { class Isolate {}; class TryCatch { public: explicit TryCatch(Isolate*) {} bool HasCaught(){return false;} void ReThrow(){} }; }
namespace blink { inline bool IsMainThread(){return true;} class Element{};class CustomElementReaction{};class CustomElementReactionStack {public:int depth=0;void Push(){++depth;}void PopInvokingReactions(){--depth;}void EnqueueToCurrentQueue(Element&,CustomElementReaction&){} }; }
'''
M=D/'mocks';M.mkdir(exist_ok=True);(M/'mock.h').write_text(mock)
includes=['third_party/blink/renderer/core/core_export.h','third_party/blink/renderer/platform/wtf/allocator/allocator.h','third_party/blink/renderer/platform/wtf/std_lib_extras.h','v8/include/v8.h','third_party/blink/renderer/bindings/core/v8/script_promise_resolver.h','third_party/blink/renderer/core/dom/document.h','third_party/blink/renderer/core/dom/element.h','third_party/blink/renderer/core/execution_context/execution_context.h','third_party/blink/renderer/core/html/custom/custom_element_reaction_stack.h']
for name in includes:
 p=M/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('#include "mock.h"\n')
(D/'test.cc').write_text('''#include "third_party/blink/renderer/core/html/custom/ce_reactions_scope.h"
#include <mutex>
#include <condition_variable>
#include <thread>
#include <cstdio>
std::mutex m;std::condition_variable cv;int phase=0;bool isolated=false;
void set(int p){std::lock_guard<std::mutex> l(m);phase=p;cv.notify_all();}
void wait(int p){std::unique_lock<std::mutex> l(m);cv.wait(l,[&]{return phase>=p;});}
int main(){v8::Isolate iso;std::thread a([&]{blink::CEReactionsScope scope(&iso);set(1);wait(2);isolated=blink::CEReactionsScope::Current()==&scope;set(3);wait(4);});std::thread b([&]{wait(1);{blink::CEReactionsScope scope(&iso);assert(blink::CEReactionsScope::Current()==&scope);set(2);wait(3);}set(4);});a.join();b.join();assert(blink::CEReactionsScope::Current()==nullptr);{blink::CEReactionsScope outer(&iso);{blink::CEReactionsScope inner(&iso);assert(blink::CEReactionsScope::Current()==&inner);}assert(blink::CEReactionsScope::Current()==&outer);}assert(blink::CEReactionsScope::Current()==nullptr);std::printf("concurrent_scope_isolation=%s nested_restore=PASS\\n",isolated?"PASS":"FAIL");return isolated?0:42;}
''')
results={}
for variant in ['before','candidate']:
 root=D/variant
 if variant=='candidate':
  for suffix in ['.cc','.h']:
   src=D/'before'/(str(rel)+suffix);dst=root/(str(rel)+suffix);dst.parent.mkdir(parents=True,exist_ok=True);s=src.read_text()
   token='CEReactionsScope* CEReactionsScope::top_of_stack_ = nullptr;' if suffix=='.cc' else '  static CEReactionsScope* top_of_stack_;'
   replacement=('#if defined(__AROS__)\n// Renderer main threads share this library, but never their reaction scopes.\nthread_local CEReactionsScope* CEReactionsScope::top_of_stack_ = nullptr;\n#else\n'+token+'\n#endif') if suffix=='.cc' else ('#if defined(__AROS__)\n  static thread_local CEReactionsScope* top_of_stack_;\n#else\n'+token+'\n#endif')
   assert s.count(token)==1;dst.write_text(s.replace(token,replacement))
 cmd=['c++','-std=c++20','-pthread','-D__AROS__','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g','-I'+str(root),'-I'+str(M),str(root/(str(rel)+'.cc')),str(D/'test.cc'),'-o',str(D/(variant+'-test'))]
 p=subprocess.run(cmd,capture_output=True,text=True);(D/(variant+'-build.log')).write_text(p.stdout+p.stderr);assert p.returncode==0
 p=subprocess.run([str(D/(variant+'-test'))],capture_output=True,text=True);(D/(variant+'-run.log')).write_text(p.stdout+p.stderr);results[variant]={'exit_code':p.returncode,'output':p.stdout+p.stderr}
 assert p.returncode==(42 if variant=='before' else 0),results
(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Actual CEReactionsScope sources with mocked V8 and DOM dependencies; controlled host thread interleaving, not native runtime proof.'},indent=2)+'\n');print(results)
