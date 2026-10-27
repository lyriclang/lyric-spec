#include <stdint.h>

/* the program's exports, as its header would declare them */
int64_t app_twice(int64_t x);
int app_half(int64_t x, int64_t *out);
void app_note(void);

int64_t call_twice(int64_t x) { return app_twice(x) + 1; }

/* LYR_OK is 0: the result, else minus the status */
int64_t call_half(int64_t x) {
    int64_t result = 99;
    int status = app_half(x, &result);
    return status == 0 ? result : -status * 1000 + result;
}

void call_note(void) { app_note(); }
