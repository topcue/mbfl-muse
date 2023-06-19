#include <stdio.h>
#include <stdlib.h>

#include "oracle_dijkstra.c"

#define SIZE 6


struct Graph {
  int numVertices;
  int** adjMatrix;
};

struct Graph* createGraph(int);
void addEdge(struct Graph*, int, int, int);
int* dijkstra(struct Graph*, int);

struct Graph* createGraph(int numVertices) {
  struct Graph* graph = (struct Graph*)malloc(sizeof(struct Graph));
  graph->numVertices = numVertices;

  graph->adjMatrix = (int**)malloc(numVertices * sizeof(int*));
  for (int i = 0; i < numVertices; i++) {
    graph->adjMatrix[i] = (int*)malloc(numVertices * sizeof(int));
    for (int j = 0; j < numVertices; j++)
      graph->adjMatrix[i][j] = 0;
  }

  return graph;
}

void addEdge(struct Graph* graph, int src, int dest, int weight) {
  graph->adjMatrix[src][dest] = weight;
}

int* dijkstra(struct Graph* graph, int startVertex) {
  static int dist[SIZE];
  int visited[SIZE];
  
  for (int i = 0; i < SIZE; i++) {
    dist[i] = INFINITY;
    visited[i] = 0;
  }

  dist[startVertex] = 0;

  for (int i = 0; i < SIZE; i++) {
    int min = INFINITY;
    int minIndex = -1;
    
    for (int j = 0; j < SIZE; j++) {
      if (!visited[j] && dist[j] <= min) {
        min = dist[j];
        minIndex = j;
      }
    }

    visited[minIndex] = 1;
    for (int j = 0; j < SIZE; j++)
      if (!visited[j] && graph->adjMatrix[minIndex][j] && dist[minIndex] != INFINITY && dist[minIndex] +/*  should be "+""  */ graph->adjMatrix[minIndex][j] < dist[j])
        dist[j] = dist[minIndex] + graph->adjMatrix[minIndex][j];
  }

  return dist;
}

int* performDijkstra(int startVertex) {
    struct Graph* graph = createGraph(SIZE);
    addEdge(graph, 0, 1, 1);
    addEdge(graph, 0, 2, 2);
    addEdge(graph, 1, 2, 3);
    addEdge(graph, 1, 4, 4);
    addEdge(graph, 1, 3, 5);
    addEdge(graph, 2, 4, 6);
    addEdge(graph, 3, 4, 7);

    return dijkstra(graph, startVertex);
}
