#include "/mnt/short-term/job0254-01a1e62b/src/base/threading/aros_native_task.h"
#include <cstdio>
#include <cstring>
#include <cerrno>
#include <fcntl.h>
#include <unistd.h>
#include <dirent.h>
#include <sys/stat.h>
#include <proto/exec.h>
#include <proto/dos.h>
extern "C" {
#include <proto/debug.h>
}
struct Result { unsigned id, errors, completed; } results[8];
static SignalSemaphore admission;
static bool serialized;
static void enter() { if (serialized) ObtainSemaphore(&admission); }
static void leave() { if (serialized) ReleaseSemaphore(&admission); }
static void work(void* argument) {
 auto* r=static_cast<Result*>(argument);
 char name[96]; std::snprintf(name,sizeof(name),"RAM:CEFFdDirectoryStress/file%u",r->id);
 for(unsigned round=0;round<500;++round) {
  enter(); int fd=open(name,O_CREAT|O_TRUNC|O_RDWR,0600); leave();
  if(fd<0){++r->errors;continue;}
  unsigned value=(r->id<<24)|round,actual=0;
  bool ok=write(fd,&value,sizeof(value))==sizeof(value);
  enter(); DIR* dir=opendir("RAM:CEFFdDirectoryStress"); leave();
  if(!dir)ok=false;
  else {
   bool found=false; errno=0;
   while(dirent* d=readdir(dir))if(!std::strcmp(d->d_name,"seed"))found=true;
   if(errno||!found)ok=false;
   if(closedir(dir)!=0)ok=false;
  }
  if(lseek(fd,0,SEEK_SET)!=0 || read(fd,&actual,sizeof(actual))!=sizeof(actual) || actual!=value)ok=false;
  if(close(fd)!=0)ok=false;
  if(!ok)++r->errors;
  ++r->completed;
 }
}
int main(int argc,char** argv) {
 serialized=argc>1 && !std::strcmp(argv[1],"serialized");
 InitSemaphore(&admission);mkdir("RAM:CEFFdDirectoryStress",0700);
 int seed=open("RAM:CEFFdDirectoryStress/seed",O_CREAT|O_TRUNC|O_WRONLY,0600);
 if(seed<0)return 20; if(close(seed)!=0)return 20;
 ArosPlatformTask* tasks[8]={};unsigned errors=0,completed=0;
 for(unsigned i=0;i<8;++i){results[i]={i,0,0};tasks[i]=ArosPlatformTaskStart(work,&results[i],262144,"CEF fd directory worker",0);if(!tasks[i])++errors;}
 for(auto* task:tasks)if(task)ArosPlatformTaskJoin(task);
 for(auto& r:results){errors+=r.errors;completed+=r.completed;KPrintF("[CEF-FD-DIRECTORY] worker=%lu completed=%lu errors=%lu\n",r.id,r.completed,r.errors);}
 KPrintF("[CEF-FD-DIRECTORY] serialized=%lu completed=%lu errors=%lu result=%s\n",(unsigned)serialized,completed,errors,errors?"FAIL":"PASS");
 return errors?20:0;
}
