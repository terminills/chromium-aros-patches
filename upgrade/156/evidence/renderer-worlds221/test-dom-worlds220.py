from pathlib import Path
import hashlib,json,difflib,subprocess
E=Path(__file__).parent;D=E/'dom-worlds220-draft';D.mkdir(exist_ok=True);S=Path('/mnt/short-term/job0254-01a1e62b/src');root='third_party/blink/renderer/platform/bindings/dom_wrapper_world';m={'files':{}};patch='';types=['IsolatedWorldSecurityOriginMap','IsolatedWorldStableIdMap','IsolatedWorldHumanReadableNameMap','IsolatedWorldEmbedderWorldIdMap'];getters=['IsolatedWorldSecurityOrigins','IsolatedWorldStableIds','IsolatedWorldHumanReadableNames','IsolatedWorldEmbedderWorldIds']
for ext in ['cc','h']:
 rel=root+'.'+ext;before=(S/rel).read_text();after=before
 if ext=='cc':
  after=after.replace('#include "third_party/blink/renderer/platform/bindings/dom_wrapper_world.h"','#include "third_party/blink/renderer/platform/bindings/dom_wrapper_world.h"\n#if defined(__AROS__)\n#include "base/aros/process_local.h"\n#endif')
  for typ in types:
   old=f'  DEFINE_STATIC_LOCAL({typ}, map, ());\n  return map;';assert after.count(old)==1;after=after.replace(old,f'''#if defined(__AROS__)
  struct {typ}OwnerTag;
  return base::aros::ProcessLocalValue<{typ}, {typ}OwnerTag>();
#else
{old}
#endif''')
  old='unsigned DOMWrapperWorld::number_of_non_main_worlds_in_main_thread_ = 0;';assert after.count(old)==1;after=after.replace(old,'#if defined(__AROS__)\nthread_local '+old+'\n#else\n'+old+'\n#endif')
  old='      static int next_devtools_isolated_world_id =';assert after.count(old)==1;after=after.replace(old,'#if defined(__AROS__)\n      static thread_local int next_devtools_isolated_world_id =\n#else\n'+old+'\n#endif')
 else:
  old='  static unsigned number_of_non_main_worlds_in_main_thread_;';assert after.count(old)==1;after=after.replace(old,'#if defined(__AROS__)\n  static thread_local unsigned number_of_non_main_worlds_in_main_thread_;\n#else\n'+old+'\n#endif')
 for v,t in [('before',before),('candidate',after)]:
  p=D/v/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t)
 m['files'][rel]={'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()};patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
def method(text,anchor):
 start=text.index(anchor);pos=text.index('{',start);depth=1;end=pos+1
 while depth:
  depth+=(text[end]=='{')-(text[end]=='}');end+=1
 return text[start:end]
helper=(S/'base/aros/process_local.h').read_text();helper=helper[helper.index('template <typename T, typename Tag>'):helper.index('}  // namespace base::aros')]
prefix='''#include <map>
#include <memory>
#include <mutex>
#include <cstdint>
#include <string>
#include <cstdio>
#define __AROS__ 1
#define DCHECK(v) do{}while(0)
#define DEFINE_STATIC_LOCAL(Type,Name,Args) static Type Name
namespace base{using Lock=std::mutex;using AutoLock=std::lock_guard<std::mutex>;template<class T>struct NoDestructor{T value;T*operator->(){return &value;}};namespace aros{uint64_t owner=0;uint64_t CurrentProcessIdentity(){return owner;}
'''+helper+'''}}
'''+''.join('using '+typ+'=std::map<int,std::string>;\n' for typ in types)
results={}
for v in ['before','candidate']:
 text=(D/v/(root+'.cc')).read_text();bodies='\n'.join(method(text,'static '+typ+'& '+getter+'() {') for typ,getter in zip(types,getters));test='int main(){int errors=0;\n'
 for getter in getters:test+='''base::aros::owner=1;GETTER()[42]="owner-A";base::aros::owner=2;if(!GETTER().empty())++errors;GETTER()[42]="owner-B";base::aros::owner=1;if(GETTER()[42]!="owner-A")++errors;GETTER().erase(42);base::aros::owner=2;if(GETTER()[42]!="owner-B")++errors;\n'''.replace('GETTER',getter)
 test+='printf("world-map ownership errors=%d\\n",errors);return errors?42:0;}';p=D/(v+'.cc');p.write_text(prefix+bodies+test);subprocess.run(['c++','-std=c++20','-pthread','-fsanitize=address,undefined',str(p),'-o',str(D/(v+'-test'))],check=True);r=subprocess.run([str(D/(v+'-test'))],capture_output=True,text=True);results[v]={'exit_code':r.returncode,'output':r.stdout+r.stderr};assert r.returncode==(42 if v=='before' else 0),results
(D/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');(D/'candidate.patch').write_text(patch);(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Four actual map getters plus ProcessLocalValue; mocked map value/allocator. Same world ID across logical owners and independent erase. Task-local count/devtools counter source reviewed; native extension/profile isolation remains unqualified.'},indent=2)+'\n');print(results)
