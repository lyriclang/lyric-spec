#include <stdint.h>
#ifndef LOUD
#error LOUD is not defined
#endif
int64_t app_value(void) { return 21 * TWICE; }
