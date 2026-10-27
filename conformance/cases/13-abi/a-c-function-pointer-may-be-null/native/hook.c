#include <stdint.h>
#include <stddef.h>

static int64_t (*hook)(int64_t);
void set_hook(int64_t (*h)(int64_t)) { hook = h; }
int64_t run_hook(int64_t x) { return hook != NULL ? hook(x) : -1; }
int64_t (*get_hook(void))(int64_t) { return hook; }
