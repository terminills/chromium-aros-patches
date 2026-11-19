from pathlib import Path
import hashlib,json,difflib,subprocess
E=Path(__file__).parent;D=E/'null-interpolation219-draft';D.mkdir(exist_ok=True);S=Path('/mnt/short-term/job0254-01a1e62b/src');rel='third_party/blink/renderer/core/animation/underlying_value_owner.cc';before=(S/rel).read_text();old='  DEFINE_STATIC_LOCAL(NullValueWrapper, null_value_wrapper, ());';assert before.count(old)==1;after=before.replace('#include <memory>','#include <memory>\n\n#if defined(__AROS__)\n#include "base/aros/process_local.h"\n#endif').replace(old,'''#if defined(__AROS__)
  // This wrapper contains a Persistent belonging to the creating Oilpan heap.
  struct NullInterpolationOwnerTag;
  auto& null_value_wrapper =
      base::aros::ProcessLocalValue<NullValueWrapper, NullInterpolationOwnerTag>();
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
#define DEFINE_STATIC_LOCAL(Type,Name,Args) static Type Name
namespace base{using Lock=std::mutex;using AutoLock=std::lock_guard<std::mutex>;template<class T>struct NoDestructor{T value;T*operator->(){return &value;}};namespace aros{uint64_t owner=0;uint64_t CurrentProcessIdentity(){return owner;}
'''+helper+'''}}
struct InterpolationValue{uint64_t owner=base::aros::owner;};struct InterpolationValueGCed{InterpolationValue value;const InterpolationValue&underlying()const{return value;}};
struct NullValueWrapper{std::unique_ptr<InterpolationValueGCed> value=std::make_unique<InterpolationValueGCed>();};
struct UnderlyingValueOwner{InterpolationValue*value_=nullptr;explicit operator bool()const{return value_;}const InterpolationValue&Value()const;};
'''
main='''int main(){UnderlyingValueOwner value;base::aros::owner=1;auto&a=value.Value();base::aros::owner=2;auto&b=value.Value();bool separated=&a!=&b&&a.owner==1&&b.owner==2;const_cast<InterpolationValue&>(a).owner=0;bool sibling=b.owner==2;base::aros::owner=3;bool fresh=value.Value().owner==3;printf("separated=%d sibling=%d fresh=%d\\n",separated,sibling,fresh);return separated&&sibling&&fresh?0:42;}
'''
results={}
for v,t in [('before',before),('candidate',after)]:
 body=t[t.index('const InterpolationValue& UnderlyingValueOwner::Value() const {'):t.index('void UnderlyingValueOwner::Set(std::nullptr_t)')];p=D/(v+'.cc');p.write_text(prefix+body+main);subprocess.run(['c++','-std=c++20','-pthread','-fsanitize=address,undefined',str(p),'-o',str(D/(v+'-test'))],check=True);r=subprocess.run([str(D/(v+'-test'))],capture_output=True,text=True);results[v]={'exit_code':r.returncode,'output':r.stdout+r.stderr};assert r.returncode==(42 if v=='before' else 0),results
(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Actual Value getter and ProcessLocalValue template; mocked interpolation/GC wrapper. Ownership and simulated retirement isolation only, not native animations.'},indent=2)+'\n');print(results)
