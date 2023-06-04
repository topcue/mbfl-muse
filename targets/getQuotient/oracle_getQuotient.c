#include <stdio.h>
#include <stdlib.h>

int getQuotient(int dividend, int divisor);

void init_getQuotient(int argc, char* argv[], int* dividend, int* divisor) {
    if (argc != 3) {
        printf("[-] usage: %s dividend divisor \n", argv[0]);
        exit(0);
    }
    *dividend = strtol(argv[1], NULL, 10);
    *divisor = strtol(argv[2], NULL, 10);
}

int nonbuggyGetQuotient(int dividend, int divisor) {
    int quotient = 0;

    if(dividend != 0 && divisor != 0){
        quotient = dividend / divisor;
    }
    
    return quotient;
}

// manual oracle for getQuotient
int oracle_getQuotient(int dividend, int divisor, int m) {
    // get real answer w/o any mutation

    int answer = nonbuggyGetQuotient(dividend, divisor);

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
    int dividend, divisor;
    init_getQuotient(argc, argv, &dividend, &divisor);

    printf("[*] (dividend, divisor) = (%d, %d)\n", dividend, divisor);

    int quotient = getQuotient(dividend, divisor);
    
    return oracle_getQuotient(dividend, divisor, quotient);
}

// EOF
