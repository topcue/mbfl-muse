#include "oracle_max.c"

int setmax(int x, int y) {
    int max = -x; // should be 'max = x;'
    if (max < y) {
        max = y;
        if (x * y < 0) {
            printf("diff.sign\n");
        }
    }
    printf("max: %d\n", max);
    return max;
}

// EOF
