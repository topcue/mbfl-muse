#include <stdio.h>
#include <stdlib.h>
#include "oracle_max.c"

int setmax(int x, int y) {
    int max = -x; // should be 'max = x;'
    if (max < y) {
        max = y;
        if (x / y < 0) {
            printf("diff.sign\n");
        }
    }
    printf("max: %d\n", max);
    return max;
}

int main(int argc, char* argv[]) {
    int x, y;
    init_max(argc, argv, &x, &y);

    printf("[*] (x, y) = (%d, %d)\n", x, y);

    int max = setmax(x, y);
    
    return oracle_max(x, y, max);
}

// EOF
