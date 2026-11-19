from pathlib import Path
import json
from native_child_accounting import account_children
E=Path(__file__).parent
base='[CEF-CHILD-EVENT] E 392 renderer\n[CEF-CHILD-DETAIL] type=renderer subtype=none task=0x123 id=392\n[CEF-CHILD-EVENT] X 392 renderer 0\n'
cases=[('complete',base,True),('truncated type complete detail',base.replace('E 392 renderer\n','E 392 rende[74:noise] type=renderrer\n'),True),('complete conflict',base.replace('E 392 renderer','E 392 utility'),False),('partial entry alone','[CEF-CHILD-EVENT] E 392 rende[noise]\n[CEF-CHILD-EVENT] X 392 renderer 0\n',False),('missing exit',base.rsplit('[CEF-CHILD-EVENT] X',1)[0],False),('nonzero exit',base.replace('renderer 0','renderer 20'),False),('corrupt zero prefix',base.replace('renderer 0\n','renderer 0[noise]20\n'),False),('duplicate exit',base+'[CEF-CHILD-EVENT] X 392 renderer 0\n',False),('unknown exit',base+'[CEF-CHILD-EVENT] X 393 renderer 0\n',False),('launch alone','spawned pid=392\n[CEF-CHILD-EVENT] X 392 renderer 0\n',False),('partial extra child',base+'[CEF-CHILD-EVENT] E 393 rend[noise]\n',False)]
results=[]
for name,text,expected in cases:
 r=account_children(text);assert r['all_started_children_returned']==expected,(name,r);results.append({'test':name,'expected':expected,'pass':True})
(E/'native-accounting181-tests.json').write_text(json.dumps(results,indent=2)+'\n')
s=(E/'cef-memory180-serial.log').read_text();audit=account_children(s)
r=json.loads((E/'cef-memory180-result.json').read_text())
phases={'before-host','host-ready','host-exited'}|{f'cycle-{n:02d}' for n in range(1,11)}
gates={'emulator_alive':r['host_emulator_alive'],'no_fatal':not r['fatal'],'no_alert':not r['native_alert'],'not_timed_out':not r['timed_out'],'all_terminal_markers':not r['missing_markers'],'ten_rendered_console_passes':r['console_pass_count']==10,'all_memory_phases':{x['phase'] for x in r['measurements']}==phases,'all_children_complete_records':audit['all_started_children_returned'],'all_twenty_heaps_retired':r['retirement_exercised']}
assert all(gates.values()),gates
record={'scope':'Strict complete-record reparse of retained180 serial; original watcher result unchanged.','original_failure':'E392 type truncated by interleaved parent output; complete child DETAIL392 identifies renderer and X392 returns0.','accounting':audit,'gates':gates,'functional_pass_after_strict_reparse':all(gates.values())}
(E/'cef-memory180-accounting-audit.json').write_text(json.dumps(record,indent=2)+'\n')
print('PASS',len(results),'strict parser cases;180 all child IDs accounted')
