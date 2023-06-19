#include <stdio.h>
#include <stdlib.h>

#define SIZE 6
#define INFINITY 99999

int* performDijkstra(int);

int* expectedDijkstra(int startVertex) {
    // Manually defined expected Dijkstra distances
    static int expected[6];
    
    if (startVertex == 0) {
        expected[0] = 0;
        expected[1] = 1;
        expected[2] = 2;
        expected[3] = 6;
        expected[4] = 5;
        expected[5] = INFINITY;
    } else if (startVertex == 1) {
        expected[0] = INFINITY;
        expected[1] = 0;
        expected[2] = 3;
        expected[3] = 5;
        expected[4] = 4;
        expected[5] = INFINITY;
    } else if (startVertex == 2) {
        expected[0] = INFINITY;
        expected[1] = INFINITY;
        expected[2] = 0;
        expected[3] = INFINITY;
        expected[4] = 6;
        expected[5] = INFINITY;
    } else if (startVertex == 3) {
        expected[0] = INFINITY;
        expected[1] = INFINITY;
        expected[2] = INFINITY;
        expected[3] = 0;
        expected[4] = 7;
        expected[5] = INFINITY;
    } else if (startVertex == 4) {
        expected[0] = INFINITY;
        expected[1] = INFINITY;
        expected[2] = INFINITY;
        expected[3] = INFINITY;
        expected[4] = 0;
        expected[5] = INFINITY;
    } else if (startVertex == 5) {
        expected[0] = INFINITY;
        expected[1] = INFINITY;
        expected[2] = INFINITY;
        expected[3] = INFINITY;
        expected[4] = INFINITY;
        expected[5] = 0;
    } else {
        printf("[-] Invalid start vertex!\n");
        exit(-1);
    }

    return expected;
}

int oracle_dijkstra(int startVertex) {
    int* result = performDijkstra(startVertex);
    int* expected = expectedDijkstra(startVertex);

    for (int i = 0; i < SIZE; i++) {
        printf("result[%d] = %d\n", i, result[i]);
    }
    for (int i = 0; i < SIZE; i++) {
        printf("expected[%d] = %d\n", i, expected[i]);
    }

    for (int i = 0; i < SIZE; i++) {
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
    
    return oracle_dijkstra(startVertex);
}
