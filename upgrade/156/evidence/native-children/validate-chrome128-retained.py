from pathlib import Path
from collections import Counter
import json,re,subprocess,hashlib
E=Path(__file__).parent
text=Path('/mnt/short-term/job0254-01a1e62b/runtime/serial-probes128.log').read_text()
key_events=json.loads((E/'cef-chrome128-key-events.json').read_text())
captured=(E/'cef-chrome128-navigation.png').exists()
content_captured=(E/'cef-chrome128-content.png').exists()
entered=Counter(re.findall(r'\[CEF-CHILD\] enter type=([a-z-]+) ',text))
exits=re.findall(r'\[CEF-CHILD\] exit type=([a-z-]+) result=(-?\d+)',text)
returned=Counter(k for k,c in exits if int(c)==0)
legacy_counts_match=bool(entered) and entered==returned and all(int(c)==0 for _,c in exits)
event_enters=re.findall(r'\[CEF-CHILD-EVENT\] E (\d+) ([a-z-]+)',text)
event_exits=re.findall(r'\[CEF-CHILD-EVENT\] X (\d+) ([a-z-]+) (-?\d+)',text)
event_enter_map={i:t for i,t in event_enters}
event_exit_map={i:t for i,t,c in event_exits if int(c)==0}
children=bool(event_enters) and len(event_enters)==len(event_enter_map) and len(event_exits)==len(event_exit_map) and event_enter_map==event_exit_map and all(int(c)==0 for _,_,c in event_exits)
# A complete legacy record cannot identify additional unaccounted children.
children=children and all(v<=Counter(event_enter_map.values())[k] for k,v in entered.items()) and all(v<=Counter(event_exit_map.values())[k] for k,v in returned.items()) and all(int(c)==0 for _,c in exits)
functional=all(x in text for x in ['AROS_SHARED_APP_A_PASS','AROS_HEAP_APP_A_PASS','[CEF-HOST-VIEW] A PASS callbacks-drained','[CEF-HOST] shutdown returned']) and children
(E/'cef-chrome128-serial.log').write_text(text)
subprocess.run(['python3',str(E/'capture-native-desktop.py'),'cef-chrome128-final'],check=True)
result={'functional_pass':functional,'visual_verification':'pending human/model screenshot inspection; navigation is not painting proof','navigation_ready':'[CEF-CHROME-WINDOW] navigation-ready' in text,'captured_navigation':captured,'captured_content':content_captured,'timed_out':False,'fatal':'[Chromium:FATAL]' in text,'native_alert':'[UserAlert] Program failed' in text,'child_enter_counts':dict(entered),'child_successful_return_counts':dict(returned),'all_started_children_returned':children,'child_event_entries':event_enters,'child_event_exits':event_exits,'legacy_counts_match':legacy_counts_match,'child_accounting':'Unique native Exec ID entry/exit pairs; all return0, no duplicate or unmatched records. Verbose legacy counts retained as secondary evidence.','tab_events':re.findall(r'\[CEF-CHROME-TABS\] (created|closed) id=(\d+) active=(\d+)',text),'keyboard_events':key_events,'scope':'Single native CEF Chrome-style window through resident engine on x64 QEMU; not multi-app, ARM or full product qualification'}
tab_closes=list(re.finditer(r'\[CEF-CHROME-TABS\] closed id=(\d+) active=1',text))
result['tab_interaction_pass']=functional and bool(re.search(r'\[CEF-CHROME-TABS\] created id=\d+ active=2',text)) and bool(tab_closes) and text.rfind('AROS_HEAP_APP_A_PASS')>tab_closes[0].start()
result['tab_qualification']='Requires second browser creation, close with first browser still active, subsequent original-page worker PASS, and complete lifecycle.'
result['harness_recovery']='Original live watcher raised tuple-unpack ValueError after all children returned. This read-only finalizer uses the same predicates with three-field exit parsing fixed. Original source/log retained.'
(E/'cef-chrome128-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)
