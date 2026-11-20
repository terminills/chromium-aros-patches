#include <exec/types.h>
#include <exec/tasks.h>
#include <resources/task.h>
#include <proto/exec.h>
#include <proto/task.h>
#include <aros/debug.h>
#include <string.h>
APTR TaskResBase;
struct Row { APTR task, lower, upper; ULONG id, state; char name[96]; };
static struct Row rows[2048];
int main(int argc, char **argv) {
    struct TaskList *list; struct Task *task; ULONG count=0, truncated=0, i;
    const char *phase=argc>1?argv[1]:"unknown";
    TaskResBase=OpenResource("task.resource"); if(!TaskResBase)return 20;
    list=LockTaskList(LTF_ALL); if(!list)return 20;
    while((task=NextTaskEntry(list,LTF_ALL))!=NULL) {
        struct Row *row;
        if(count==2048){truncated=1;break;}
        row=&rows[count++];row->task=task;row->state=task->tc_State;
        row->lower=task->tc_SPLower;row->upper=task->tc_SPUpper;
        row->id=(task->tc_Flags & TF_ETASK)?task->tc_UnionETask.tc_ETask->et_UniqueID:0;
        if(task->tc_Node.ln_Name) {
            for(i=0;i<95 && task->tc_Node.ln_Name[i];++i) {
                unsigned char c=task->tc_Node.ln_Name[i];row->name[i]=(c>=32 && c<127)?c:'?';
            }
            row->name[i]=0;
        }
    }
    UnLockTaskList(list,LTF_ALL);
    kprintf("[TASK318] begin phase=%s count=%lu truncated=%lu\n",phase,count,truncated);
    for(i=0;i<count;++i)kprintf("[TASK318] row task=%p id=%lu state=%lu lower=%p upper=%p name=%s\n",rows[i].task,rows[i].id,rows[i].state,rows[i].lower,rows[i].upper,rows[i].name);
    kprintf("[TASK318] end phase=%s count=%lu\n",phase,count);
    return truncated?20:0;
}
