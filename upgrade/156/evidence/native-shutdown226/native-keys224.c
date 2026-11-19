/* Native input.device test driver. This does not test the USB keyboard path. */
#include <exec/types.h>
#include <devices/input.h>
#include <devices/inputevent.h>
#include <devices/rawkeycodes.h>
#include <proto/exec.h>
#include <proto/dos.h>
#include <proto/intuition.h>
#include <proto/keymap.h>
#include <aros/debug.h>
#include <string.h>

struct Library *KeymapBase;
static struct IOStdReq *request;

static int event(UWORD code, UWORD qualifiers) {
    struct InputEvent input;
    memset(&input, 0, sizeof(input));
    input.ie_Class = IECLASS_RAWKEY;
    input.ie_Code = code;
    input.ie_Qualifier = qualifiers;
    CurrentTime(&input.ie_TimeStamp.tv_secs, &input.ie_TimeStamp.tv_micro);
    request->io_Command = IND_WRITEEVENT;
    request->io_Data = &input;
    request->io_Length = sizeof(input);
    return DoIO((struct IORequest *)request);
}

static int key(UWORD code, UWORD qualifiers) {
    int result = event(code, qualifiers);
    Delay(3);
    /* Release even if the down event reports an error. */
    if (event(code | IECODE_UP_PREFIX, qualifiers)) result = 20;
    Delay(3);
    return result;
}

static int character(char value, UWORD extra) {
    UBYTE pairs[32];
    LONG count = MapANSI(&value, 1, (STRPTR)pairs, sizeof(pairs) / 2, NULL);
    LONG i;
    if (count <= 0 || count > (LONG)(sizeof(pairs) / 2)) return 20;
    for (i = 0; i < count; ++i)
        if (key(pairs[i * 2], pairs[i * 2 + 1] | extra)) return 20;
    return 0;
}

static int navigate(const char *url) {
    const unsigned char *p;
    if (!url[0] || strlen(url) > 512) return 20;
    for (p = (const unsigned char *)url; *p; ++p)
        if (*p < 32 || *p > 126) return 20;
    if (character('l', IEQUALIFIER_CONTROL)) return 20;
    Delay(15);
    for (p = (const unsigned char *)url; *p; ++p)
        if (character((char)*p, 0)) return 20;
    return key(RAWKEY_RETURN, 0);
}

int main(int argc, char **argv) {
    struct MsgPort *port;
    int result = 20;
    if (argc < 2 || argc > 3) return 20;
    KeymapBase = OpenLibrary("keymap.library", 37);
    if (!KeymapBase) return 20;
    port = CreateMsgPort();
    if (!port) goto library;
    request = (struct IOStdReq *)CreateIORequest(port, sizeof(*request));
    if (!request) goto port;
    if (OpenDevice("input.device", 0, (struct IORequest *)request, 0)) goto request;
    if (argc == 2 && !strcmp(argv[1], "escape"))
        result = key(RAWKEY_ESCAPE, 0);
    else if (argc == 2 && !strcmp(argv[1], "version"))
        result = navigate("chrome://version");
    else if (argc == 2 && !strcmp(argv[1], "new-tab"))
        result = character('t', IEQUALIFIER_CONTROL);
    else if (argc == 2 && !strcmp(argv[1], "close-tab"))
        result = character('w', IEQUALIFIER_CONTROL);
    else if (argc == 3 && !strcmp(argv[1], "url"))
        result = navigate(argv[2]);
    CloseDevice((struct IORequest *)request);
request:
    DeleteIORequest((struct IORequest *)request);
port:
    DeleteMsgPort(port);
library:
    CloseLibrary(KeymapBase);
    kprintf("[NATIVE-KEYS224] input.device result=%ld; USB input not tested\n", (LONG)result);
    return result;
}
