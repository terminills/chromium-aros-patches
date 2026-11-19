from pathlib import Path
import json,hashlib,difflib,re,subprocess
E=Path(__file__).parent;D=E/'xml-scope210-draft';D.mkdir(exist_ok=True);S=Path('/mnt/short-term/job0254-01a1e62b/src');root='third_party/blink/renderer/core/xml/parser/xml_document_parser_scope';m={'files':{}};patch=''
for ext in ['h','cc']:
 rel=root+'.'+ext;before=(S/rel).read_text();old='  static Document* current_document_;' if ext=='h' else 'Document* XMLDocumentParserScope::current_document_ = nullptr;';assert before.count(old)==1;new=old.replace('static ','static thread_local ') if ext=='h' else 'thread_local '+old;after=before.replace(old,'#if defined(__AROS__)\n'+new+'\n#else\n'+old+'\n#endif')
 for v,t in [('before',before),('candidate',after)]:
  p=D/v/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(t)
 m['files'][rel]={'before':hashlib.sha256(before.encode()).hexdigest(),'after':hashlib.sha256(after.encode()).hexdigest()};patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))
results={}
for v in ['before','candidate']:
 code='''#include <thread>
#include <mutex>
#include <condition_variable>
#include <cstdio>
#define __AROS__ 1
#define STACK_ALLOCATED()
using xmlGenericErrorFunc=void(*)();using xmlStructuredErrorFunc=void(*)();
thread_local xmlGenericErrorFunc xmlGenericError=nullptr;thread_local xmlStructuredErrorFunc xmlStructuredError=nullptr;thread_local void*xmlGenericErrorContext=nullptr;thread_local void*structured_context=nullptr;
void xmlSetGenericErrorFunc(void*c,xmlGenericErrorFunc f){xmlGenericErrorContext=c;xmlGenericError=f;}
void xmlSetStructuredErrorFunc(void*c,xmlStructuredErrorFunc f){structured_context=c;xmlStructuredError=f;}
namespace blink{struct Document{};}
'''
 for ext in ['h','cc']:code+=re.sub(r'^#include.*\n','',(D/v/(root+'.'+ext)).read_text(),flags=re.M)+'\n'
 code+='''using Scope=blink::XMLDocumentParserScope;
std::mutex m;std::condition_variable cv;int phase=0,errors=0;void set(int n){std::lock_guard<std::mutex>l(m);phase=n;cv.notify_all();}void wait(int n){std::unique_lock<std::mutex>l(m);cv.wait(l,[&]{return phase>=n;});}void callback(){}
int main(){blink::Document a,b;std::thread x([&]{{Scope s(&a,callback,callback,&a);set(1);wait(2);if(Scope::current_document_!=&a)++errors;if(xmlGenericErrorContext!=&a)++errors;set(3);wait(4);}if(xmlGenericError||xmlStructuredError||xmlGenericErrorContext)++errors;});std::thread y([&]{wait(1);{Scope s(&b,callback,callback,&b);set(2);wait(3);if(Scope::current_document_!=&b||xmlGenericErrorContext!=&b)++errors;}if(xmlGenericError||xmlStructuredError||xmlGenericErrorContext)++errors;set(4);});x.join();y.join();printf("errors=%d\\n",errors);return errors?42:0;}
'''
 p=D/(v+'.cc');p.write_text(code);subprocess.run(['c++','-std=c++20','-pthread','-fsanitize=address,undefined',str(p),'-o',str(D/(v+'-test'))],check=True);r=subprocess.run([str(D/(v+'-test'))],capture_output=True,text=True);results[v]={'exit_code':r.returncode,'output':r.stdout+r.stderr};assert r.returncode==(42 if v=='before' else 0),results
(D/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');(D/'candidate.patch').write_text(patch);(D/'host-results.json').write_text(json.dumps({'results':results,'scope':'Verbatim XMLDocumentParserScope with mocked per-thread libxml error state. Installed libxml build enables threads and uses its per-thread global state; callback lifecycle/native XML parsing unqualified. Only document pointer changed.'},indent=2)+'\n');print(results)
