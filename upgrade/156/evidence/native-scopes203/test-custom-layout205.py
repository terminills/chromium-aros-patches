from pathlib import Path
import hashlib,difflib,json,re,subprocess
E=Path(__file__).parent;D=E/'custom-layout205-draft';D.mkdir(exist_ok=True);S=Path('/mnt/short-term/job0254-01a1e62b/src');root='third_party/blink/renderer/core/layout/custom/custom_layout_scope';m={'files':{}};patch=''
for ext in ['cc','h']:
 rel=root+'.'+ext;before=(S/rel).read_text();old='  static CustomLayoutScope* current_scope_;' if ext=='h' else 'CustomLayoutScope* CustomLayoutScope::current_scope_ = nullptr;';assert before.count(old)==1;new=old.replace('static ','static thread_local ') if ext=='h' else 'thread_local '+old;after=before.replace(old,'#if defined(__AROS__)\n'+new+'\n#else\n'+old+'\n#endif')
 for v,t in [('before',before),('candidate',after)]:
  p=D/v/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t)
 m['files'][rel]={'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()};patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
results={}
for v in ['before','candidate']:
 code='''#include <thread>
#include <mutex>
#include <condition_variable>
#include <vector>
#include <cstdio>
#define __AROS__ 1
#define STACK_ALLOCATED()
int errors=0;
#define DCHECK_EQ(a,b) do{if((a)!=(b))++errors;}while(0)
struct Visitor{};template<class T>struct GarbageCollected{};template<class T>using Member=T*;template<class T,int N=0>using HeapVector=std::vector<T>;struct CustomLayoutWorkTask{};
template<class T>T* MakeGarbageCollected(){static thread_local std::vector<T*> owned;T*p=new T;owned.push_back(p);return p;}
'''
 for ext in ['h','cc']:code+=re.sub(r'^#include.*\n','',(D/v/(root+'.'+ext)).read_text(),flags=re.M)+'\n'
 code+='''using S=blink::CustomLayoutScope;
std::mutex m;std::condition_variable cv;int phase=0;void set(int n){std::lock_guard<std::mutex>l(m);phase=n;cv.notify_all();}void wait(int n){std::unique_lock<std::mutex>l(m);cv.wait(l,[&]{return phase>=n;});}
int main(){std::thread a([&]{{S x;set(1);wait(2);if(S::Current()!=&x)++errors;else if(!x.Token()->IsValid())++errors;{S y;if(S::Current()!=&y)++errors;}if(S::Current()!=&x)++errors;set(3);wait(4);}set(5);});std::thread b([&]{wait(1);{S x;set(2);wait(3);if(S::Current()!=&x)++errors;}set(4);wait(5);});a.join();b.join();printf("scope errors=%d\\n",errors);return errors?42:0;}
'''
 p=D/(v+'.cc');p.write_text(code);subprocess.run(['c++','-std=c++20','-pthread',str(p),'-o',str(D/(v+'-test'))],check=True);r=subprocess.run([str(D/(v+'-test'))],capture_output=True,text=True);results[v]={'exit_code':r.returncode,'output':r.stdout+r.stderr};assert r.returncode==(42 if v=='before' else 0),results
(D/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');(D/'candidate.patch').write_text(patch);(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Verbatim CustomLayoutScope and token implementation, mocked GC/container. Deterministic sibling and nesting checks; not native layout worklet proof.'},indent=2)+'\n');print(results)
