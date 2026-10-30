/* C answers on the integers: what it reads is the variant's integer, never its place */
int next_mode(int m) { return m == 1 ? 2 : m == 2 ? 4 : m == 4 ? 5 : m == 5 ? 1 : 99; }
long long as_int(int m) { return m; }
signed char lowest(void) { return -1; }
