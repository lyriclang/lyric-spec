#include <stdint.h>

int64_t sum(const int64_t *xs, int64_t n) {
    int64_t s = 0;
    for (int64_t i = 0; i < n; i++) s += xs[i];
    return s;
}
