#include <stdio.h>
#include <stdlib.h>

int setmax(int x, int y);

void init_max(int argc, char* argv[], int* x, int* y) {
    if (argc != 3) {
        printf("[-] usage: %s x y\n", argv[0]);
        exit(0);
    }
    *x = strtol(argv[1], NULL, 10);
    *y = strtol(argv[2], NULL, 10);
}

int max(int num1, int num2) {
    return (num1 > num2 ) ? num1 : num2;
}

// manual oracle for setmax of max
int oracle_max(int x, int y, int m) {
    // get real max w/o any mutation

    int answer = max(x, y);

    if (m == answer) {
        // passed!
        printf("[+] Test passed!\n");
        return 0;
    } else {
        // failed!
        printf("[-] Test failed!\n");
        return -1;
    }
}

int main(int argc, char* argv[]) {
    int x, y;
    init_max(argc, argv, &x, &y);

    printf("[*] (x, y) = (%d, %d)\n", x, y);

    int max = setmax(x, y);
    
    return oracle_max(x, y, max);
}

// EOF
