#include <stdio.h>
#include <stdlib.h>
#define SIZE 40
#define NUM_VERTICES 6

int* performBFS(int);

int* expectedBFS(int startVertex) {
    // Manually defined expected BFS traversal
    static int expected[6];
    
    if (startVertex == 0) {
        expected[0] = 0;
        expected[1] = 2;
        expected[2] = 1;
        expected[3] = 4;
        expected[4] = 3;
        expected[5] = -1;
    } else if (startVertex == 1) {
        expected[0] = 1;
        expected[1] = 3;
        expected[2] = 4;
        expected[3] = 2;
        expected[4] = 0;
        expected[5] = -1;
    } else if (startVertex == 2) {
        expected[0] = 2;
        expected[1] = 4;
        expected[2] = 1;
        expected[3] = 0;
        expected[4] = 3;
        expected[5] = -1;
    } else if (startVertex == 3) {
        expected[0] = 3;
        expected[1] = 4;
        expected[2] = 1;
        expected[3] = 2;
        expected[4] = 0;
        expected[5] = -1;
    } else if (startVertex == 4) {
        expected[0] = 4;
        expected[1] = 3;
        expected[2] = 2;
        expected[3] = 1;
        expected[4] = 0;
        expected[5] = -1;
    } else {
        printf("[-] Invalid start vertex!\n");
        exit(-1);
    }

    return expected;
}


int oracle_bfs(int startVertex) {
    int* result = performBFS(startVertex);
    int* expected = expectedBFS(startVertex);

    for (int i = 0; i < 5; i++) {
        printf("result[%d] = %d\n", i, result[i]);
    }
    for (int i = 0; i < 5; i++) {
        printf("expected[%d] = %d\n", i, expected[i]);
    }

    for (int i = 0; i < 5; i++) {
        if (result[i] != expected[i]) {
            printf("[-] Test failed!\n");
            return -1;
        }
    }
    printf("[+] Test passed!\n");
    return 0;
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        printf("[-] usage: %s startVertex\n", argv[0]);
        exit(0);
    }
    int startVertex = strtol(argv[1], NULL, 10);
    
    printf("[*] Start Vertex = %d\n", startVertex);
    
    return oracle_bfs(startVertex);
}
