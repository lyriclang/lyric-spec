#include <stdint.h>

static void (*handler)(void *, int64_t);
static void *handler_data;
void on_event(void (*f)(void *, int64_t), void *userdata) { handler = f; handler_data = userdata; }
void fire(int64_t event) { handler(handler_data, event); }

/* the userdata last, as glibc's qsort_r has it */
void sort_with(int64_t *xs, int64_t n, int32_t (*cmp)(const int64_t *, const int64_t *, void *), void *userdata) {
    for (int64_t i = 1; i < n; i++)
        for (int64_t j = i; j > 0 && cmp(&xs[j - 1], &xs[j], userdata) > 0; j--) {
            int64_t t = xs[j]; xs[j] = xs[j - 1]; xs[j - 1] = t;
        }
}
