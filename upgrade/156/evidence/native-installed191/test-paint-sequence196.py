from pathlib import Path
import subprocess,json,hashlib,difflib
E=Path(__file__).parent;D=E/'paint-sequence196-draft';D.mkdir(exist_ok=True);S=Path('/mnt/short-term/job0254-01a1e62b/src');rel=Path('third_party/blink/renderer/platform/graphics/compositing/paint_artifact_compositor.cc');before=(S/rel).read_text();token='static int g_s_property_tree_sequence_number = 1;';after=before.replace(token,'#if defined(__AROS__)\n// Each native renderer updates its property trees on its own main task.\nstatic thread_local int g_s_property_tree_sequence_number = 1;\n#else\n'+token+'\n#endif');assert before!=after
for name,source in [('before',before),('candidate',after)]:
 p=D/name/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(source)
(D/'manifest.json').write_text(json.dumps({'files':{str(rel):{'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()}}},indent=2)+'\n');(D/'candidate.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+str(rel),tofile='b/'+str(rel))))
s=(S/'cc/layers/layer.cc').read_text();start=s.index('int Layer::effect_tree_index(const PropertyTrees& property_trees) const {');end=s.index('\nbool Layer::effect_tree_index_is_valid',start);method=s[start:end];results={}
for variant,source in [('before',before),('candidate',after)]:
 declaration=token if variant=='before' else 'static thread_local int g_s_property_tree_sequence_number = 1;';assert declaration in source
 code='''#include <mutex>
#include <condition_variable>
#include <thread>
#include <cstdio>
namespace cc {constexpr int kInvalidPropertyNodeId=-1;struct PropertyTrees{int sequence;int sequence_number()const{return sequence;}};class Layer{public:struct Value{int value;int Read(const Layer&)const{return value;}};Value property_tree_sequence_number_;Value effect_tree_index_;int effect_tree_index(const PropertyTrees&)const;};
'''+method+'\n}\n'+declaration+'\n'
 code+='''std::mutex m;std::condition_variable cv;int phase=0;void set(int x){std::lock_guard<std::mutex> l(m);phase=x;cv.notify_all();}void wait(int x){std::unique_lock<std::mutex> l(m);cv.wait(l,[&]{return phase>=x;});}
int main(){int index=-2;std::thread a([&]{cc::Layer layer{{g_s_property_tree_sequence_number},{3}};set(1);wait(2);cc::PropertyTrees trees{g_s_property_tree_sequence_number};index=layer.effect_tree_index(trees);});std::thread b([&]{wait(1);++g_s_property_tree_sequence_number;set(2);});a.join();b.join();printf("effect_tree_index=%d expected=3\\n",index);return index==3?0:42;}
'''
 p=D/(variant+'-test.cc');p.write_text(code);r=subprocess.run(['c++','-std=c++20','-fsanitize=address,undefined','-pthread','-g',str(p),'-o',str(D/(variant+'-test'))],capture_output=True,text=True);(D/(variant+'-build.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
 r=subprocess.run([str(D/(variant+'-test'))],capture_output=True,text=True);(D/(variant+'-run.log')).write_text(r.stdout+r.stderr);results[variant]={'exit_code':r.returncode,'output':r.stdout+r.stderr};assert r.returncode==(42 if variant=='before' else 0),results
(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Model of interleaved PaintArtifactCompositor sequence reads/increment using production counter declaration and verbatim Layer::effect_tree_index with mocked Layer storage. Not a full compositor execution or native proof. Matches native191 invalid index symptom but alternative causes remain until replay.'},indent=2)+'\n');print(results)
