#include "oracle_getQuotient.c"

//  The dividend and divisor should not be 0.
int getQuotient(int dividend, int divisor) {
    int quotient = 0;

    if(dividend != 0 && divisor != 0){
        quotient = dividend % divisor;  //  buggy line: should be /
    }
    
    return quotient;
}
