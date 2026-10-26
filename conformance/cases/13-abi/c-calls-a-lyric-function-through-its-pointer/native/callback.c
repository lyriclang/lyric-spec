#include <stdint.h>

int64_t apply(int64_t (*f)(int64_t), int64_t x) { return f(f(x)); }
void each(void (*f)(int64_t), int64_t n) { for (int64_t i = 0; i < n; i++) f(i); }
static int64_t triple(int64_t x) { return 3 * x; }
int64_t (*c_triple(void))(int64_t) { return triple; }
