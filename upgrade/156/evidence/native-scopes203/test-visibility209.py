from pathlib import Path
import hashlib,difflib,json,subprocess
E=Path(__file__).parent;D=E/'visibility209-draft';D.mkdir(exist_ok=True);S=Path('/mnt/short-term/job0254-01a1e62b/src');base='third_party/blink/renderer/core/';m={'files':{}};patch=''
items={'fullscreen/fullscreen.cc':['  static bool running_request_fullscreen_;','bool RequestFullscreenScope::running_request_fullscreen_ = false;'],'paint/paint_layer.h':['  static bool should_check_;'],'paint/paint_layer.cc':['bool CheckAncestorPositionVisibilityScope::should_check_ = false;']}
for name,lines in items.items():
 rel=base+name;before=(S/rel).read_text();after=before
 for old in lines:
  assert after.count(old)==1;new=old.replace('static ','static thread_local ') if 'static ' in old else 'thread_local '+old;after=after.replace(old,'#if defined(__AROS__)\n'+new+'\n#else\n'+old+'\n#endif')
 for v,t in [('before',before),('candidate',after)]:
  p=D/v/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t)
 m['files'][rel]={'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()};patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
results={}
for cls in ['RequestFullscreenScope','CheckAncestorPositionVisibilityScope']:
 results[cls]={}
 for v in ['before','candidate']:
  if cls=='RequestFullscreenScope':
   text=(D/v/(base+'fullscreen/fullscreen.cc')).read_text();body=text[text.index('class RequestFullscreenScope {'):text.index('// Walks the frame tree')];construct='Scope s;';getter='RunningRequestFullscreen()'
  else:
   text=(D/v/(base+'paint/paint_layer.h')).read_text();body=text[text.index('class CheckAncestorPositionVisibilityScope {'):text.index('#if DCHECK_IS_ON()',text.index('class CheckAncestorPositionVisibilityScope {'))];body+=('thread_local ' if v=='candidate' else '')+'bool CheckAncestorPositionVisibilityScope::should_check_=false;\n';construct='PaintLayer p;Scope s(p);';getter='ShouldCheck()'
  code='''#include <thread>
#include <mutex>
#include <condition_variable>
#include <cstdio>
#define __AROS__ 1
#define STACK_ALLOCATED()
int errors=0;
#define DCHECK(v) do{if(!(v))++errors;}while(0)
#define CHECK(v) DCHECK(v)
namespace base {template<class T>struct AutoReset {T*p,old;AutoReset(T*q,T v):p(q),old(*q){*p=v;}~AutoReset(){*p=old;}};}
struct PaintLayer{bool descendant_needs_check_position_visibility_=true;const PaintLayer&GetLayoutObject()const{return *this;}bool IsStackingContext()const{return true;}};
'''+body+'using Scope='+cls+';\n'+'''
std::mutex m;std::condition_variable cv;int phase=0;void set(int n){std::lock_guard<std::mutex>l(m);phase=n;cv.notify_all();}void wait(int n){std::unique_lock<std::mutex>l(m);cv.wait(l,[&]{return phase>=n;});}
int main(){std::thread a([&]{{CONSTRUCT set(1);wait(2);}set(3);});std::thread b([&]{wait(1);if(Scope::GETTER)++errors;set(2);wait(3);{CONSTRUCT if(!Scope::GETTER)++errors;}if(Scope::GETTER)++errors;});a.join();b.join();printf("errors=%d\\n",errors);return errors?42:0;}
'''.replace('CONSTRUCT',construct).replace('GETTER',getter)
  p=D/(cls+'-'+v+'.cc');p.write_text(code);out=D/(cls+'-'+v);subprocess.run(['c++','-std=c++20','-pthread','-fsanitize=address,undefined',str(p),'-o',str(out)],check=True);r=subprocess.run([str(out)],capture_output=True,text=True);results[cls][v]={'exit_code':r.returncode,'output':r.stdout+r.stderr};assert r.returncode==(42 if v=='before' else 0),results
(D/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');(D/'candidate.patch').write_text(patch);(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Actual extracted scope classes; mocked stacking-context/AutoReset; host sibling and restoration checks only.'},indent=2)+'\n');print(results)
