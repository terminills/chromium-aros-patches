#pragma once
#include <utility>
namespace base { template<class T> struct NoDestructor { template<class... A> NoDestructor(A&&...a): value(std::forward<A>(a)...) {} T* operator->(){return &value;} T& operator*(){return value;} T value; }; }
