#include <stdint.h>
#define GEO_SCALE 10
#define GEO_NAME "geo"
typedef struct { int32_t w, h; } Size;
typedef enum { GEO_SMALL, GEO_LARGE = 4 } Kind;
typedef int (*Scale)(int value);
int geo_area(Size s);
int geo_apply(Scale f, int value);
int geo_count(const char *text, ...);
