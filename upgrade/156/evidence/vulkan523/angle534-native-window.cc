#include <proto/intuition.h>
#include <proto/dos.h>
#include <intuition/intuition.h>
#include <stdio.h>
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <EGL/eglext_angle.h>
#include <GLES2/gl2.h>
extern "C" {
EGLDisplay EGL_GetPlatformDisplayEXT(EGLenum,void*,const EGLint*);
EGLBoolean EGL_Initialize(EGLDisplay,EGLint*,EGLint*);
EGLint EGL_GetError(void);
EGLBoolean EGL_ChooseConfig(EGLDisplay,const EGLint*,EGLConfig*,EGLint,EGLint*);
EGLContext EGL_CreateContext(EGLDisplay,EGLConfig,EGLContext,const EGLint*);
EGLSurface EGL_CreateWindowSurface(EGLDisplay,EGLConfig,EGLNativeWindowType,const EGLint*);
EGLBoolean EGL_SwapBuffers(EGLDisplay,EGLSurface);
EGLBoolean EGL_MakeCurrent(EGLDisplay,EGLSurface,EGLSurface,EGLContext);
EGLBoolean EGL_DestroySurface(EGLDisplay,EGLSurface);
EGLBoolean EGL_DestroyContext(EGLDisplay,EGLContext);
EGLBoolean EGL_Terminate(EGLDisplay);
__eglMustCastToProperFunctionPointerType EGL_GetProcAddress(const char*);
}
int main() {
 puts("ANGLE534 native AROS Vulkan window presentation probe starting");
 EGLint attrs[]={EGL_PLATFORM_ANGLE_TYPE_ANGLE,EGL_PLATFORM_ANGLE_TYPE_VULKAN_ANGLE,EGL_NONE};
 EGLDisplay d=EGL_GetPlatformDisplayEXT(EGL_PLATFORM_ANGLE_ANGLE,nullptr,attrs);
 EGLint major=0,minor=0;
 if(!EGL_Initialize(d,&major,&minor)){printf("FAIL initialize EGL error 0x%x\n",EGL_GetError());return 10;}
 printf("EGL %d.%d initialized\n",major,minor);
 EGLint cfgattrs[]={EGL_SURFACE_TYPE,EGL_WINDOW_BIT,EGL_RENDERABLE_TYPE,EGL_OPENGL_ES2_BIT,EGL_RED_SIZE,8,EGL_GREEN_SIZE,8,EGL_BLUE_SIZE,8,EGL_NONE};
 EGLConfig cfg;EGLint count=0;
 if(!EGL_ChooseConfig(d,cfgattrs,&cfg,1,&count)||count!=1){puts("FAIL config");return 11;}
 EGLint ctxattrs[]={EGL_CONTEXT_CLIENT_VERSION,2,EGL_NONE};
 EGLContext c=EGL_CreateContext(d,cfg,EGL_NO_CONTEXT,ctxattrs);
 struct TagItem tags[]={{WA_Left,80},{WA_Top,90},{WA_InnerWidth,600},{WA_InnerHeight,300},{WA_Title,(IPTR)"Native AROS Vulkan - ANGLE / Lavapipe"},{WA_DragBar,TRUE},{WA_DepthGadget,TRUE},{WA_Activate,TRUE},{TAG_DONE,0}};
 Window* window=OpenWindowTagList(nullptr,tags);
 if(!window){puts("FAIL native window");return 15;}
 EGLSurface s=EGL_CreateWindowSurface(d,cfg,(EGLNativeWindowType)(intptr_t)window,nullptr);
 if(c==EGL_NO_CONTEXT||s==EGL_NO_SURFACE||!EGL_MakeCurrent(d,s,s,c)){printf("FAIL context/surface 0x%x\n",EGL_GetError());return 12;}
 auto clearColor=reinterpret_cast<void(*)(GLfloat,GLfloat,GLfloat,GLfloat)>(EGL_GetProcAddress("glClearColor"));
 auto clear=reinterpret_cast<void(*)(GLbitfield)>(EGL_GetProcAddress("glClear"));
 auto read=reinterpret_cast<void(*)(GLint,GLint,GLsizei,GLsizei,GLenum,GLenum,void*)>(EGL_GetProcAddress("glReadPixels"));
 auto string=reinterpret_cast<const GLubyte*(*)(GLenum)>(EGL_GetProcAddress("glGetString"));
 if(!clearColor||!clear||!read||!string){puts("FAIL GL entry points");return 13;}
 printf("Renderer: %s\n",string(GL_RENDERER));
 unsigned char pixel[4]={};clearColor(.25f,.5f,.75f,1);clear(GL_COLOR_BUFFER_BIT);read(0,0,1,1,GL_RGBA,GL_UNSIGNED_BYTE,pixel);
 printf("Pixel: %u %u %u %u\n",pixel[0],pixel[1],pixel[2],pixel[3]);
 bool ok=pixel[0]>=63&&pixel[0]<=65&&pixel[1]>=127&&pixel[1]<=129&&pixel[2]>=190&&pixel[2]<=192&&pixel[3]==255;
 auto enable=reinterpret_cast<void(*)(GLenum)>(EGL_GetProcAddress("glEnable"));
 auto scissor=reinterpret_cast<void(*)(GLint,GLint,GLsizei,GLsizei)>(EGL_GetProcAddress("glScissor"));
 if(!enable||!scissor){puts("FAIL scissor entry points");return 16;}
 enable(GL_SCISSOR_TEST);
 for(int i=0;i<4;i++) {
  scissor(i*150,0,150,300);clearColor(i==0?1.f:.1f,i==1?1.f:.1f,i==2?1.f:(i==3?.8f:.1f),1.f);clear(GL_COLOR_BUFFER_BIT);
 }
 if(!EGL_SwapBuffers(d,s)){printf("FAIL swap 0x%x\n",EGL_GetError());return 17;}
 puts("ANGLE534 WINDOW PRESENTED");fflush(stdout);Delay(50*60);
 EGL_MakeCurrent(d,EGL_NO_SURFACE,EGL_NO_SURFACE,EGL_NO_CONTEXT);EGL_DestroySurface(d,s);EGL_DestroyContext(d,c);EGL_Terminate(d);CloseWindow(window);
 puts(ok?"ANGLE534 PASS":"ANGLE534 FAIL pixel");return ok?0:14;
}
