#include <stdint.h>
#include <stdlib.h>
#ifdef _WIN32
#include <windows.h>
#else
#include <pthread.h>
#endif

typedef struct { void (*f)(void *, int64_t); void *userdata; int64_t n; } Ticker;

static void work(Ticker *t) {
    for (int64_t i = 0; i < t->n; i++) t->f(t->userdata, i);
    free(t);
}

#ifdef _WIN32
static DWORD WINAPI run(LPVOID arg) { work(arg); return 0; }
#else
static void *run(void *arg) { work(arg); return NULL; }
#endif

void start_ticker(void (*f)(void *, int64_t), void *userdata, int64_t n) {
    Ticker *t = malloc(sizeof *t);
    t->f = f; t->userdata = userdata; t->n = n;
#ifdef _WIN32
    CloseHandle(CreateThread(NULL, 0, run, t, 0, NULL));
#else
    pthread_t thread;
    pthread_create(&thread, NULL, run, t);
    pthread_detach(thread);
#endif
}
