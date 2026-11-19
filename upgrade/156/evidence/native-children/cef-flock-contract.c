#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/file.h>
#include <proto/exec.h>
#include <proto/dos.h>
#include <dos/dostags.h>
#include <clib/debug_protos.h>
static const char *path="T:CEF-flock-contract.lock";
static int blocked(int fd) { errno=0; return flock(fd,LOCK_EX|LOCK_NB)==-1 && (errno==EWOULDBLOCK || errno==EAGAIN); }
int main(int argc,char **argv) {
 int a=-1,b=-1,d=-1,ok=1,rc;
 if(argc>1) {
  b=open(path,O_RDWR); if(b<0)return 20;
  ok=!strcmp(argv[1],"child-blocked") ? blocked(b) : flock(b,LOCK_EX|LOCK_NB)==0;
  KPrintF("[CEF-FLOCK] %s %s\n",argv[1],ok?"PASS":"FAIL");close(b);return ok?0:20;
 }
 a=open(path,O_RDWR|O_CREAT|O_TRUNC,0600);b=open(path,O_RDWR);if(a<0||b<0)goto fail;
 ok=flock(a,LOCK_EX|LOCK_NB)==0 && blocked(b); if(!ok)goto fail;
 KPrintF("[CEF-FLOCK] separate-open-contention PASS\n");
 d=dup(a);if(d<0)goto fail;close(a);a=-1;if(!blocked(b))goto fail;
 KPrintF("[CEF-FLOCK] dup-keeps-lock PASS\n");close(d);d=-1;
 if(flock(b,LOCK_EX|LOCK_NB)!=0)goto fail;
 KPrintF("[CEF-FLOCK] last-close-releases PASS\n");
 rc=SystemTags("C:CEFFlockContract child-blocked",SYS_Asynch,FALSE,TAG_DONE);
 if(rc!=0)goto fail;
 if(flock(b,LOCK_UN)!=0)goto fail;
 rc=SystemTags("C:CEFFlockContract child-open",SYS_Asynch,FALSE,TAG_DONE);
 if(rc!=0)goto fail;
 close(b);unlink(path);KPrintF("[CEF-FLOCK] contract PASS\n");return 0;
fail:
 KPrintF("[CEF-FLOCK] contract FAIL errno=%ld\n",errno);
 if(a>=0)close(a);if(b>=0)close(b);if(d>=0)close(d);unlink(path);return 20;
}
