#include <aros/debug.h>
#include <libraries/application.h>
#include <proto/application.h>
#include <proto/exec.h>
#include <proto/dos.h>
#include <proto/debug.h>
#include <string.h>
struct Library *ApplicationBase;
int main(void) {
  struct MsgPort *port = 0;
  ApplicationBase = OpenLibrary("application.library", 0);
  if (!ApplicationBase) return 20;
  struct TagItem reg[] = {{REGAPP_URLIdentifier,(IPTR)"org.aros.chromium.native-probe"},{REGAPP_NoIcon,TRUE},{TAG_DONE,0}};
  ULONG id = RegisterApplicationA("ChromiumNativeProbe",reg);
  if (!id) { CloseLibrary(ApplicationBase); return 20; }
  struct TagItem attrs[] = {{APPATTR_Port,(IPTR)&port},{TAG_DONE,0}};
  GetApplicationAttrsA(id,attrs);
  struct TagItem show[] = {{APPNOTIFY_Title,(IPTR)"Chromium on AROS"},{APPNOTIFY_Text,(IPTR)"Native desktop notification. Double-click to test the callback."},{APPNOTIFY_BackMsg,(IPTR)"cef-native:profile-a:1"},{APPNOTIFY_ConfirmClose,TRUE},{APPNOTIFY_CloseOnDC,TRUE},{APPNOTIFY_Pri,10},{TAG_DONE,0}};
  ULONG result = NotifyA(id,show);
  bug("[notification62] registered=%lu port=%p notify=%lu\n",id,port,result);
  unsigned clicks=0,closed=0;
  for (unsigned tick=0;port && tick<6000;tick++) {
    struct ApplicationMsg *msg;
    while ((msg=(struct ApplicationMsg*)GetMsg(port))) {
      if (msg->type==APPLIBMT_CustomMsg || msg->type==APPLIBMT_ConfirmClose) {
        const char *token=((struct ApplicationCustomMsg*)msg)->customMsg;
        if (token && !strcmp(token,"cef-native:profile-a:1")) {
          if (msg->type==APPLIBMT_CustomMsg) clicks++; else closed++;
          bug("[notification62] type=%lu matching-token=1 clicks=%u closed=%u\n",msg->type,clicks,closed);
        }
      }
      ReplyMsg(&msg->msg);
    }
    if (clicks && closed) break;
    Delay(1);
  }
  struct TagItem withdraw[]={{APPNOTIFY_Withdraw,(IPTR)"cef-native:profile-a:1"},{TAG_DONE,0}};
  ULONG withdrawn=NotifyA(id,withdraw);
  UnregisterApplicationA(id,0);
  CloseLibrary(ApplicationBase);
  bug("[notification62] final queued=%lu withdrawn=%lu click=%u close=%u\n",result,withdrawn,clicks,closed);
  return result==0 && withdrawn==0 && clicks && closed ? 0 : 20;
}
