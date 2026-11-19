from pathlib import Path
import re,hashlib,difflib,json,subprocess
E=Path(__file__).parent;D=E/'render-guards204-draft';D.mkdir(exist_ok=True);S=Path('/mnt/short-term/job0254-01a1e62b/src');base='third_party/blink/renderer/'
items=[('core/layout/disable_layout_side_effects_scope','DisableLayoutSideEffectsScope',['count_'],'IsDisabled()'),('core/paint/pre_paint_disable_side_effects_scope','PrePaintDisableSideEffectsScope',['count_'],'IsDisabled()'),('core/editing/markers/suggestion_marker_replacement_scope','SuggestionMarkerReplacementScope',['currently_in_scope_'],'CurrentlyInScope()'),('platform/graphics/paint/ignore_paint_timing_scope','IgnorePaintTimingScope',['ignore_depth_','is_document_element_invisible_'],'ShouldIgnore()')]
manifest={'files':{}};patch='';results={}
for stem,cls,fields,getter in items:
 for ext in ['h','cc']:
  rel=base+stem+'.'+ext;before=(S/rel).read_text();after=before
  for field in fields:
   pattern=(r'^  static [^\n;]+ '+field+r';$') if ext=='h' else (r'^\w+ '+cls+'::'+field+r' = [^;]+;$')
   match=re.findall(pattern,after,re.M);assert len(match)==1,(rel,field,match);old=match[0];new=old.replace('static ','static thread_local ') if ext=='h' else 'thread_local '+old
   after=after.replace(old,'#if defined(__AROS__)\n'+new+'\n#else\n'+old+'\n#endif')
  for variant,text in [('before',before),('candidate',after)]:
   p=D/variant/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
  manifest['files'][rel]={'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()}
  patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
 testresults={}
 for variant in ['before','candidate']:
  code='''#include <thread>
#include <mutex>
#include <condition_variable>
#include <cstdio>
#define __AROS__ 1
#define CORE_EXPORT
#define PLATFORM_EXPORT
#define STACK_ALLOCATED()
int errors=0;
#define DCHECK(v) do{if(!(v))++errors;}while(0)
namespace base {template<class T>struct AutoReset{T*p,old;AutoReset(T*q,T value):p(q),old(*q){*p=value;}~AutoReset(){*p=old;}};}
'''
  for ext in ['h','cc']:
   text=(D/variant/(base+stem+'.'+ext)).read_text();text=re.sub(r'^#include.*\n','',text,flags=re.M);code+=text+'\n'
  code+='using Scope=blink::'+cls+';\n'
  setup='Scope::IncrementIgnoreDepth();' if cls=='IgnorePaintTimingScope' else ''
  code+='''std::mutex m;std::condition_variable cv;int phase=0;
void set(int x){std::lock_guard<std::mutex> l(m);phase=x;cv.notify_all();}void wait(int x){std::unique_lock<std::mutex> l(m);cv.wait(l,[&]{return phase>=x;});}
int main(){std::thread a([&]{{Scope s;SETUP set(1);wait(2);}set(3);});std::thread b([&]{wait(1);if(Scope::GETTER)++errors;set(2);wait(3);{Scope s;SETUP if(!Scope::GETTER)++errors;}if(Scope::GETTER)++errors;});a.join();b.join();printf("errors=%d\\n",errors);return errors?42:0;}
'''.replace('SETUP',setup).replace('GETTER',getter)
  p=D/(cls+'-'+variant+'.cc');p.write_text(code);out=D/(cls+'-'+variant);subprocess.run(['c++','-std=c++20','-pthread','-fsanitize=address,undefined',str(p),'-o',str(out)],check=True);r=subprocess.run([str(out)],capture_output=True,text=True);testresults[variant]={'exit_code':r.returncode,'output':r.stdout+r.stderr};assert r.returncode==(42 if variant=='before' else 0),testresults
 results[cls]=testresults
(D/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(D/'candidate.patch').write_text(patch);(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Full extracted scope headers and implementation with assertions/AutoReset mocked. Ordered host threads test sibling inactive state and restoration. Private drafts only; frozen203 source untouched.'},indent=2)+'\n');print(results)
