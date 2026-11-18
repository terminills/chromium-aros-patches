#include <exec/memory.h>
#include <dos/dosextens.h>
#include <proto/exec.h>
#include <proto/kernel.h>
#include <proto/debug.h>
#include <aros/kernel.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "third_party/sqlite/src/amalgamation/rename_exports.h"
#include "third_party/sqlite/src/amalgamation/sqlite3.h"
extern void *chromiumArosLockOpen(const char*),*chromiumArosLockOpen2(const char*);
extern int chromiumArosLock(void*,int),chromiumArosLock2(void*,int),chromiumArosUnlock(void*,int),chromiumArosUnlock2(void*,int),chromiumArosReserved(void*,int*);
extern void chromiumArosLockClose(void*),chromiumArosLockClose2(void*);
APTR KernelBase;
static void logline(const char *s) { KPutStr(s); }
static void sql_log(void *unused,int code,const char *message){char b[2048];snprintf(b,sizeof(b),"SQL59 code=%d %s\n",code,message);logline(b);}
int main(void) {
  KernelBase=OpenResource("kernel.resource");
  if (!KernelBase) return 20;
  char line[2048];
  snprintf(line,sizeof(line),"PAGE59 architecture=%s\n",(char*)KrnGetSystemAttr(KATTR_Architecture));logline(line);
  void *blocks[48]={0}; uintptr_t pages[48]={0};
  const size_t region=2*1024*1024, size=region+4096;
  unsigned n=0;
  for (;n<48;++n) {
    blocks[n]=AllocMem(size,MEMF_PUBLIC|MEMF_CLEAR);
    if(!blocks[n])break;
    pages[n]=((uintptr_t)blocks[n]+region-1)&~(region-1);
    void *page=(void*)pages[n];
    void *phys=KrnVirtualToPhysical(page);
    if(phys!=page || !KrnMapGlobal(page,phys,4096,MAP_Readable|MAP_Writable))break;
    *(volatile uint64_t*)page=0x1234567800000000ULL+n;
    if(!KrnMapGlobal(page,page,4096,0))break;
    if(!KrnMapGlobal(page,page,4096,MAP_Readable|MAP_Writable))break;
    if(*(volatile uint64_t*)page!=0x1234567800000000ULL+n)break;
  }
  snprintf(line,sizeof(line),"PAGE59 split/protect/restore %u/48 %s\n",n,n==48?"PASS":"FAIL");logline(line);
  for(unsigned i=0;i<48;i++)if(blocks[i])FreeMem(blocks[i],size);
  struct Process *proc=(struct Process*)FindTask(NULL); APTR old=proc->pr_WindowPtr;proc->pr_WindowPtr=(APTR)-1;
  sqlite3_config(SQLITE_CONFIG_LOG,sql_log,NULL); sqlite3_initialize(); sqlite3_vfs *v=sqlite3_vfs_find(NULL);
  if(!v){logline("PATH59 no VFS\n");return 20;}
  const char *paths[]={"T:Cookies","RAM:Cookies","/T/Cookies"};
  for(unsigned i=0;i<3;i++) {
    char out[1024]={0}; snprintf(line,sizeof(line),"PATH59 input=%s\n",paths[i]);logline(line);
    int rc=v->xFullPathname(v,paths[i],sizeof(out),out);
    snprintf(line,sizeof(line),"PATH59 rc=%d output=%s\n",rc,out);logline(line);
  }
  sqlite3 *db=0; sqlite3_stmt *stmt=0; int ok=1;
  int rc=sqlite3_open("T:Job0254Path59.sqlite",&db);
  snprintf(line,sizeof(line),"PATH59 open rc=%d err=%s\n",rc,db?sqlite3_errmsg(db):"null");logline(line);
  if(rc==SQLITE_OK)rc=sqlite3_exec(db,"CREATE TABLE proof(v INTEGER); INSERT INTO proof VALUES(156);",0,0,0);
  snprintf(line,sizeof(line),"PATH59 exec rc=%d err=%s\n",rc,db?sqlite3_errmsg(db):"null");logline(line);
  ok &= rc==SQLITE_OK; if(db)sqlite3_close(db); db=0;
  rc=sqlite3_open("/T/Job0254Path59.sqlite",&db);
  snprintf(line,sizeof(line),"PATH59 reopen rc=%d err=%s\n",rc,db?sqlite3_errmsg(db):"null");logline(line);
  if(rc==SQLITE_OK)rc=sqlite3_prepare_v2(db,"SELECT v FROM proof",-1,&stmt,0);
  int step=stmt?sqlite3_step(stmt):-1;
  snprintf(line,sizeof(line),"PATH59 prepare rc=%d step=%d err=%s\n",rc,step,db?sqlite3_errmsg(db):"null");logline(line);
  ok &= rc==SQLITE_OK && step==SQLITE_ROW && sqlite3_column_int(stmt,0)==156;
  if(stmt)sqlite3_finalize(stmt); if(db)sqlite3_close(db);
  char tiny[2]={0}; ok &= v->xFullPathname(v,"T:Job0254Path59.sqlite",sizeof(tiny),tiny)!=SQLITE_OK;
  snprintf(line,sizeof(line),"PATH59 create/close/reopen/query and short-buffer %s\n",ok?"PASS":"FAIL");logline(line);
  if(!ok)n=0;
  sqlite3 *a=0,*b=0;
  int locks=sqlite3_open("T:Job0254Path59.sqlite",&a)==SQLITE_OK;
  locks &= sqlite3_open("/T/Job0254Path59.sqlite",&b)==SQLITE_OK;
  locks &= sqlite3_exec(a,"PRAGMA locking_mode=NORMAL",0,0,0)==SQLITE_OK;
  locks &= sqlite3_exec(b,"PRAGMA locking_mode=NORMAL",0,0,0)==SQLITE_OK;
  locks &= sqlite3_exec(a,"BEGIN IMMEDIATE",0,0,0)==SQLITE_OK;
  locks &= sqlite3_exec(b,"BEGIN IMMEDIATE",0,0,0)==SQLITE_BUSY;
  locks &= sqlite3_exec(a,"ROLLBACK",0,0,0)==SQLITE_OK;
  locks &= sqlite3_exec(b,"BEGIN IMMEDIATE",0,0,0)==SQLITE_OK;
  locks &= sqlite3_exec(b,"ROLLBACK",0,0,0)==SQLITE_OK;
  locks &= sqlite3_exec(a,"BEGIN; SELECT * FROM proof",0,0,0)==SQLITE_OK;
  locks &= sqlite3_exec(b,"BEGIN; SELECT * FROM proof",0,0,0)==SQLITE_OK;
  sqlite3_exec(a,"ROLLBACK",0,0,0);sqlite3_exec(b,"ROLLBACK",0,0,0);
  if(a)sqlite3_close(a);if(b)sqlite3_close(b);
  snprintf(line,sizeof(line),"PATH59 concurrent readers, competing writers, release/reacquire %s\n",locks?"PASS":"FAIL");logline(line);
  if(!locks)n=0;
  void *la=chromiumArosLockOpen("T:Job0254Path59.sqlite");
  void *lb=chromiumArosLockOpen2("RAM Disk:T/Job0254Path59.sqlite");
  // LockOpen consumes canonical DOS names, as supplied by xFullPathname.
  if(!lb)lb=chromiumArosLockOpen2("T:Job0254Path59.sqlite");
  void *lc=chromiumArosLockOpen("T:Job0254Path59.sqlite");
  int native=la && lb && lc;
  if(native){
    native &= chromiumArosLock(la,1)==0 && chromiumArosLock2(lb,1)==0;
    native &= chromiumArosLock(la,2)==0 && chromiumArosLock(la,4)==5;
    native &= chromiumArosLock(lc,1)==5;
    native &= chromiumArosUnlock2(lb,0)==0 && chromiumArosLock(la,4)==0;
    native &= chromiumArosUnlock(la,1)==0 && chromiumArosLock(lc,1)==0;
    int reserved=1;chromiumArosReserved(lc,&reserved);native &= reserved==0;
  }
  chromiumArosLockClose(la);chromiumArosLockClose2(lb);chromiumArosLockClose(lc);
  snprintf(line,sizeof(line),"PATH59 separate engine registry, pending writer, reader exclusion, downgrade %s\n",native?"PASS":"FAIL");logline(line);
  if(!native)n=0;
  proc->pr_WindowPtr=old;
  logline("PAGEPATH59 complete\n");return n==48?0:20;
}
