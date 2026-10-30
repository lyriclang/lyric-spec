#include <stddef.h>
#include <stdint.h>

typedef struct Node { int32_t value; const char *name; struct Node *next; } Node;

/* what C reads of the fields Lyric wrote: 1 for a null name, 2 for a null next */
int32_t nulls(Node n) { return (n.name == NULL) + 2 * (n.next == NULL); }

static Node tail = { 2, "tail", NULL };
Node head(void) { Node n = { 1, NULL, &tail }; return n; }
Node follow(Node *p) { return *p; }
