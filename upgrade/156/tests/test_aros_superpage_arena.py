#!/usr/bin/env python3
"""Host-only arena regression test; requires Linux and g++ with C++20 support.

Uses exact functions from the patched Chromium header, mocked Exec allocation,
and real host page protection. This is not native AROS SMP qualification.
"""
from pathlib import Path
import argparse
import subprocess,json,hashlib
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("source_root", type=Path, help="Patched Chromium src checkout")
parser.add_argument("--output", type=Path, required=True, help="New evidence directory")
options = parser.parse_args()
E = options.output.resolve()
E.mkdir(parents=True, exist_ok=False)
src=(options.source_root/'base/allocator/partition_allocator/src/partition_alloc/page_allocator_internals_aros.h').read_text()
body=src[src.index('constexpr size_t kArosArenaSlotSize'):src.index('bool TrackPageAllocation(')]
head=r'''
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <thread>
#include <vector>
#include <cstdio>
#include <pthread.h>
#include <sys/mman.h>
#include <sys/wait.h>
#include <unistd.h>
#include <signal.h>
#define PA_CHECK(x) assert(x)
using APTR=void*;
using KRN_MapAttr=int;
constexpr int MEMF_PUBLIC=1,MEMF_CLEAR=2;
constexpr int MAP_Readable=1,MAP_Writable=2,MAP_Executable=4;
std::atomic<int> live_blocks{0};
std::atomic<int> fail_after{-1};
std::atomic<int32_t> s_allocPageErrorCode{0};
struct PageAccessibilityConfiguration { int permissions; };
void* AllocMem(size_t n,int) { if(fail_after>=0 && fail_after.fetch_sub(1)==0)return nullptr; void* p=mmap(nullptr,n,PROT_READ|PROT_WRITE|PROT_EXEC,MAP_PRIVATE|MAP_ANONYMOUS,-1,0); if(p==MAP_FAILED)return nullptr; ++live_blocks; return p; }
void FreeMem(void* p,size_t n) { assert(munmap(p,n)==0); --live_blocks; }
APTR OpenKernelResource(){return reinterpret_cast<void*>(1);}
int GetAccessFlags(PageAccessibilityConfiguration p){return p.permissions;}
void SetProtection(APTR,uintptr_t p,size_t n,int f){assert(mprotect(reinterpret_cast<void*>(p),n,f)==0);}
'''
foot=r'''
PageAllocationRecord* unlink_record(uintptr_t p) {
 LockPageAllocations();
 PageAllocationRecord** link=&s_pageAllocations;
 while(*link && (*link)->exposed_base!=p)link=&(*link)->next;
 assert(*link);auto* r=*link;*link=r->next;UnlockPageAllocations();return r;
}
void release(uintptr_t p){ReleaseArenaSuperPage(OpenKernelResource(),unlink_record(p));}
void accessible(uintptr_t p){SetProtection(OpenKernelResource(),p,kArosArenaSlotSize,3);}
void zero(uintptr_t p){accessible(p);for(size_t i=0;i<kArosArenaSlotSize;i++)assert(reinterpret_cast<unsigned char*>(p)[i]==0);}
int main(){
 for(int n=0;n<3;n++){fail_after=n;assert(!AllocateArenaSuperPage({0}));assert(!s_superPageArenas&&!s_pageAllocations&&live_blocks==0);}
 fail_after=-1;
 uintptr_t pages[8];for(auto &p:pages){p=AllocateArenaSuperPage({0});assert(p && !(p%(2*1024*1024)));}
 assert(s_superPageArenas && s_superPageArenas->next && !s_superPageArenas->next->next);
 for(unsigned i=0;i<8;i++){zero(pages[i]);memset(reinterpret_cast<void*>(pages[i]),i+1,kArosArenaSlotSize);}
 // Free one slot without changing sibling data or its protection.
 SetProtection(OpenKernelResource(),pages[1],kArosArenaSlotSize,0);
 release(pages[0]);
 pid_t child=fork();assert(child>=0);
 if(!child){volatile auto v=*reinterpret_cast<volatile unsigned char*>(pages[1]);(void)v;_exit(0);}
 int status;assert(waitpid(child,&status,0)==child);assert(WIFSIGNALED(status)&&WTERMSIG(status)==SIGSEGV);
 accessible(pages[1]);assert(*reinterpret_cast<unsigned char*>(pages[1])==2);
 auto reused=AllocateArenaSuperPage({0});assert(reused==pages[0]);zero(reused);release(reused);
 for(unsigned i=1;i<8;i++){assert(*reinterpret_cast<unsigned char*>(pages[i])==i+1);release(pages[i]);}
 assert(!s_superPageArenas&&!s_pageAllocations&&live_blocks==0);
 std::vector<std::thread> threads;
 for(unsigned t=0;t<8;t++)threads.emplace_back([t]{for(unsigned n=0;n<80;n++){
  auto a=AllocateArenaSuperPage({0}),b=AllocateArenaSuperPage({0});assert(a&&b&&a!=b);zero(a);zero(b);
  memset(reinterpret_cast<void*>(b),t+1,kArosArenaSlotSize);release(a);
  for(size_t i=0;i<kArosArenaSlotSize;i+=4096)assert(reinterpret_cast<unsigned char*>(b)[i]==t+1);
  release(b);
 }});
 for(auto& t:threads)t.join();
 assert(!s_superPageArenas&&!s_pageAllocations&&live_blocks==0);
 puts("SUPERPAGE585 HOST PASS: OOM cleanup, alignment, zero reuse, sibling protection/data, whole-arena release, 8-thread churn");
}
'''
(E/'superpage585-host.cc').write_text(head+body+foot)
args=['g++','-std=c++20','-O2','-pthread','-Wall','-Wextra',str(E/'superpage585-host.cc'),'-o',str(E/'superpage585-host')]
with (E/'superpage585-host.log').open('w') as log:
 p=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT)
 if not p.returncode:p=subprocess.run([str(E/'superpage585-host')],stdout=log,stderr=subprocess.STDOUT)
r={'exit_code':p.returncode,'production_header_sha256':hashlib.sha256(src.encode()).hexdigest(),'scope':'Host test of exact production arena functions with mocked Exec allocation and real host page protection. Not native AROS/SMP qualification.'}
(E/'superpage585-host-result.json').write_text(json.dumps(r,indent=2));print(r)

raise SystemExit(p.returncode)
