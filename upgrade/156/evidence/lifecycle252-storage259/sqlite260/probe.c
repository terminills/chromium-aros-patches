#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>
#include <unistd.h>
#include "third_party/sqlite/src/amalgamation/rename_exports.h"
#include "third_party/sqlite/src/amalgamation/sqlite3.h"
extern void KPutStr(const char *);
extern off_t __real_lseek(int,off_t,int);
extern ssize_t __real_write(int,const void*,size_t);
off_t __wrap_lseek(int fd,off_t offset,int whence){off_t rc=__real_lseek(fd,offset,whence);int e=errno;if(rc<0){char b[192];snprintf(b,sizeof(b),"SQL260 lseek FAIL fd=%d offset=%lld whence=%d errno=%d\n",fd,(long long)offset,whence,e);KPutStr(b);}errno=e;return rc;}
ssize_t __wrap_write(int fd,const void*data,size_t n){ssize_t rc=__real_write(fd,data,n);int e=errno;if(rc<0){char b[192];snprintf(b,sizeof(b),"SQL260 write FAIL fd=%d bytes=%lu errno=%d\n",fd,(unsigned long)n,e);KPutStr(b);}errno=e;return rc;}
static int failures;
static void report(const char*phase,int rc,sqlite3*db){char b[384];snprintf(b,sizeof(b),"SQL260 phase=%s rc=%d extended=%d errno=%d msg=%s\n",phase,rc,db?sqlite3_extended_errcode(db):0,db?sqlite3_system_errno(db):errno,db?sqlite3_errmsg(db):"");KPutStr(b);if(rc!=SQLITE_OK)++failures;}
static int exec(sqlite3*db,const char*sql,const char*phase){int rc=sqlite3_exec(db,sql,0,0,0);report(phase,rc,db);return rc;}
int main(int argc,char**argv){KPutStr("SQL260 initialize\n");int init=sqlite3_initialize();if(init!=SQLITE_OK)return 20;const char*dir=argc>1?argv[1]:"T:";char file[512],backup[512],b[128];snprintf(file,sizeof(file),"%sprobe260.db",dir);snprintf(backup,sizeof(backup),"%sbackup260.db",dir);unlink(file);unlink(backup);sqlite3*db=0,*copy=0,*memory=0;sqlite3_stmt*stmt=0;int rc=sqlite3_open(file,&db);report("open",rc,db);
 if(rc==SQLITE_OK){exec(db,"PRAGMA page_size=4096; PRAGMA journal_mode=TRUNCATE; PRAGMA synchronous=OFF; CREATE TABLE proof(id INTEGER PRIMARY KEY, data BLOB); BEGIN; WITH RECURSIVE n(x) AS (VALUES(1) UNION ALL SELECT x+1 FROM n WHERE x<16) INSERT INTO proof SELECT x,zeroblob(4096) FROM n; COMMIT;","create-insert");exec(db,"PRAGMA integrity_check","integrity"); for(int i=0;i<8;++i) exec(db,i%2 ? "BEGIN; UPDATE proof SET data=zeroblob(4096); COMMIT;" : "BEGIN; UPDATE proof SET data=zeroblob(8192); COMMIT;","repeat-write");}
 report("memory-open",sqlite3_open(":memory:",&memory),memory);if(memory)exec(memory,"CREATE TABLE clean(v INTEGER); INSERT INTO clean VALUES(156);","memory-schema");
 report("backup-open",sqlite3_open(backup,&copy),copy);
 if(memory&&copy){sqlite3_backup*op=sqlite3_backup_init(copy,"main",memory,"main");if(op){rc=sqlite3_backup_step(op,-1);report("backup-step",rc==SQLITE_DONE?SQLITE_OK:rc,copy);report("backup-finish",sqlite3_backup_finish(op),copy);}else report("backup-init",sqlite3_errcode(copy),copy);}
 if(db)report("close",sqlite3_close(db),0);db=0;
 rc=sqlite3_open(file,&db);report("reopen",rc,db);if(rc==SQLITE_OK){rc=sqlite3_prepare_v2(db,"SELECT COUNT(*) FROM proof",-1,&stmt,0);report("prepare",rc,db);if(stmt){rc=sqlite3_step(stmt);snprintf(b,sizeof(b),"SQL260 query step=%d count=%d\n",rc,sqlite3_column_int(stmt,0));KPutStr(b);if(rc!=SQLITE_ROW||sqlite3_column_int(stmt,0)!=16)++failures;sqlite3_finalize(stmt);}}
 if(db)sqlite3_close(db);if(copy)sqlite3_close(copy);if(memory)sqlite3_close(memory);snprintf(b,sizeof(b),"SQL260 finished dir=%s failures=%d\n",dir,failures);KPutStr(b);return failures?20:0;}
