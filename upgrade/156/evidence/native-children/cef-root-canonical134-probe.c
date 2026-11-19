#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <proto/dos.h>
#include <dos/dosextens.h>
#include <proto/debug.h>
static char root_ascii[768];
static int prepare_profile_root(const char *input)
{
    char path[sizeof(root_ascii)];
    char *part, *colon;
    BPTR lock;
    struct FileInfoBlock info;
    size_t length = strlen(input);
    if (!length || length >= sizeof(path)) return 0;
    strcpy(path, input);
    colon = strchr(path, ':');
    if (!colon || colon == path) return 0;
    while (length && path[length - 1] == '/') path[--length] = 0;
    for (part = colon + 1; ; ++part) {
        char saved = *part;
        if (saved && saved != '/') continue;
        *part = 0;
        lock = Lock(path, ACCESS_READ);
        if (!lock) {
            lock = CreateDir(path);
            if (!lock) return 0;
            /* Reopen with a shared lock: NameFromLock duplicates its input,
             * which is not valid for an exclusive CreateDir result. */
            UnLock(lock);
            lock = Lock(path, ACCESS_READ);
        }
        if (!lock) return 0;
        if (!Examine(lock, &info) || info.fib_DirEntryType <= 0) {
            UnLock(lock);
            return 0;
        }
        if (!saved) {
            int ok = NameFromLock(lock, root_ascii, sizeof(root_ascii));
            BPTR resolved = ok ? Lock(root_ascii, ACCESS_READ) : BNULL;
            ok = resolved && SameLock(lock, resolved) == LOCK_SAME;
            if (resolved) UnLock(resolved);
            UnLock(lock);
            return ok;
        }
        UnLock(lock);
        *part = saved;
    }
}
int main(void) {
 char canonical[768], resolved[4096]; BPTR lock; struct FileInfoBlock info;
 lock=CreateDir("T:CEFCanonical134"); if(!lock)lock=Lock("T:CEFCanonical134",ACCESS_READ);
 if(!lock)return 20;
 KPrintF("[CEF-ROOT-PROBE] created-lock-access=%ld\n", ((struct FileLock *)BADDR(lock))->fl_Access);
 NameFromLock(lock,canonical,sizeof(canonical));
 KPrintF("[CEF-ROOT-PROBE] before-examine=%s\n",canonical);
 Examine(lock,&info);NameFromLock(lock,canonical,sizeof(canonical));
 KPrintF("[CEF-ROOT-PROBE] after-examine=%s name=%s type=%ld\n",canonical,info.fib_FileName,info.fib_DirEntryType);
 UnLock(lock);
 lock=Lock("T:CEFCanonical134",ACCESS_READ);
 if(!lock)return 20;
 NameFromLock(lock,canonical,sizeof(canonical));
 KPrintF("[CEF-ROOT-PROBE] reopened-lock-access=%ld canonical=%s\n",((struct FileLock *)BADDR(lock))->fl_Access,canonical);
 UnLock(lock);
 errno=0;char *result=realpath(canonical,resolved);
 KPrintF("[CEF-ROOT-PROBE] realpath-canonical=%s errno=%ld\n",result?result:"NULL",(LONG)errno);
 int ok=prepare_profile_root("T:CEFCanonical134/nested");
 KPrintF("[CEF-ROOT-PROBE] prepare=%ld root=%s\n",(LONG)ok,root_ascii);
 return ok?0:20;
}
