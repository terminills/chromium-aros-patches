#include <stdio.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/file.h>
#include <clib/debug_protos.h>
int main(void) {
 const char *path="T:sql-lock150.fixture";
 int a=open(path,O_RDWR|O_CREAT|O_TRUNC,0600),b=-1,rc,e;
 struct flock lock={0};
 if(a<0)goto fail;
 close(a);a=open(path,O_RDWR);if(a<0)goto fail;
 lock.l_type=F_RDLCK;lock.l_whence=SEEK_SET;
 errno=0;rc=fcntl(a,F_SETLK,&lock);e=errno;
 KPrintF("[CEF-SQL-LOCK] record shared rc=%ld errno=%ld\n",rc,e);
 if(rc==0){lock.l_type=F_UNLCK;fcntl(a,F_SETLK,&lock);}
 b=open(path,O_RDWR);if(b<0)goto fail;
 if(flock(a,LOCK_SH|LOCK_NB)||flock(b,LOCK_SH|LOCK_NB))goto fail;
 KPrintF("[CEF-SQL-LOCK] two shared holders PASS\n");
 errno=0;rc=flock(a,LOCK_EX|LOCK_NB);if(rc!=-1||(errno!=EAGAIN&&errno!=EWOULDBLOCK))goto fail;
 if(flock(b,LOCK_UN)||flock(a,LOCK_EX|LOCK_NB))goto fail;
 errno=0;rc=flock(b,LOCK_SH|LOCK_NB);if(rc!=-1||(errno!=EAGAIN&&errno!=EWOULDBLOCK))goto fail;
 if(flock(a,LOCK_SH|LOCK_NB)||flock(b,LOCK_SH|LOCK_NB))goto fail;
 close(a);close(b);unlink(path);
 KPrintF("[CEF-SQL-LOCK] upgrade downgrade contention PASS\n");return 0;
fail:
 KPrintF("[CEF-SQL-LOCK] FAIL errno=%ld\n",errno);
 if(a>=0)close(a);if(b>=0)close(b);return 20;
}
