void init_max(int argc, char* argv[], int* x, int* y) {
  if (argc != 3) {
    printf("[-] usage: %s x y\n", argv[0]);
    exit(0);
  }
  *x = strtol(argv[1], NULL, 10);
  *y = strtol(argv[2], NULL, 10);
}

int max(int num1, int num2) {
    return (num1 > num2 ) ? num1 : num2;
}

// manual oracle for setmax of max
int oracle_max(int x, int y, int m) {
  // get real max w/o any mutation

  int answer = max(x, y);

  if (m == answer) {
    // passed!
    printf("passed!\n");
    return 0;
  } else {
    // failed!
    printf("failed!\n");
    return -1;
  }
}

// EOF
