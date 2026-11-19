from pathlib import Path
import subprocess,json,difflib,hashlib
E=Path(__file__).parent;D=E/'style195-draft';D.mkdir(exist_ok=True);S=Path('/mnt/short-term/job0254-01a1e62b/src');rel=Path('third_party/blink/renderer/core/css/post_style_update_scope');manifest={'files':{}};patch=[]
for ext in ['.cc','.h']:
 before=(S/(str(rel)+ext)).read_text();token='PostStyleUpdateScope* PostStyleUpdateScope::current_ = nullptr;' if ext=='.cc' else '  static PostStyleUpdateScope* current_;';after=before.replace(token,'#if defined(__AROS__)\n'+('thread_local '+token if ext=='.cc' else token.replace('static ','static thread_local '))+'\n#else\n'+token+'\n#endif');assert before!=after
 for label,s in [('before',before),('candidate',after)]:
  p=D/label/(str(rel)+ext);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
 manifest['files'][str(rel)+ext]={'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()};patch+=difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+str(rel)+ext,tofile='b/'+str(rel)+ext)
(D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(D/'candidate.patch').write_text(''.join(patch));results={}
for variant in ['before','candidate']:
 root=D/variant;s=(root/(str(rel)+'.cc')).read_text();methods=s[s.index('namespace blink {')+len('namespace blink {'):s.index('bool PostStyleUpdateScope::Apply()')];tls='thread_local ' if variant=='candidate' else ''
 code='''#include <vector>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <cassert>
#include <cstdio>
struct AssertStream{template<class T>AssertStream& operator<<(const T&){return *this;}};
#define DCHECK(x) (assert(x),AssertStream())
namespace blink {struct Document{};class PostStyleUpdateScope {public:struct AnimationData{std::vector<int> elements_with_pending_updates_;};struct PseudoData{std::vector<int> pending_backdrops_;};static AnimationData* CurrentAnimationData();static PseudoData* CurrentPseudoData();explicit PostStyleUpdateScope(Document&);~PostStyleUpdateScope();private:Document& document_;AnimationData animation_data_;PseudoData pseudo_data_;PseudoData* GetPseudoData(){return &pseudo_data_;}static '''+tls+'PostStyleUpdateScope* current_;};\n'+methods+'\n}\n'
 code+='''std::mutex m;std::condition_variable cv;int phase=0;void set(int p){std::lock_guard<std::mutex> l(m);phase=p;cv.notify_all();}void wait(int p){std::unique_lock<std::mutex> l(m);cv.wait(l,[&]{return phase>=p;});}
int main(){using namespace blink;Document d;PostStyleUpdateScope::AnimationData *a=nullptr,*b=nullptr;bool nested=false,restored=false;std::thread ta([&]{{PostStyleUpdateScope outer(d);a=PostStyleUpdateScope::CurrentAnimationData();{PostStyleUpdateScope inner(d);nested=PostStyleUpdateScope::CurrentAnimationData()==a;}set(1);wait(2);restored=PostStyleUpdateScope::CurrentAnimationData()==a;set(3);wait(4);}assert(PostStyleUpdateScope::CurrentAnimationData()==nullptr);});std::thread tb([&]{wait(1);{PostStyleUpdateScope outer(d);b=PostStyleUpdateScope::CurrentAnimationData();set(2);wait(3);}set(4);});ta.join();tb.join();printf("separate_animation_state=%d nested_outer_state=%d first_renderer_restored=%d\\n",a!=b,nested,restored);return a!=b&&nested&&restored?0:42;}
'''
 p=D/(variant+'-test.cc');p.write_text(code);r=subprocess.run(['c++','-std=c++20','-D__AROS__','-fsanitize=address,undefined','-pthread','-g',str(p),'-o',str(D/(variant+'-test'))],capture_output=True,text=True);(D/(variant+'-build.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
 r=subprocess.run([str(D/(variant+'-test'))],capture_output=True,text=True);(D/(variant+'-run.log')).write_text(r.stdout+r.stderr);results[variant]={'exit_code':r.returncode,'output':r.stdout+r.stderr};assert r.returncode==(42 if variant=='before' else 0),results
(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Verbatim production current-scope accessors and constructor/destructor with mocked Document and scope member types. Controlled host interleaving, not native CSS/animation qualification. Unapplied candidate.'},indent=2)+'\n');print(results)
