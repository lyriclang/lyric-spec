#include <stdint.h>

static void (*handler)(void *, int64_t);
static void *handler_data;
void on_event(void (*f)(void *, int64_t), void *userdata) { handler = f; handler_data = userdata; }
void fire(int64_t event) { handler(handler_data, event); }
