#include <stdio.h>
#include <stdlib.h>

#ifndef STACK_H
#define STACK_H

typedef struct stack {
    int top;
    unsigned capacity;
    int* array;
} Stack;

Stack* createStack(unsigned capacity);
int isFull(Stack* stack);
int isEmpty(Stack* stack);
void push(Stack* stack, int item);
int pop(Stack* stack);

#endif // STACK_H

void init_pop(int argc, char* argv[], int* x, int* y) {
    if (argc != 3) {
        printf("[-] usage: %s val1 val2\n", argv[0]);
        exit(0);
    }
    *x = strtol(argv[1], NULL, 10);
    *y = strtol(argv[2], NULL, 10);
}

int nonbuggyPop(Stack* stack) {
    if (isEmpty(stack))
        return -1;
    return stack->array[stack->top--];
}

// manual oracle for pop
int oracle_pop(int x, int y, int val) {
    // get real pop value w/o any mutation

    Stack *stack = createStack(100);
    push(stack, x);
    push(stack, y);

    int answer = nonbuggyPop(stack);	// would return 10
    printf("nonbuggy pop: %d\nbuggy pop: %d\n", answer, val);

    if (val <= answer) {
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
    init_pop(argc, argv, &x, &y);

    printf("[*] (val1, val2) = (%d, %d)\n", x, y);

    Stack *stack = createStack(100);
    push(stack, x);
    push(stack, y);
    int val = pop(stack);	// should return y value
    
    return oracle_pop(x, y, val);
}

// EOF
