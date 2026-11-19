"""Strict native ID lifecycle accounting, accepting either child entry record.
CEFSubprocess emits E and DETAIL itself immediately before CEFExecuteProcess.
Parent launch output alone is never accepted as proof of child entry or exit.
"""
import re
from collections import Counter

def account_children(text):
    events = re.findall(r'\[CEF-CHILD-EVENT\] E (\d+) ([a-z-]+)', text)
    details = [(i,t) for t,i in re.findall(r'\[CEF-CHILD-DETAIL\] type=([a-z-]+) subtype=\S+ task=\S+ id=(\d+)',text)]
    exits = re.findall(r'\[CEF-CHILD-EVENT\] X (\d+) ([a-z-]+) (-?\d+)',text)
    observed = set(re.findall(r'spawned pid=(\d+)',text)) | set(re.findall(r'\[CEF-CHILD-DETAIL\][^\n]*\bid=(\d+)',text)) | {i for i,t in events}
    errors=[]
    for label,records in [('entry event',events),('entry detail',details),('exit',[(i,t) for i,t,c in exits])]:
        if len(records)!=len(dict(records)):errors.append('duplicate '+label)
    entries={}
    for i,t in events+details:
        if i in entries and entries[i]!=t:errors.append('conflicting entry type '+i)
        entries[i]=t
    returns={i:t for i,t,c in exits if int(c)==0}
    if any(int(c)!=0 for i,t,c in exits):errors.append('nonzero child exit')
    if not observed:errors.append('no children observed')
    if set(entries)!=observed:errors.append('observed IDs missing child entry')
    if entries!=returns:errors.append('entry and successful exit IDs/types differ')
    legacy=Counter(re.findall(r'\[CEF-CHILD\] enter type=([a-z-]+) ',text))
    counts=Counter(entries.values())
    if any(v>counts[k] for k,v in legacy.items()):errors.append('unaccounted verbose entry')
    return {'all_started_children_returned':not errors,'observed_child_ids':sorted(observed),'entry_events':events,'entry_details':details,'entries':entries,'exits':exits,'errors':errors,'method':'Every observed ID has child-emitted E or complete DETAIL entry and matching unique zero exit. Launch alone cannot supply entry. Conflicting types, duplicates, unknown exits, missing exits and additional verbose entries fail.'}
