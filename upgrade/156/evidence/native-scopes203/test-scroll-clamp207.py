from pathlib import Path
import re,json,hashlib,difflib,subprocess
E=Path(__file__).parent;D=E/'scroll-clamp207-draft';D.mkdir(exist_ok=True);S=Path('/mnt/short-term/job0254-01a1e62b/src');root='third_party/blink/renderer/core/paint/paint_layer_scrollable_area';m={'files':{}};patch=''
for ext in ['h','cc']:
 rel=root+'.'+ext;before=(S/rel).read_text();after=before
 if ext=='h':
  old='    static int count_;';assert after.count(old)==2;after=after.replace(old,'#if defined(__AROS__)\n    static thread_local int count_;\n#else\n'+old+'\n#endif')
 else:
  for cls in ['FreezeScrollbarsScope','DelayScrollOffsetClampScope']:
   old='int PaintLayerScrollableArea::'+cls+'::count_ = 0;';assert after.count(old)==1;after=after.replace(old,'#if defined(__AROS__)\nthread_local '+old+'\n#else\n'+old+'\n#endif')
 for v,t in [('before',before),('candidate',after)]:
  p=D/v/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t)
 m['files'][rel]={'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()};patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
cc=(S/(root+'.cc')).read_text();ctor=cc[cc.index('PaintLayerScrollableArea::DelayScrollOffsetClampScope::\n    DelayScrollOffsetClampScope()'):cc.index('void PaintLayerScrollableArea::DelayScrollOffsetClampScope::SetNeedsClamp')]
results={}
for v in ['before','candidate']:
 tls='thread_local ' if v=='candidate' else ''
 code='''#include <thread>
#include <mutex>
#include <condition_variable>
#include <vector>
#include <cstdio>
int errors=0;
#define DCHECK(v) do{if(!(v))++errors;}while(0)
struct PaintLayerScrollableArea {struct DelayScrollOffsetClampScope {
DelayScrollOffsetClampScope();~DelayScrollOffsetClampScope();
static std::vector<int>& NeedsClampList(){static thread_local std::vector<int> list;return list;}
static int& Clamped(){static thread_local int n=0;return n;}
static void ClampScrollableAreas(){Clamped()+=NeedsClampList().size();NeedsClampList().clear();}
static TLS int count_;
};};
TLS int PaintLayerScrollableArea::DelayScrollOffsetClampScope::count_=0;
'''.replace('TLS ',tls)+ctor+'''
using Scope=PaintLayerScrollableArea::DelayScrollOffsetClampScope;
std::mutex m;std::condition_variable cv;int phase=0;void set(int n){std::lock_guard<std::mutex>l(m);phase=n;cv.notify_all();}void wait(int n){std::unique_lock<std::mutex>l(m);cv.wait(l,[&]{return phase>=n;});}
int main(){int ac=0,bc=0;std::thread a([&]{{Scope s;Scope::NeedsClampList().push_back(1);set(1);wait(2);}ac=Scope::Clamped();set(3);});std::thread b([&]{wait(1);{Scope s;Scope::NeedsClampList().push_back(2);set(2);wait(3);}bc=Scope::Clamped();});a.join();b.join();printf("A clamped=%d B clamped=%d\\n",ac,bc);return ac==1&&bc==1?0:42;}
'''
 p=D/(v+'.cc');p.write_text(code);subprocess.run(['c++','-std=c++20','-pthread','-fsanitize=address,undefined',str(p),'-o',str(D/(v+'-test'))],check=True);r=subprocess.run([str(D/(v+'-test'))],capture_output=True,text=True);results[v]={'exit_code':r.returncode,'output':r.stdout+r.stderr};assert r.returncode==(42 if v=='before' else 0),results
(D/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');(D/'candidate.patch').write_text(patch);(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Actual delayed-clamp ctor/dtor with mocked per-renderer pending list matching existing Persistent singleton ownership. Before misses A clamp; task-local count drains both. Freeze count source-reviewed only; native pending.'},indent=2)+'\n');print(results)
