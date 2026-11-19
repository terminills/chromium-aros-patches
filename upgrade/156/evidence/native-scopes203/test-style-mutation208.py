from pathlib import Path
import json,hashlib,difflib,re,subprocess
E=Path(__file__).parent;D=E/'style-mutation208-draft';D.mkdir(exist_ok=True);S=Path('/mnt/short-term/job0254-01a1e62b/src');root='third_party/blink/renderer/core/css/style_attribute_mutation_scope';m={'files':{}};patch=''
for ext in ['h','cc']:
 rel=root+'.'+ext;before=(S/rel).read_text();after=before
 for field in ['scope_count_','current_element_','should_notify_inspector_','should_deliver_']:
  pat=(r'^  static [^\n;]+ '+field+r';$') if ext=='h' else (r'^[^\n]+ StyleAttributeMutationScope::'+field+r' = [^;]+;$');match=re.findall(pat,after,re.M);assert len(match)==1,(rel,field);old=match[0];new=old.replace('static ','static thread_local ') if ext=='h' else 'thread_local '+old;after=after.replace(old,'#if defined(__AROS__)\n'+new+'\n#else\n'+old+'\n#endif')
 for v,t in [('before',before),('candidate',after)]:
  p=D/v/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t)
 m['files'][rel]={'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()};patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
prefix='''#include <thread>
#include <mutex>
#include <condition_variable>
#include <cstdio>
#define __AROS__ 1
#define STACK_ALLOCATED()
#define DISABLE_CFI_PERF
int errors=0;
#define DCHECK(v) do{if(!(v))++errors;}while(0)
#define DCHECK_EQ(a,b) DCHECK((a)==(b))
namespace blink {
using AtomicString=int;constexpr int g_null_atom=0;namespace html_names{constexpr int kStyleAttr=1;}
struct Element{int notifications=0,mutations=0;int getAttribute(int){return 7;}};
struct AbstractPropertySetCSSStyleDeclaration{Element*e;Element*ParentElement(){return e;}};
struct MutationRecord{static MutationRecord*CreateAttributes(Element*,int,int){static thread_local MutationRecord r;return &r;}};
struct MutationObserverInterestGroup{Element*e;static MutationObserverInterestGroup*CreateForAttributesMutation(Element&e,int){static thread_local MutationObserverInterestGroup g;g.e=&e;return &g;}bool IsOldValueRequested(){return true;}void EnqueueMutationRecord(MutationRecord*){++e->mutations;}};
struct CustomElementDefinition{void EnqueueAttributeChangedCallback(Element&,int,int,int){}};
CustomElementDefinition*DefinitionIfStyleChangedCallback(Element*){return nullptr;}
namespace probe {void DidInvalidateStyleAttr(Element*e){++e->notifications;}}
}
'''
main='''using Scope=blink::StyleAttributeMutationScope;
std::mutex m;std::condition_variable cv;int phase=0;void set(int n){std::lock_guard<std::mutex>l(m);phase=n;cv.notify_all();}void wait(int n){std::unique_lock<std::mutex>l(m);cv.wait(l,[&]{return phase>=n;});}
int main(){blink::Element a,b;std::thread x([&]{{Scope s(&a);s.EnqueueMutationRecord();s.DidInvalidateStyleAttr();set(1);wait(2);}set(3);});std::thread y([&]{wait(1);{Scope s(&b);s.EnqueueMutationRecord();s.DidInvalidateStyleAttr();}set(2);wait(3);});x.join();y.join();printf("A mutations=%d notifications=%d B mutations=%d notifications=%d\\n",a.mutations,a.notifications,b.mutations,b.notifications);return a.mutations==1&&b.mutations==1&&a.notifications==1&&b.notifications==1?0:42;}
'''
results={}
for v in ['before','candidate']:
 h=re.sub(r'^#include.*\n','',(D/v/(root+'.h')).read_text(),flags=re.M);cc=(D/v/(root+'.cc')).read_text();start=cc.index('unsigned StyleAttributeMutationScope::scope_count_') if v=='before' else cc.index('#if defined(__AROS__)');body=cc[start:];code=prefix+h+'\nnamespace blink {\n'+body+main;p=D/(v+'.cc');p.write_text(code);subprocess.run(['c++','-std=c++20','-pthread','-fsanitize=address,undefined',str(p),'-o',str(D/(v+'-test'))],check=True);r=subprocess.run([str(D/(v+'-test'))],capture_output=True,text=True);results[v]={'exit_code':r.returncode,'output':r.stdout+r.stderr};assert r.returncode==(42 if v=='before' else 0),results
(D/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');(D/'candidate.patch').write_text(patch);(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Actual scope header and Initialize/destructor, mocked DOM/mutation recipients/inspector. Controlled cross-renderer overlap proves lost delivery before; both delivered after. Not full native mutation observer proof.'},indent=2)+'\n');print(results)
