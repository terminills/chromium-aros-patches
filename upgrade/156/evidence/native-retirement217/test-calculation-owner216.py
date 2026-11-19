from pathlib import Path
import json,hashlib,difflib,subprocess
E=Path(__file__).parent;D=E/'calculation-owner216-draft';D.mkdir(exist_ok=True);S=Path('/mnt/short-term/job0254-01a1e62b/src');rel='third_party/blink/renderer/platform/geometry/length.cc';before=(S/rel).read_text();old='''  DEFINE_STATIC_LOCAL(CalculationValueHandleMap, handle_map, ());
  return handle_map;''';assert before.count(old)==1;after=before.replace('#include <array>','#include <array>\n\n#if defined(__AROS__)\n#include "base/aros/process_local.h"\n#endif');after=after.replace(old,'''#if defined(__AROS__)
  // The wrapper owns an Oilpan Persistent internally, so the generic
  // Persistent-only static trait cannot infer its renderer ownership.
  struct CalculationValueHandlesOwnerTag;
  return base::aros::ProcessLocalValue<CalculationValueHandleMap,
                                      CalculationValueHandlesOwnerTag>();
#else
'''+old+'\n#endif')
for v,t in [('before',before),('candidate',after)]:
 p=D/v/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t)
(D/'manifest.json').write_text(json.dumps({'files':{rel:{'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()}}},indent=2)+'\n');(D/'candidate.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)))
helper=(S/'base/aros/process_local.h').read_text();helper=helper[helper.index('template <typename T, typename Tag>'):helper.index('}  // namespace base::aros')]
prefix='''#include <map>
#include <memory>
#include <mutex>
#include <cstdint>
#include <cstdio>
#define __AROS__ 1
#define DCHECK(v) do{}while(0)
#define DEFINE_STATIC_LOCAL(Type,Name,Args) static Type Name
namespace base {using Lock=std::mutex;using AutoLock=std::lock_guard<std::mutex>;template<class T>struct NoDestructor{T value;T*operator->(){return &value;}};namespace aros {uint64_t owner=0;uint64_t CurrentProcessIdentity(){return owner;}
'''+helper+'''} }
struct CalculationValueHandleMap {uint64_t root_owner=base::aros::owner;};
'''
main='''int main(){base::aros::owner=1;auto&a=CalcHandles();base::aros::owner=2;auto&b=CalcHandles();bool distinct=&a!=&b;bool owners=a.root_owner==1&&b.root_owner==2;a.root_owner=0;bool sibling_alive=b.root_owner==2;bool same_owner=&CalcHandles()==&b;base::aros::owner=3;auto&c=CalcHandles();bool replacement=c.root_owner==3;printf("distinct=%d owners=%d sibling_survives_retirement=%d same_owner=%d new_owner_fresh=%d\\n",distinct,owners,sibling_alive,same_owner,replacement);return distinct&&owners&&sibling_alive&&same_owner&&replacement?0:42;}
'''
results={}
for v,t in [('before',before),('candidate',after)]:
 body=t[t.index('static CalculationValueHandleMap& CalcHandles() {'):t.index('Length::Length(const CalculationValue*')];p=D/(v+'.cc');p.write_text(prefix+body+main);subprocess.run(['c++','-std=c++20','-pthread','-fsanitize=address,undefined',str(p),'-o',str(D/(v+'-test'))],check=True);r=subprocess.run([str(D/(v+'-test'))],capture_output=True,text=True);results[v]={'exit_code':r.returncode,'output':r.stdout+r.stderr};assert r.returncode==(42 if v=='before' else 0),results
(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Actual CalcHandles getter and ProcessLocalValue template, mocked GC-owning wrapper and locks/static wrapper. Checks distinct owner, sibling after root retirement, same-owner reuse and new owner. Not native Oilpan qualification.'},indent=2)+'\n');print(results)
