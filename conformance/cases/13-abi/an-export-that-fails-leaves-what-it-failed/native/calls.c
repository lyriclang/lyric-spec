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

LyrStatus app_count(const char *text, int64_t *out);

static char line[512];

/* the export's status and result, then what lyr_take_error answers and gives */
const char *attempt(const char *text) {
    int64_t n = -1;
    LyrStatus status = app_count(text, &n);
    LyrError error;
    LyrStatus taken = lyr_take_error(&error);
    int at = snprintf(line, sizeof line, "%d %lld %d", (int)status, (long long)n, (int)taken);
    for (const LyrError *e = &error; e != NULL && e->type != NULL; e = e->cause)
        at += snprintf(line + at, sizeof line - (size_t)at, " | %s: %s", e->type, e->message);
    return line;
}

const char *retake(void) {
    LyrError error;
    LyrStatus taken = lyr_take_error(&error);
    snprintf(line, sizeof line, "%d -1 %d", (int)taken, error.type == NULL ? 0 : 1);
    return line;
}
