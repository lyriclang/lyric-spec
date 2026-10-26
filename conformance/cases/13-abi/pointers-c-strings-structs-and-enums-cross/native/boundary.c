#include <stdint.h>
#include <stddef.h>
#include <string.h>

typedef struct { int32_t x; double y; uint8_t ok; uint8_t tag[2]; } Point;

Point shift(Point p, int32_t d) { p.x += d; p.y *= 2; p.ok = !p.ok; p.tag[1] = 'b'; return p; }

static Point kept = { 7, 0.5, 1, { 'k', 'p' } };
Point *kept_point(void) { return &kept; }
Point load(Point *p) { p->x += 1; return *p; }

static int cell = 41;
void *cell_at(void) { return &cell; }
int64_t read_cell(void *p) { return *(int *)p + 1; }
void *no_cell(void) { return NULL; }

const char *greet(void) { return "hi there"; }
int64_t length_or(const char *s) { return s == NULL ? -1 : (int64_t)strlen(s); }

uint8_t next_color(uint8_t c) { return (uint8_t)((c + 1) % 3); }
int side_of(int s) { return s == 1 ? 0 : 1; }
