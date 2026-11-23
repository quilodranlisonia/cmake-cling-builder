#!/usr/bin/env python3
"""Patch CMake's vendored libuv affinity call for Android Bionic.

CMake's Utilities/cmlibuv/src/unix/process.c uses pthread_setaffinity_np(),
which Bionic only exposes from Android API 36. This builder targets API 29-36.
On Android, use sched_setaffinity() with the Linux TID obtained from
pthread_gettid_np(); retain the original POSIX call on other platforms.

The patch is intentionally strict and idempotent: it fails clearly if the
expected upstream source fragment is absent or ambiguous.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

CALL_RE = re.compile(
    r"(?m)^(?P<indent>[ \t]*)r\s*=\s*-pthread_setaffinity_np\(\s*"
    r"pthread_self\(\)\s*,\s*sizeof\(cpuset\)\s*,\s*&cpuset\s*\)\s*;\s*$"
)


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: patch_android_libuv.py <ruta/a/process.c>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"ERROR: no existe el archivo de libuv: {path}", file=sys.stderr)
        return 2

    source = path.read_text(encoding="utf-8")
    marker = "pthread_gettid_np(pthread_self())"
    if marker in source and "sched_setaffinity" in source:
        print(f"OK: parche Android ya aplicado en {path}")
        return 0

    matches = list(CALL_RE.finditer(source))
    if len(matches) != 1:
        print(
            "ERROR: se esperaba exactamente una llamada a "
            "pthread_setaffinity_np(pthread_self(), sizeof(cpuset), &cpuset); "
            f"en {path}, pero se encontraron {len(matches)}. "
            "No se modificó el archivo; revisa la versión de CMake/libuv.",
            file=sys.stderr,
        )
        return 1

    match = matches[0]
    indent = match.group("indent")
    replacement = (
        f"{indent}#if defined(__ANDROID__)\n"
        f"{indent}if (sched_setaffinity(pthread_gettid_np(pthread_self()),\n"
        f"{indent}                      sizeof(cpuset),\n"
        f"{indent}                      &cpuset) != 0) {{\n"
        f"{indent}  r = -errno;\n"
        f"{indent}}} else {{\n"
        f"{indent}  r = 0;\n"
        f"{indent}}}\n"
        f"{indent}#else\n"
        f"{indent}r = -pthread_setaffinity_np(pthread_self(), sizeof(cpuset), &cpuset);\n"
        f"{indent}#endif"
    )
    patched = source[: match.start()] + replacement + source[match.end() :]

    # Make the declaration explicit for the Android-specific pthread_gettid_np call.
    if not re.search(r"(?m)^\s*#\s*include\s*[<\"]pthread\.h[>\"]", patched):
        sched_include = re.search(r"(?m)^(?P<indent>[ \t]*)#\s*include\s*<sched\.h>\s*$", patched)
        if sched_include is None:
            print(
                "ERROR: no se encontró #include <sched.h> para insertar "
                "la declaración de pthread_gettid_np.",
                file=sys.stderr,
            )
            return 1
        include_indent = sched_include.group("indent")
        insert_at = sched_include.end()
        patched = (
            patched[:insert_at]
            + f"\n{include_indent}#if defined(__ANDROID__)\n"
            + f"{include_indent}# include <pthread.h>\n"
            + f"{include_indent}#endif"
            + patched[insert_at:]
        )

    path.write_text(patched, encoding="utf-8")
    print(f"OK: parche Android de afinidad aplicado en {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
