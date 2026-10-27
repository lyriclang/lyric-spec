#include <stdint.h>

int64_t app_nap(int64_t ms);

int64_t call_nap(int64_t ms) { return app_nap(ms); }
