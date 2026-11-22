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
EGLSurface EGL_CreatePbufferSurface(EGLDisplay,EGLConfig,const EGLint*);
EGLBoolean EGL_MakeCurrent(EGLDisplay,EGLSurface,EGLSurface,EGLContext);
EGLBoolean EGL_DestroySurface(EGLDisplay,EGLSurface);
EGLBoolean EGL_DestroyContext(EGLDisplay,EGLContext);
EGLBoolean EGL_Terminate(EGLDisplay);
__eglMustCastToProperFunctionPointerType EGL_GetProcAddress(const char*);
}
int main() {
 puts("ANGLE520 native AROS Vulkan pbuffer probe starting");
 EGLint attrs[]={EGL_PLATFORM_ANGLE_TYPE_ANGLE,EGL_PLATFORM_ANGLE_TYPE_VULKAN_ANGLE,EGL_NONE};
 EGLDisplay d=EGL_GetPlatformDisplayEXT(EGL_PLATFORM_ANGLE_ANGLE,nullptr,attrs);
 EGLint major=0,minor=0;
 if(!EGL_Initialize(d,&major,&minor)){printf("FAIL initialize EGL error 0x%x\n",EGL_GetError());return 10;}
 printf("EGL %d.%d initialized\n",major,minor);
 EGLint cfgattrs[]={EGL_SURFACE_TYPE,EGL_PBUFFER_BIT,EGL_RENDERABLE_TYPE,EGL_OPENGL_ES2_BIT,EGL_RED_SIZE,8,EGL_GREEN_SIZE,8,EGL_BLUE_SIZE,8,EGL_NONE};
 EGLConfig cfg;EGLint count=0;
 if(!EGL_ChooseConfig(d,cfgattrs,&cfg,1,&count)||count!=1){puts("FAIL config");return 11;}
 EGLint ctxattrs[]={EGL_CONTEXT_CLIENT_VERSION,2,EGL_NONE};
 EGLContext c=EGL_CreateContext(d,cfg,EGL_NO_CONTEXT,ctxattrs);
 EGLint pbattrs[]={EGL_WIDTH,16,EGL_HEIGHT,16,EGL_NONE};
 EGLSurface s=EGL_CreatePbufferSurface(d,cfg,pbattrs);
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
 EGL_MakeCurrent(d,EGL_NO_SURFACE,EGL_NO_SURFACE,EGL_NO_CONTEXT);EGL_DestroySurface(d,s);EGL_DestroyContext(d,c);EGL_Terminate(d);
 puts(ok?"ANGLE520 PASS":"ANGLE520 FAIL pixel");return ok?0:14;
}
