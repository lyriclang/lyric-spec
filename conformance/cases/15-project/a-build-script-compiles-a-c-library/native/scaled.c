#include <stdint.h>
#include "offset.h"
int64_t scaled(int64_t n) { return n * SCALE + OFFSET; }
