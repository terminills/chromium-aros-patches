from pathlib import Path
import subprocess,json
D=Path(__file__).parent/'dom-worlds220-draft'
def method(text,anchor):
 a=text.index(anchor);b=text.index('{',a);depth=1;i=b+1
 while depth:depth+=(text[i]=='{')-(text[i]=='}');i+=1
 return text[a:i]
prefix="""#include <optional>
#include <thread>
#include <cstdio>
#include <cstdlib>
#define __AROS__ 1
#define DCHECK(x) do{}while(0)
#define CHECK_GE(a,b) do{}while(0)
#define NOTREACHED() std::abort()
bool IsMainThread(){return true;}
namespace IsolatedWorldId{constexpr int kDevToolsFirstIsolatedWorldId=100;constexpr int kDevToolsLastIsolatedWorldId=101;}
struct DOMWrapperWorld {enum class WorldType{kMain,kIsolated,kInspectorIsolated,kForV8ContextSnapshotNonMain,kWorkerOrWorklet,kShadowRealm};static constexpr int kMainWorldId=0,kUnspecifiedWorldIdStart=200;static std::optional<int> GenerateWorldIdForType(WorldType);};
constinit thread_local int next_world_id=200;
"""
test="""int main(){int errors=0;std::thread a([&]{for(int i=0;i<2;i++){auto v=DOMWrapperWorld::GenerateWorldIdForType(DOMWrapperWorld::WorldType::kInspectorIsolated);if(!v||*v!=100+i)++errors;}if(DOMWrapperWorld::GenerateWorldIdForType(DOMWrapperWorld::WorldType::kInspectorIsolated))++errors;});a.join();std::thread b([&]{auto v=DOMWrapperWorld::GenerateWorldIdForType(DOMWrapperWorld::WorldType::kInspectorIsolated);if(!v||*v!=100)++errors;});b.join();printf("independent world ID errors=%d\\n",errors);return errors?42:0;}"""
results={}
for version in ['before','candidate']:
 text=(D/version/'third_party/blink/renderer/platform/bindings/dom_wrapper_world.cc').read_text();body=method(text,'std::optional<int> DOMWrapperWorld::GenerateWorldIdForType(');src=D/(version+'-ids.cc');src.write_text(prefix+body+test);exe=D/(version+'-ids');subprocess.run(['c++','-std=c++20','-pthread','-fsanitize=address,undefined',str(src),'-o',str(exe)],check=True);r=subprocess.run([str(exe)],capture_output=True,text=True);results[version]={'exit_code':r.returncode,'output':r.stdout+r.stderr};assert r.returncode==(42 if version=='before' else 0),results
(D/'id-host-results.json').write_text(json.dumps({'results':results,'scope':'Actual ID generation method; mocked isolate-world range of two IDs. A exhausts its range; B receives its independent first ID. Host thread model only, not native DevTools qualification.'},indent=2)+'\n');print(results)
