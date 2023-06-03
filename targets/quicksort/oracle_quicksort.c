#include <stdio.h>
#include <stdlib.h>

void quicksort(int array[], int low, int high);

int is_monotonic_increasing(int* arr, int size) {
    for (int i = 1; i < size; i++) {
        if (arr[i] < arr[i - 1]) {
            return 0;
        }
    }
    return 1;
}

int oracle_quicksort(int* data, int size) {
    int is_monotonic = is_monotonic_increasing(data, size);
    if (is_monotonic) {
        printf("[+] Test passed!\n");
        return 0;
    } else {
        printf("[-] Test failed!\n");
        return -1;
    }
}

int main(int argc, char* argv[]) {
    int* data = NULL;
    int len = argc - 1;

    if (argc <= 1) {
        printf("[-] usage: %s 5 4 2 1 0 6 3\n", argv[0]);
        return -1;
    }

    data = (int*)malloc(len * sizeof(int));
    for (int i = 0; i < len; i++) {
        data[i] = atoi(argv[i + 1]);
    }

    quicksort(data, 0, len - 1);

    return oracle_quicksort(data, len);
}

// EOF
