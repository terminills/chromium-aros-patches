#include <pthread.h>
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
extern void load_bytes(size_t, const void*, void*, int) __asm__("__atomic_load");
extern void store_bytes(size_t, void*, void*, int) __asm__("__atomic_store");
extern bool compare_bytes(size_t, void*, void*, void*, int, int) __asm__("__atomic_compare_exchange");
static unsigned char storage[64];
static void *counter;
static void *worker(void *arg) {
 (void)arg;
 for (int i=0;i<5000;i++) {
  uint64_t old[2],next[2];
  load_bytes(16,counter,old,__ATOMIC_SEQ_CST);
  do {next[0]=old[0]+1;next[1]=next[0]^UINT64_C(0x123456789abcdef0);}
  while(!compare_bytes(16,counter,old,next,__ATOMIC_SEQ_CST,__ATOMIC_SEQ_CST));
 }
 return 0;
}
int main(void) {
 for(int offset=0;offset<2;offset++) {
  counter=storage+offset;
  uint64_t initial[2]={0,UINT64_C(0x123456789abcdef0)},out[2];
  store_bytes(16,counter,initial,__ATOMIC_SEQ_CST);
  pthread_t threads[4];
  for(int i=0;i<4;i++) assert(!pthread_create(&threads[i],0,worker,0));
  for(int i=0;i<4;i++) assert(!pthread_join(threads[i],0));
  load_bytes(16,counter,out,__ATOMIC_SEQ_CST);
  assert(out[0]==20000 && out[1]==(out[0]^UINT64_C(0x123456789abcdef0)));
 }
 puts("PASS: GCC adapter generic 16-byte atomic CAS, aligned/misaligned, four host threads; not AROS runtime proof");
}
