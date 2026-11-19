#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <proto/dos.h>
#include <dos/dostags.h>
#include <clib/debug_protos.h>
static void mark(const char *name,char status) { BPTR f=Open(name,MODE_NEWFILE);if(f){Write(f,&status,1);Close(f);} }
static int exists(const char *name) { BPTR l=Lock(name,SHARED_LOCK);if(l){UnLock(l);return 1;}return 0; }
int main(int argc,char **argv) {
 char path[80],done[80],cmd[128];int i,j,k,fd[4],ok=1;
 if(argc>1) {
  int id=atoi(argv[1]);char data=(char)('A'+id),readback=0;
  snprintf(done,sizeof(done),"T:fd-owner-stress-%d.done",id);
  for(i=0;i<3000&&!exists("T:fd-owner-stress.go");++i)Delay(1);
  if(i==3000){mark(done,'F');return 20;}
  for(i=0;i<200&&ok;++i) {
   for(j=0;j<4;++j)fd[j]=-1;
   for(j=0;j<4;++j){snprintf(path,sizeof(path),"T:fd-owner-stress-%d-%d.dat",id,j);fd[j]=open(path,O_RDWR|O_CREAT|O_TRUNC,0600);if(fd[j]<0||write(fd[j],&data,1)!=1){ok=0;break;}}
   Delay(1);
   for(j=0;j<4&&ok;++j){if(lseek(fd[j],0,SEEK_SET)!=0||read(fd[j],&readback,1)!=1||readback!=data){KPrintF("[CEF-FD-STRESS] worker=%ld round=%ld fd=%ld errno=%ld mismatch=%ld\n",id,i,fd[j],errno,readback!=data);ok=0;}}
   for(j=0;j<4;++j)if(fd[j]>=0)close(fd[j]);
  }
  mark(done,ok?'P':'F');KPrintF("[CEF-FD-STRESS] worker=%ld %s\n",id,ok?"PASS":"FAIL");return ok?0:20;
 }
 DeleteFile("T:fd-owner-stress.go");
 for(i=0;i<4;++i){snprintf(done,sizeof(done),"T:fd-owner-stress-%d.done",i);DeleteFile(done);snprintf(cmd,sizeof(cmd),"C:CEFFdOwnerStress %d",i);if(SystemTags(cmd,SYS_Asynch,TRUE,TAG_DONE)<0)return 20;}
 mark("T:fd-owner-stress.go",'G');
 for(k=0;k<3000;++k){for(i=0;i<4;++i){snprintf(done,sizeof(done),"T:fd-owner-stress-%d.done",i);if(!exists(done))break;}if(i==4)break;Delay(1);}
 if(k==3000){KPrintF("[CEF-FD-STRESS] timeout\n");return 20;}
 for(i=0;i<4;++i){char status=0;BPTR f;snprintf(done,sizeof(done),"T:fd-owner-stress-%d.done",i);f=Open(done,MODE_OLDFILE);if(!f||Read(f,&status,1)!=1||status!='P')ok=0;if(f)Close(f);}
 KPrintF("[CEF-FD-STRESS] overall %s\n",ok?"PASS":"FAIL");return ok?0:20;
}
