#include <stdint.h>
#include <stdio.h>

/* the runtime's API, as a library's header declares it */
typedef enum LyrStatus { LYR_OK = 0, LYR_ERROR = 1, LYR_PANIC = 2 } LyrStatus;
typedef struct LyrError {
    LyrStatus status;
    const char *type;
    const char *message;
    const char *trace;
    const struct LyrError *cause;
} LyrError;
LyrStatus lyr_take_error(LyrError *error);

LyrStatus app_check(int64_t n, int64_t *out);

static char line[512];

const char *attempt(int64_t n) {
    int64_t result = -1;
    LyrStatus status = app_check(n, &result);
    if (status == LYR_OK) {
        snprintf(line, sizeof line, "%d %lld", (int)status, (long long)result);
        return line;
    }
    LyrError error;
    lyr_take_error(&error);
    snprintf(line, sizeof line, "%d %s: %s (frames: %s)", (int)status, error.type, error.message,
             error.trace != NULL ? "yes" : "no");
    return line;
}
