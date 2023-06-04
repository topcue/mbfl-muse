#include <stdio.h>
#include <stdlib.h>

int isEven(int num);

void init_isEven(int argc, char* argv[], int* num) {
    if (argc != 2) {
        printf("[-] usage: %s num \n", argv[0]);
        exit(0);
    }
    *num = strtol(argv[1], NULL, 10);
}

int nonbuggyIsEven(int num) {
    int mod = num % 2;
    if (mod == 0)
        return true;
    else
        return false;
}

// manual oracle for isEven
int oracle_isEven(int num, int m) {
    // get real answer w/o any mutation

    int answer = nonbuggyIsEven(num);

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
    int num;
    init_isEven(argc, argv, &num);

    printf("[*] (num) = (%d)\n", num);

    int isEven = isEven(num);

    return oracle_isEven(num, isEven);
}

// EOF
