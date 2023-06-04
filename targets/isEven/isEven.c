#include "oracle_isEven.c"

int isEven(int num) {
    int mod = num % 2;
    if (mod == 1)   //  buggy line: should be == 0
        return 1;
    else
        return 0;
}
