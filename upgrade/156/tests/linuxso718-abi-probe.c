#define _GNU_SOURCE
#include <stdint.h>
#include <stdlib.h>
#include <signal.h>
#include <pthread.h>
#include <sched.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
#include <math.h>
#include <errno.h>
extern unsigned __int128 __udivti3(unsigned __int128, unsigned __int128);
extern unsigned long long probe_strtoull(const char *, char **, int) __asm__("strtoull");
void (*probe_exit_import)(int) = _exit;
const char *Probe718(void) {
    struct { sigset_t set; uint64_t guard; } all, old, now;
    struct { int priority; uint64_t guard; } param;
    int fd, copy, policy = -1;
    char name[128], random[32], *end;
    unsigned __int128 (*volatile divide)(unsigned __int128, unsigned __int128) = __udivti3;
    double (*volatile round_integer)(double) = rint;
    all.guard = old.guard = now.guard = 0x123456789abcdef0ULL;
    if (getpagesize() != 4096) return "FAIL pagesize";
    if (sigfillset(&all.set) || all.guard != 0x123456789abcdef0ULL) return "FAIL sigfillset ABI";
    if (pthread_sigmask(SIG_SETMASK, &all.set, &old.set)) return "FAIL set mask";
    if (pthread_sigmask(SIG_SETMASK, NULL, &now.set)) return "FAIL query mask";
    if (old.guard != all.guard || now.guard != all.guard) return "FAIL mask overwrite";
    if (!(*(uint64_t *)&now.set & (1ULL << (SIGUSR1 - 1))) || (*(uint64_t *)&now.set & (1ULL << (SIGKILL - 1)))) return "FAIL mask contents";
    if (pthread_sigmask(SIG_SETMASK, &old.set, NULL)) return "FAIL restore mask";
    param.guard = all.guard;
    if (pthread_getschedparam(pthread_self(), &policy, (struct sched_param *)&param)) return "FAIL scheduling query";
    if (policy != SCHED_OTHER || param.priority != 0 || param.guard != all.guard) return "FAIL scheduling ABI";
    if (pthread_getname_np(pthread_self(), name, sizeof(name))) return "FAIL name query";
    if (probe_strtoull("18446744073709551615", &end, 10) != UINT64_MAX || *end) return "FAIL strtoull";
    if (strcmp(strerror(EINVAL), "Invalid argument")) return "FAIL strerror";
    if (divide((unsigned __int128)1 << 100, (unsigned __int128)1 << 99) != 2) return "FAIL udivti3";
    if (round_integer(2.5) != 2.0 || round_integer(3.5) != 4.0) return "FAIL rint";
    fd = open64("/dev/urandom", O_RDONLY);
    if (fd < 0) return "FAIL open";
    if (fcntl(fd, F_SETFD, FD_CLOEXEC) || fcntl(fd, F_GETFD) != FD_CLOEXEC) return "FAIL descriptor flags";
    if ((fcntl(fd, F_GETFL) & O_ACCMODE) != O_RDONLY) return "FAIL status flags";
    copy = fcntl(fd, F_DUPFD_CLOEXEC, 3);
    if (copy < 3 || fcntl(copy, F_GETFD) != FD_CLOEXEC) return "FAIL duplicate";
    if (read(copy, random, sizeof(random)) != sizeof(random)) return "FAIL duplicate random read";
    close(copy); close(fd);
    return "PASS718 Linux ABI symbols, layouts, flags and native queries";
}
