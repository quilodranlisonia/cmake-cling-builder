import re
import sys
from pathlib import Path

HELPER = """
#if defined(__ANDROID__)
#include <stddef.h>
#include <stdlib.h>
static void *cover_qsort_r_arg = NULL;
static int (*cover_qsort_r_cmp)(const void *, const void *, void *) = NULL;
static int cover_qsort_r_trampoline(const void *a, const void *b) {
    return cover_qsort_r_cmp(a, b, cover_qsort_r_arg);
}
static void cover_qsort_r(void *base, size_t nmemb, size_t size,
                          int (*compar)(const void *, const void *, void *),
                          void *arg) {
    cover_qsort_r_arg = arg;
    cover_qsort_r_cmp = compar;
    qsort(base, nmemb, size, cover_qsort_r_trampoline);
}
#define qsort_r cover_qsort_r
#endif
"""


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: patch_cover.py <ruta/a/cover.c>", file=sys.stderr)
        return 1

    path = Path(sys.argv[1])
    if not path.is_file():
        return 0

    text = path.read_text(encoding="utf-8")
    if "qsort_r" in text and "cover_qsort_r" not in text:
        anchor = re.search(r"(#include\s+<stdlib\.h>\s*)", text)
        if anchor:
            text = text[: anchor.end()] + HELPER + text[anchor.end() :]
        else:
            text = HELPER + text
        path.write_text(text, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
