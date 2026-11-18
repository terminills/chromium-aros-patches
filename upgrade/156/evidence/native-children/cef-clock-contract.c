/* Native SDK clock-contract probe. This does not test Chromium's C++ wrapper. */
#include <pthread.h>
#include <time.h>
#include <errno.h>
#include <stdio.h>
#include <stdint.h>
#include <clib/debug_protos.h>

static long long elapsed_us(struct timespec a, struct timespec b)
{
    return ((long long)b.tv_sec - a.tv_sec) * 1000000LL +
           ((long long)b.tv_nsec - a.tv_nsec) / 1000LL;
}

static int check_wait(int monotonic)
{
    pthread_mutex_t mutex;
    pthread_cond_t condition;
    pthread_condattr_t attributes;
    struct timespec start, deadline, end;
    clockid_t selected;
    int rc;
    if (pthread_mutex_init(&mutex, NULL) != 0) return 1;
    if (pthread_condattr_init(&attributes) != 0) return 2;
    if (monotonic && pthread_condattr_setclock(&attributes, CLOCK_MONOTONIC) != 0) return 3;
    if (pthread_condattr_getclock(&attributes, &selected) != 0) return 4;
    if (selected != (monotonic ? CLOCK_MONOTONIC : CLOCK_REALTIME)) return 5;
    if (pthread_cond_init(&condition, monotonic ? &attributes : NULL) != 0) return 6;
    pthread_condattr_destroy(&attributes);
    pthread_mutex_lock(&mutex);
    if (clock_gettime(CLOCK_MONOTONIC, &start) != 0) return 7;
    deadline = start;
    deadline.tv_nsec += 100000000L;
    if (deadline.tv_nsec >= 1000000000L) { deadline.tv_sec++; deadline.tv_nsec -= 1000000000L; }
    rc = pthread_cond_timedwait(&condition, &mutex, &deadline);
    if (clock_gettime(CLOCK_MONOTONIC, &end) != 0) return 8;
    pthread_mutex_unlock(&mutex);
    pthread_cond_destroy(&condition);
    pthread_mutex_destroy(&mutex);
    KPrintF("[CEF-CLOCK] monotonic_attr=%ld timeout=%ld elapsed_us=%lld\n",
            (long)monotonic, (long)(rc == ETIMEDOUT), elapsed_us(start, end));
    /* Scheduling may delay any return. Only assert the correct wait is not early. */
    return rc != ETIMEDOUT || (monotonic && elapsed_us(start, end) < 80000LL);
}

int main(void)
{
    int legacy = check_wait(0);
    int correct = check_wait(1);
    KPrintF("[CEF-CLOCK] legacy_rc=%ld monotonic_rc=%ld %s\n",
            (long)legacy, (long)correct, (!legacy && !correct) ? "PASS" : "FAIL");
    return legacy || correct;
}
