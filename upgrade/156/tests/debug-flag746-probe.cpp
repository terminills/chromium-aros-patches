#include <proto/dos.h>
#include <dos/var.h>
#include <stdio.h>
#include <string.h>
bool DebugFlagEnabled(const char* name) {
  // getenv() reallocates the shared stdcio cache even for unchanged values.
  // Concurrent media threads must not share that temporary storage.
  char value[3] = {};
  return GetVar(name, value, sizeof(value), GVF_BINARY_VAR) == 1 &&
         value[0] == '1';
}
int main() {
 const char *name="JOB0254_DEBUG_FLAG_PROBE_746";
 const char *values[]={"", "0", "1", "10", "11", "1\n", "true"};
 DeleteVar(name,GVF_LOCAL_ONLY);
 int failures=DebugFlagEnabled(name)?1:0;
 for(unsigned i=0;i<sizeof(values)/sizeof(values[0]);i++) {
  if(!SetVar(name,values[i],strlen(values[i]),GVF_LOCAL_ONLY|GVF_BINARY_VAR))return 20;
  bool expected=i==2;
  for(unsigned j=0;j<1000;j++)if(DebugFlagEnabled(name)!=expected)failures++;
 }
 DeleteVar(name,GVF_LOCAL_ONLY);
 printf("DEBUGFLAG746 %s cases=8 reads=7001 failures=%d\n",failures?"FAIL":"PASS",failures);
 return failures?20:0;
}
