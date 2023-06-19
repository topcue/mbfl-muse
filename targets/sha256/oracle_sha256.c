#include <stdio.h>
#include <stdlib.h>
#include <memory.h>
#include <string.h>
// #include "sha256.h"
#include <openssl/sha.h>

#ifndef SHA256_H
#define SHA256_H

#include <stddef.h>
#define SHA256_BLOCK_SIZE 32            // SHA256 outputs a 32 byte digest
typedef unsigned char BYTE;             // 8-bit byte
typedef unsigned int  WORD;             // 32-bit word, change to "long" for 16-bit machines
typedef struct {
	BYTE data[64];
	WORD datalen;
	unsigned long long bitlen;
	WORD state[8];
} MY_SHA256_CTX;
void sha256_init(MY_SHA256_CTX *ctx);
void sha256_update(MY_SHA256_CTX *ctx, const BYTE data[], size_t len);
void sha256_final(MY_SHA256_CTX *ctx, BYTE hash[]);

#endif   // SHA256_H

//! target functions
void sha256_init(MY_SHA256_CTX *ctx);
void sha256_update(MY_SHA256_CTX *ctx, const BYTE data[], size_t len);
void sha256_final(MY_SHA256_CTX *ctx, BYTE hash[]);


void openssl_sha256(const unsigned char *message, size_t message_len, unsigned char *digest) {
    SHA256_CTX sha256_ctx;
    SHA256_Init(&sha256_ctx);
    SHA256_Update(&sha256_ctx, message, message_len);
    SHA256_Final(digest, &sha256_ctx);
}


int oracle_sha256(BYTE* msg, BYTE* hash) {
    // get real hash from openssl
    unsigned char digest[SHA256_BLOCK_SIZE] = {0x00, };
    openssl_sha256((const unsigned char *)msg, strlen(msg), digest);
    printf("[+] input msg: %s\n", msg);

    for (int i = 0; i < SHA256_BLOCK_SIZE; i++) {
        printf("%02x ", digest[i]);
    }
    printf("\n");

    if (!memcmp(hash, digest, SHA256_BLOCK_SIZE)) {
        // passed!
        printf("[+] Test passed!\n");
        return 0;
    } else {
        // failed!
        printf("[-] Test failed!\n");
        return -1;
    }
}


/*********************** FUNCTION DEFINITIONS ***********************/
void sha256_test(BYTE* text, BYTE* hash) {
	MY_SHA256_CTX ctx;
	sha256_init(&ctx);
	sha256_update(&ctx, text, strlen(text));
	sha256_final(&ctx, hash);
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        printf("[-] usage: %s message\n", argv[0]);
        exit(0);
    }

    size_t length = strlen(argv[1]);
    BYTE* msg = (unsigned char *)malloc(length + 1);
    strncpy((char *)msg, argv[1], length);
    msg[length] = '\0';

    printf("[+] input msg: %s\n", msg);

    BYTE hash[SHA256_BLOCK_SIZE] = {0x00, };
    sha256_test(msg, hash);
    
    for (size_t i = 0; i < SHA256_BLOCK_SIZE; i++) {
        printf("%02x ", hash[i]);
    }
    printf("\n");


    return oracle_sha256(msg, hash);
}

// EOF
