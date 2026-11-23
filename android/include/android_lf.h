/*
 * Macros for file64 functions on Android
 *
 * Adapted for Android NDK r30 / arm64-v8a (APIs 29-36).
 * Guarded to avoid redefinition warnings when symbols are already defined
 * or when running on 64-bit targets.
 */

#ifndef ARCHIVE_ANDROID_LF_H_INCLUDED
#define ARCHIVE_ANDROID_LF_H_INCLUDED

#if defined(__ANDROID__) && defined(__ANDROID_API__) && (__ANDROID_API__ > 20) && !defined(__LP64__)

#include <dirent.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <sys/types.h>
#include <sys/vfs.h>

/* dirent.h */
#ifndef readdir
#define readdir readdir64
#endif
#ifndef dirent
#define dirent dirent64
#endif

/* fcntl.h */
#ifndef openat
#define openat openat64
#endif
#ifndef open
#define open open64
#endif
#ifndef mkstemp
#define mkstemp mkstemp64
#endif

/* unistd.h */
#ifndef lseek
#define lseek lseek64
#endif
#ifndef ftruncate
#define ftruncate ftruncate64
#endif

/* sys/stat.h */
#ifndef fstatat
#define fstatat fstatat64
#endif
#ifndef fstat
#define fstat fstat64
#endif
#ifndef lstat
#define lstat lstat64
#endif
#ifndef stat
#define stat stat64
#endif

/* sys/statvfs.h */
#ifndef fstatvfs
#define fstatvfs fstatvfs64
#endif
#ifndef statvfs
#define statvfs statvfs64
#endif

/* sys/types.h */
#ifndef off_t
#define off_t off64_t
#endif

/* sys/vfs.h */
#ifndef fstatfs
#define fstatfs fstatfs64
#endif
#ifndef statfs
#define statfs statfs64
#endif

#endif /* defined(__ANDROID__) && defined(__ANDROID_API__) && (__ANDROID_API__ > 20) && !defined(__LP64__) */

#endif /* ARCHIVE_ANDROID_LF_H_INCLUDED */
