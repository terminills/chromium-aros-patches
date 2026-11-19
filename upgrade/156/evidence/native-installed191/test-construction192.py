from pathlib import Path
import shutil,subprocess,json,difflib,hashlib
E=Path(__file__).parent;D=E/'construction192-draft';D.mkdir(exist_ok=True);S=Path('/mnt/short-term/job0254-01a1e62b/src');rel=Path('third_party/blink/renderer/core/html/custom/custom_element_construction_stack')
manifest={'files':{}};patch=[]
for ext in ['.cc','.h']:
 p=S/(str(rel)+ext);before=p.read_text();token='wtf_size_t CustomElementConstructionStackScope::nesting_level_ = 0;' if ext=='.cc' else '  static wtf_size_t nesting_level_;'
 change='thread_local '+token if ext=='.cc' else token.replace('static ','static thread_local ')
 after=before.replace(token,'#if defined(__AROS__)\n'+change+'\n#else\n'+token+'\n#endif');assert before!=after
 for label,content in [('before',before),('candidate',after)]:
  dest=D/label/(str(rel)+ext);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(content)
 manifest['files'][str(rel)+ext]={'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()};patch+=difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+str(rel)+ext,tofile='b/'+str(rel)+ext)
(D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(D/'candidate.patch').write_text(''.join(patch))
M=D/'mocks';M.mkdir(exist_ok=True)
(M/'mock.h').write_text('''#pragma once
#include <vector>
#include <cstddef>
#define CORE_EXPORT
#define STACK_ALLOCATED()
#define DISALLOW_NEW()
#define WTF_ALLOW_CLEAR_UNUSED_SLOTS_WITH_MEM_FUNCTIONS(x)
#define DCHECK_IS_ON() 0
namespace v8{class Object{};template<class T>class Local{};}
namespace blink {using wtf_size_t=std::size_t;class Element{};class CustomElementDefinition{};template<class T>struct Member{T* p=nullptr;Member()=default;Member(T& x):p(&x){}};struct Visitor{template<class T>void Trace(const T&){} };template<class T,int N>using GCedHeapVector=std::vector<T>;}
''')
for name in ['third_party/blink/renderer/bindings/core/v8/v8_custom_element_constructor_hash.h','third_party/blink/renderer/core/dom/element.h','third_party/blink/renderer/core/html/custom/custom_element_definition.h','third_party/blink/renderer/platform/heap/collection_support/heap_vector.h']:
 p=M/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('#include "mock.h"\n')
results={}
for variant in ['before','candidate']:
 root=D/variant;s=(root/(str(rel)+'.cc')).read_text();start=s.index('wtf_size_t CustomElementConstructionStackScope::nesting_level_ = 0;') if variant=='before' else s.index('#if defined(__AROS__)');methods=s[start:s.rindex('}  // namespace blink')]
 code='#include "'+str(rel)+'.h"\n#include <mutex>\n#include <condition_variable>\n#include <thread>\n#include <cassert>\n#include <cstdio>\nnamespace blink {\nstruct Holder{bool alive=false;void Clear(){alive=false;}};thread_local Holder holder;Holder& GetWindowMapHolder(){return holder;}CustomElementConstructionStack& EnsureConstructionStack(CustomElementDefinition&){thread_local CustomElementConstructionStack stack;holder.alive=true;return stack;}\n'+methods+'\n}\n'
 code+='''std::mutex m;std::condition_variable cv;int phase=0;bool a_clear=false,b_clear=false;
void set(int x){std::lock_guard<std::mutex> l(m);phase=x;cv.notify_all();}void wait(int x){std::unique_lock<std::mutex> l(m);cv.wait(l,[&]{return phase>=x;});}
int main(){using namespace blink;CustomElementDefinition d;Element e;{CustomElementConstructionStackScope outer(d,e);{CustomElementConstructionStackScope inner(d,e);}assert(holder.alive);}assert(!holder.alive);std::thread a([&]{{CustomElementConstructionStackScope outer(d,e);set(1);wait(2);}a_clear=!holder.alive;set(3);});std::thread b([&]{wait(1);{CustomElementConstructionStackScope outer(d,e);set(2);wait(3);}b_clear=!holder.alive;});a.join();b.join();printf("first_renderer_root_cleared=%d second_renderer_root_cleared=%d nested_scope=PASS\\n",a_clear,b_clear);return a_clear&&b_clear?0:42;}
'''
 p=D/(variant+'-test.cc');p.write_text(code);args=['c++','-std=c++20','-D__AROS__','-fsanitize=address,undefined','-pthread','-g','-I'+str(root),'-I'+str(M),str(p),'-o',str(D/(variant+'-test'))];r=subprocess.run(args,capture_output=True,text=True);(D/(variant+'-build.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
 r=subprocess.run([str(D/(variant+'-test'))],capture_output=True,text=True);(D/(variant+'-run.log')).write_text(r.stdout+r.stderr);results[variant]={'exit_code':r.returncode,'output':r.stdout+r.stderr};assert r.returncode==(42 if variant=='before' else 0),results
(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Verbatim production constructor/destructor and static counter with actual header; mocked DOM/GC container dependencies and per-owner holder. Controlled host interleaving, not native runtime qualification. Candidate not applied while191/ARM71 are building.'},indent=2)+'\n');print(results)
