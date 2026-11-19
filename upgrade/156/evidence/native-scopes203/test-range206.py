from pathlib import Path
import json,hashlib,difflib,subprocess
E=Path(__file__).parent;D=E/'range206-draft';D.mkdir(exist_ok=True);S=Path('/mnt/short-term/job0254-01a1e62b/src');rel='third_party/blink/renderer/core/dom/range.cc';before=(S/rel).read_text();after=before
for old in ['  static int scope_count_;','  static Range* current_range_;','int RangeUpdateScope::scope_count_ = 0;','Range* RangeUpdateScope::current_range_;']:
 assert after.count(old)==1;new=old.replace('static ','static thread_local ') if old.startswith('  ') else 'thread_local '+old;after=after.replace(old,'#if defined(__AROS__)\n'+new+'\n#else\n'+old+'\n#endif')
for variant,text in [('before',before),('candidate',after)]:
 p=D/variant/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
(D/'manifest.json').write_text(json.dumps({'files':{rel:{'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()}}},indent=2)+'\n');(D/'candidate.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)))
prefix='''#include <thread>
#include <mutex>
#include <condition_variable>
#include <cstdio>
#define __AROS__ 1
#define STACK_ALLOCATED()
#define DCHECK_IS_ON() 0
int errors=0;
#define DCHECK(v) do{if(!(v))++errors;}while(0)
#define DCHECK_GE(a,b) DCHECK((a)>=(b))
struct Settings{bool GetDoNotUpdateSelectionOnMutatingSelectionRange(){return false;}};
struct Frame{Settings s;Settings*GetSettings(){return &s;}};
struct Document{Frame f;Frame*GetFrame(){return &f;}bool operator!=(Document&x){return this!=&x;}};
struct Range{Document d;int updated=0,reset=0,visual=0;Document&OwnerDocument(){return d;}void RemoveFromSelectionIfInDifferentRoot(Document&){}void UpdateSelectionIfAddedToSelection(){++updated;}void ResetUpdateSelectionBehavior(){++reset;}void ScheduleVisualUpdateIfInRegisteredHighlight(Document&){++visual;}};
'''
main='''std::mutex m;std::condition_variable cv;int phase=0;void set(int n){std::lock_guard<std::mutex>l(m);phase=n;cv.notify_all();}void wait(int n){std::unique_lock<std::mutex>l(m);cv.wait(l,[&]{return phase>=n;});}
int main(){Range a,b;std::thread x([&]{{RangeUpdateScope s(&a);set(1);wait(2);}set(3);});std::thread y([&]{wait(1);{RangeUpdateScope s(&b);}set(2);wait(3);});x.join();y.join();printf("A updates=%d B updates=%d\\n",a.updated,b.updated);return a.updated==1&&b.updated==1&&a.reset==1&&b.reset==1&&a.visual==1&&b.visual==1?0:42;}
'''
results={}
for v,text in [('before',before),('candidate',after)]:
 body=text[text.index('class RangeUpdateScope {'):text.index('Range::Range(Document&')];p=D/(v+'.cc');p.write_text(prefix+body+main);subprocess.run(['c++','-std=c++20','-pthread','-fsanitize=address,undefined',str(p),'-o',str(D/(v+'-test'))],check=True);r=subprocess.run([str(D/(v+'-test'))],capture_output=True,text=True);results[v]={'exit_code':r.returncode,'output':r.stdout+r.stderr};assert r.returncode==(42 if v=='before' else 0),results
(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Verbatim RangeUpdateScope; mocked Range/Document/Settings; controlled nested cross-renderer lifetime. Host only, not native selection proof.'},indent=2)+'\n');print(results)
