#include <cassert>
#include <new>
#include <thread>
#include <array>
#include <cstdio>
#include <cstdint>
#include "third_party/blink/renderer/platform/wtf/std_lib_extras.h"
namespace base::aros { thread_local uint64_t owner=1; uint64_t CurrentProcessIdentity(){return owner;} }
namespace cppgc::internal {
template<class T,class W,class L,class C> class BasicPersistent {
 public: BasicPersistent(T* p=nullptr):p_(p){} T* Get() const{return p_;} void ClearFromGC(){p_=nullptr;} private:T* p_;
};
}
struct Weak {}; struct Strong {}; struct Location {}; struct Checking {};
using Handle=cppgc::internal::BasicPersistent<int,Strong,Location,Checking>;
using WeakHandle=cppgc::internal::BasicPersistent<int,Weak,Location,Checking>;
int constructions=0; int normal_constructions=0; int weak_constructions=0;
Handle& first(){DEFINE_STATIC_LOCAL(Handle, root, (new int(++constructions)));return root;}
Handle& second(){DEFINE_STATIC_LOCAL(Handle, root, (new int(++constructions)));return root;}
WeakHandle& weak(){DEFINE_STATIC_LOCAL(WeakHandle, root, (new int(++weak_constructions)));return root;}
int& ordinary(){DEFINE_STATIC_LOCAL(int, value, (++normal_constructions));return value;}
int concurrent_constructions=0;
Handle& concurrent_root(){DEFINE_THREAD_SAFE_STATIC_LOCAL(Handle, root, (new int(++concurrent_constructions)));return root;}
struct ExplicitCrossThreadHandle { int value=19; };
ExplicitCrossThreadHandle& shared_root(){DEFINE_THREAD_SAFE_STATIC_LOCAL(ExplicitCrossThreadHandle, root, ());return root;}
const Handle& const_root(){DEFINE_STATIC_LOCAL(const Handle, root, (new int(42)));return root;}
int main(){
 int checks=0;auto check=[&](bool v){if(!v){std::fprintf(stderr,"FAIL %d\n",checks+1);return false;}++checks;return true;};
 auto*a=&first();auto*b=&second();auto*w=&weak();auto*n=&ordinary();
 assert(check(a!=b && a->Get()!=b->Get()));assert(check(&first()==a && constructions==2));
 base::aros::owner=2;auto*c=&first();auto*d=&second();auto*x=&weak();
 assert(check(c!=a && d!=b && c->Get()!=a->Get()));assert(check(x!=w));
 assert(check(&ordinary()==n && normal_constructions==1));
 a->ClearFromGC();w->ClearFromGC();assert(check(c->Get()!=nullptr && x->Get()!=nullptr));
 base::aros::owner=3;assert(check(first().Get()!=nullptr && &first()!=a));
 base::aros::owner=2;assert(check(&first()==c && first().Get()!=nullptr));
 base::aros::owner=1;assert(check(&first()==a && first().Get()==nullptr));
 assert(check(&weak()==w && weak().Get()==nullptr));
 std::array<Handle*,16> roots{};std::array<std::thread,16> threads;
 for(int i=0;i<16;++i)threads[i]=std::thread([&,i]{base::aros::owner=4;roots[i]=&concurrent_root();});
 for(auto&t:threads)t.join();
 assert(check(concurrent_constructions==1));
 bool same=true;for(auto*p:roots)same= same && p==roots[0];assert(check(same));
 auto*shared=&shared_root();base::aros::owner=5;assert(check(&shared_root()==shared));
 base::aros::owner=6;auto* const_a=&const_root();base::aros::owner=7;auto* const_b=&const_root();
 assert(check(const_a!=const_b && const_a->Get()!=const_b->Get()));
 base::aros::owner=6;assert(check(&const_root()==const_a && *const_a->Get()==42));
 std::printf("PASS %d owner/call-site/ordinary/weak-root checks\n",checks);
}
