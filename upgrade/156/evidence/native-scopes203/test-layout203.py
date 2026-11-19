from pathlib import Path
import subprocess,json,hashlib,difflib
E=Path(__file__).parent;D=E/'layout203-draft';D.mkdir(exist_ok=True);S=Path('/mnt/short-term/job0254-01a1e62b/src');root='third_party/blink/renderer/core/layout/layout_shift_tracker';manifest={'files':{}};patch=''
for ext in ['cc','h']:
 rel=root+'.'+ext;before=(S/rel).read_text();after=before
 for cls in ['ReattachHookScope','ContainingBlockScope']:
  old=('    static '+cls+'* top_;') if ext=='h' else cls+'* '+cls+'::top_ = nullptr;'
  new=old.replace('static ','static thread_local ') if ext=='h' else 'thread_local '+old
  assert after.count(old)==1
  after=after.replace(old,'#if defined(__AROS__)\n'+new+'\n#else\n'+old+'\n#endif')
 for variant,text in [('before',before),('candidate',after)]:
  p=D/variant/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
 manifest['files'][rel]={'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()}
 patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
(D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(D/'candidate.patch').write_text(patch)
cc=(S/(root+'.cc')).read_text();h=(S/(root+'.h')).read_text();methods=cc[cc.index('ReattachHookScope::ReattachHookScope('):cc.index('void ReattachHookScope::NotifyDetach')]
block=h[h.index('    ContainingBlockScope(const PhysicalSize&'):h.index('    ContainingBlockScope(const ContainingBlockScope&)')]
prefix='''#include <thread>
#include <mutex>
#include <condition_variable>
#include <cstdio>
struct Node {bool layout;bool GetLayoutObject()const{return layout;}};
struct PhysicalSize{};struct PhysicalRect{};
int errors=0;
#define DCHECK_EQ(a,b) do {if((a)!=(b))++errors;}while(0)
'''
main='''
std::mutex mutex;std::condition_variable cv;int phase=0;
void set(int x){std::lock_guard<std::mutex> l(mutex);phase=x;cv.notify_all();}
void wait(int x){std::unique_lock<std::mutex> l(mutex);cv.wait(l,[&]{return phase>=x;});}
int main(){Node n{true},none{false};PhysicalSize s;PhysicalRect r;
std::thread a([&]{ReattachHookScope x(n);ContainingBlockScope y(s,s,r,r);set(1);wait(2);
if(ReattachHookScope::top_!=&x || ContainingBlockScope::top_!=&y)++errors;
{ReattachHookScope z(n);ContainingBlockScope w(s,s,r,r);if(ReattachHookScope::top_!=&z || ContainingBlockScope::top_!=&w)++errors;}
if(ReattachHookScope::top_!=&x || ContainingBlockScope::top_!=&y)++errors;
{ReattachHookScope inactive(none);if(ReattachHookScope::top_!=&x)++errors;}
set(3);wait(4);});
std::thread b([&]{wait(1);{ReattachHookScope x(n);ContainingBlockScope y(s,s,r,r);set(2);wait(3);if(ReattachHookScope::top_!=&x || ContainingBlockScope::top_!=&y)++errors;}set(4);});
a.join();b.join();printf("scope ownership errors=%d\\n",errors);return errors?42:0;}
'''
results={}
for variant in ['before','candidate']:
 tls='thread_local ' if variant=='candidate' else ''
 code=prefix+'struct ReattachHookScope {ReattachHookScope(const Node&);~ReattachHookScope();ReattachHookScope* outer_;static '+tls+'ReattachHookScope* top_;};\n'+tls+'ReattachHookScope* ReattachHookScope::top_=nullptr;\n'+methods+'struct ContainingBlockScope {\n'+block+'ContainingBlockScope* outer_;PhysicalSize old_size_,new_size_;PhysicalRect old_rect_,new_rect_;static '+tls+'ContainingBlockScope* top_;};\n'+tls+'ContainingBlockScope* ContainingBlockScope::top_=nullptr;\n'+main
 p=D/(variant+'.cc');p.write_text(code);subprocess.run(['c++','-std=c++20','-pthread','-fsanitize=address,undefined',str(p),'-o',str(D/variant/'test')],check=True)
 r=subprocess.run([str(D/variant/'test')],capture_output=True,text=True);results[variant]={'exit_code':r.returncode,'output':r.stdout+r.stderr};assert r.returncode==(42 if variant=='before' else 0),results
(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Extracted production constructors/destructors; mocked Node and geometry, deterministic host-thread interleaving and nested restoration. No native browser qualification.'},indent=2)+'\n');print(results)
