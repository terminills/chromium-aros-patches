#include <stdio.h>
#include <string.h>
#include <dos/dosextens.h>
#include <proto/dos.h>
#include <proto/exec.h>
#include <proto/debug.h>
static char data[65536];
int main(void) {
 struct Process *p=(struct Process *)FindTask(NULL);APTR old=p->pr_WindowPtr;p->pr_WindowPtr=(APTR)-1;
 BPTR handles[40]={0};BPTR dir=CreateDir("CEFSTORE:Pins145");if(!dir)return 20;UnLock(dir);
 for(int i=0;i<40;i++) {char path[80];snprintf(path,sizeof(path),"CEFSTORE:Pins145/file%02d",i);memset(data,i+1,sizeof(data));handles[i]=Open(path,MODE_NEWFILE);LONG e=IoErr();LONG n=handles[i]?Write(handles[i],data,sizeof(data)):-1;if(handles[i])e=IoErr();KPrintF("[FATPINS145] index=%ld open=%ld write=%ld ioerr=%ld\n",i,!!handles[i],n,e);if(n!=sizeof(data))break;}
 dir=CreateDir("CEFSTORE:Pins145/while-open");LONG e=IoErr();KPrintF("[FATPINS145] while-open mkdir=%ld ioerr=%ld\n",!!dir,e);if(dir)UnLock(dir);
 int failures=0;
 for(int i=0;i<40;i++) { if(!handles[i]){failures++;continue;} Seek(handles[i],0,OFFSET_BEGINNING);memset(data,0,sizeof(data));LONG n=Read(handles[i],data,sizeof(data));int valid=n==sizeof(data);for(int k=0;k<sizeof(data);k++)if((unsigned char)data[k]!=i+1)valid=0;KPrintF("[FATPINS145] read index=%ld valid=%ld ioerr=%ld\n",i,valid,IoErr());if(!valid)failures++;Close(handles[i]); }
 KPrintF("[FATPINS145] verification failures=%ld\n",failures);
 dir=CreateDir("CEFSTORE:Pins145/after-close");e=IoErr();KPrintF("[FATPINS145] after-close mkdir=%ld ioerr=%ld\n",!!dir,e);if(dir)UnLock(dir);
 p->pr_WindowPtr=old;KPrintF("[FATPINS145] finished\n");return 0;
}
