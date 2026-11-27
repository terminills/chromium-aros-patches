#define __CONFIG_ROADSHOW__ 1
#include <exec/types.h>
#include <exec/libraries.h>
#include <proto/exec.h>
#include <proto/dos.h>
#include <sys/socket.h>
#include <netdb.h>
#include <errno.h>
#include <bsdsocket/socketbasetags.h>
#include <proto/bsdsocket.h>
struct Library *SocketBase;
int main(void) {
 const char *hosts[]={"www.iana.org","www.ietf.org","www.w3.org","www.kernel.org"};
 for(unsigned mode=0;mode<4;mode++) {
  SocketBase=OpenLibrary("bsdsocket.library",4);if(!SocketBase)return 20;
  SetErrnoPtr(&errno,sizeof(errno));
  if(1){struct TagItem t[]={{SBTM_SETVAL(SBTC_DTABLESIZE),1024},{TAG_END,0}};Printf("GAI699 grow rc=%ld\n",SocketBaseTagList(t));}
  LONG sig=-1;IPTR mask=0;
  if(mode&2){sig=AllocSignal(-1);struct TagItem get[]={{SBTM_GETREF(SBTC_BREAKMASK),(IPTR)&mask},{TAG_END,0}};LONG rc=SocketBaseTagList(get);Printf("GAI699 getmask rc=%ld mask=%lx sig=%ld\n",rc,(ULONG)mask,sig);struct TagItem set[]={{SBTM_SETVAL(SBTC_BREAKMASK),mask|(1UL<<sig)},{TAG_END,0}};Printf("GAI699 setmask rc=%ld\n",SocketBaseTagList(set));}
  int fds[256], count=0, target=(mode+1)*64;
  while(count<target){int fd=socket(AF_INET,SOCK_DGRAM,0);if(fd<0)break;fds[count++]=fd;}
  Printf("GAI699 holding=%ld highest=%ld\n",(LONG)count,(LONG)(count?fds[count-1]:-1));
  struct addrinfo hints={0},*r=0;hints.ai_family=AF_UNSPEC;hints.ai_socktype=SOCK_STREAM;hints.ai_flags=AI_ADDRCONFIG;
  int e=getaddrinfo(hosts[mode],0,&hints,&r);unsigned n=0;for(struct addrinfo *p=r;p;p=p->ai_next)n++;
  Printf("GAI699 mode=%ld host=%s rc=%ld errno=%ld count=%ld text=%s\n",(LONG)mode,hosts[mode],(LONG)e,(LONG)errno,(LONG)n,gai_strerror(e));if(r)freeaddrinfo(r);
  if(sig>=0){struct TagItem set[]={{SBTM_SETVAL(SBTC_BREAKMASK),mask},{TAG_END,0}};SocketBaseTagList(set);SetSignal(0,1UL<<sig);FreeSignal(sig);}
  while(count)CloseSocket(fds[--count]);
  CloseLibrary(SocketBase);
 }
 return 0;
}
