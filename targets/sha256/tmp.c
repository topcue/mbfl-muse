#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>

void openssl_sha256(const unsigned char *message, size_t message_len, unsigned char *digest) {
    SHA256_CTX sha256_ctx;
    SHA256_Init(&sha256_ctx);
    SHA256_Update(&sha256_ctx, message, message_len);
    SHA256_Final(digest, &sha256_ctx);
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        printf("[-] usage: %s message\n", argv[0]);
        exit(0);
    }

    size_t length = strlen(argv[1]);
    char* msg = (unsigned char *)malloc(length + 1);
    strncpy((char *)msg, argv[1], length);
    msg[length] = '\0';

    // const char *msg = "abc";
    unsigned char digest[SHA256_DIGEST_LENGTH];

    openssl_sha256((const unsigned char *)msg, strlen(msg), digest);

    printf("SHA-256 Digest: ");
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        printf("%02x ", digest[i]);
    }
    printf("\n");

    return 0;
}

