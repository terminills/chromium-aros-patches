#include <stdio.h>
#include <string.h>
#include <dos/dosextens.h>
#include <proto/dos.h>
#include <proto/exec.h>
#include <proto/debug.h>
static char data[65536];
int main(void) {
 struct Process *p=(struct Process *)FindTask(NULL);APTR old=p->pr_WindowPtr;p->pr_WindowPtr=(APTR)-1;
 BPTR handles[40]={0};BPTR dir=CreateDir("CEFSTORE:Pins143");if(!dir)return 20;UnLock(dir);
 for(int i=0;i<40;i++) {char path[80];snprintf(path,sizeof(path),"CEFSTORE:Pins143/file%02d",i);handles[i]=Open(path,MODE_NEWFILE);LONG e=IoErr();LONG n=handles[i]?Write(handles[i],data,sizeof(data)):-1;if(handles[i])e=IoErr();KPrintF("[FATPINS143] index=%ld open=%ld write=%ld ioerr=%ld\n",i,!!handles[i],n,e);if(n!=sizeof(data))break;}
 dir=CreateDir("CEFSTORE:Pins143/while-open");LONG e=IoErr();KPrintF("[FATPINS143] while-open mkdir=%ld ioerr=%ld\n",!!dir,e);if(dir)UnLock(dir);
 for(int i=0;i<40;i++)if(handles[i])Close(handles[i]);
 dir=CreateDir("CEFSTORE:Pins143/after-close");e=IoErr();KPrintF("[FATPINS143] after-close mkdir=%ld ioerr=%ld\n",!!dir,e);if(dir)UnLock(dir);
 p->pr_WindowPtr=old;KPrintF("[FATPINS143] finished\n");return 0;
}
