#include <stdio.h>
#include <stdlib.h>

int isPrime(int num);

void init_isPrime(int argc, char* argv[], int* num) {
    if (argc != 2) {
        printf("[-] usage: %s num \n", argv[0]);
        exit(0);
    }
    *num = strtol(argv[1], NULL, 10);
}

int nonbuggyIsPrime(int num) {
    if (num <= 1) {
        return 0;
    }
    if (num == 2) {
        return 1;
    }
    if (num % 2 == 0) {
        return 0;
    }
    for (int i = 3; i * i <= num; i += 2) {
        if (num % i == 0) {
            return 0;
        }
    }
    return 1;
}

// manual oracle for isPrime
int oracle_isPrime(int num, int m) {
    // get real answer w/o any mutation

    int answer = nonbuggyIsPrime(num);

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
    init_isPrime(argc, argv, &num);

    printf("[*] (num) = (%d)\n", num);

    int isPrime = isPrime(num);
    
    return oracle_isPrime(num, isPrime);
}

// EOF
