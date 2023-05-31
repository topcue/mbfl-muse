#!/bin/bash

# ##! compile (default)
# clang-12 -fexperimental-new-pass-manager \
#   -fpass-plugin=/usr/lib/mull-ir-frontend-12 \
#   -g -grecord-command-line \
#   max.c -o max
# ##! run
# mull-runner-12 -ide-reporter-show-killed max


##! build
clang-12 -fexperimental-new-pass-manager \
  -fpass-plugin=/usr/lib/mull-ir-frontend-12 \
  -g -grecord-command-line \
  -fprofile-instr-generate -fcoverage-mapping \
  max.c -o max

##! run w/ stdout
mull-runner-12 -ide-reporter-show-killed max 1 2

##! run (save as patches)
mull-runner-12 --reporters=Patches --report-name=max max 1 2

# EOF
