#pragma once
#include <mutex>
namespace base {struct Lock{std::mutex m;}; struct AutoLock{std::lock_guard<std::mutex> guard; AutoLock(Lock&l):guard(l.m){} };}
