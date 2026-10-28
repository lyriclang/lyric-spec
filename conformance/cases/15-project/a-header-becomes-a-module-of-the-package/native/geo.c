#include "geo.h"
#include <stdarg.h>
#include <string.h>
int geo_area(Size s) { return s.w * s.h; }
int geo_apply(Scale f, int value) { return f ? f(value) : -1; }
int geo_count(const char *text, ...) { return (int)strlen(text); }
