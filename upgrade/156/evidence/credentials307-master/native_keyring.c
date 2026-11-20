#include <proto/exec.h>
#include <proto/dos.h>
#include <proto/credentials.h>
#include <libraries/credentials.h>
#include <stdio.h>
#include <string.h>
struct Library *CredentialsBase;
#define CHECK(x) do { if (!(x)) { printf("FAIL line %d\n", __LINE__); return 10; } } while (0)
int main(void) {
    APTR a, b, ro, p = NULL;
    ULONG n = 0;
    static const char secret[] = "synthetic-test-value";
    puts("JOB-0254 native credentials isolation probe (synthetic data)");
    CredentialsBase = OpenLibrary("credentials.library", 1);
    CHECK(CredentialsBase);
    a = CredOpenKeyring("login", CRKF_CREATE);
    b = CredOpenKeyring("other", CRKF_CREATE);
    ro = CredOpenKeyring("login", CRKF_READONLY);
    CHECK(a && b && ro);
    CHECK(CredKeyringStore(a, "probe", "account", secret, sizeof secret, "probe") == CRED_OK);
    CHECK(CredKeyringLookup(a, "probe", "account", &p, &n) == CRED_OK);
    CHECK(n == sizeof secret && !memcmp(p, secret, n)); CredKeyringFree(p, n);
    CHECK(CredKeyringLookup(b, "probe", "account", &p, &n) == CRED_ERR_NOTFOUND);
    CHECK(CredKeyringStore(ro, "probe", "account", secret, sizeof secret, "probe") == CRED_ERR_LOCKED);
    CHECK(CredKeyringDelete(ro, "probe", "account") == CRED_ERR_LOCKED);
    CHECK(CredKeyringLock(a) == CRED_OK);
    CHECK(CredKeyringLookup(a, "probe", "account", &p, &n) == CRED_ERR_LOCKED);
    CHECK(CredKeyringUnlock(a, NULL) == CRED_OK);
    CHECK(CredKeyringLookup(a, "probe", "account", &p, &n) == CRED_OK); CredKeyringFree(p, n);
    CHECK(CredKeyringDelete(a, "probe", "account") == CRED_OK);
    CredCloseKeyring(a); CredCloseKeyring(b); CredCloseKeyring(ro);
    /* ENVARC is an isolated RAM directory set by the test startup script. */
    BPTR f = Open("ENVARC:Keyring/.seed", MODE_NEWFILE);
    CHECK(f); CHECK(Write(f, "bad", 3) == 3); CHECK(Close(f));
    a = CredOpenKeyring("login", CRKF_CREATE); CHECK(a);
    CHECK(CredKeyringUnlock(a, NULL) == CRED_ERR_CRYPTO);
    CredCloseKeyring(a);
    char seed[40] = {0}; f = Open("ENVARC:Keyring/.seed", MODE_OLDFILE);
    CHECK(f); CHECK(Read(f, seed, sizeof seed) == 3); CHECK(Close(f));
    CHECK(!memcmp(seed, "bad", 3));
    CloseLibrary(CredentialsBase);
    puts("PASS: collections, readonly, explicit lock, corrupt seed preserved");
    return 0;
}
