#include <stdint.h>

void each(void (*f)(int64_t), int64_t n) { for (int64_t i = 0; i < n; i++) f(i); }
