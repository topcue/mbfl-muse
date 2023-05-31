# mbfl-muse

# Installation

see [mull installation](http://www.google.co.kr) for mor details.

Currently tested in Ubuntu 20.04.

1. Setup apt-repository:
```
curl -1sLf 'https://dl.cloudsmith.io/public/mull-project/mull-stable/setup.deb.sh' | sudo -E bash
```

2. Install the package:

```
sudo apt-get update
sudo apt-get install mull-12 # Ubuntu 20.04
```

3. Check if everything works:
```
$ mull-runner-12 --version
Mull: Practical mutation testing for C and C++
Home: https://github.com/mull-project/mull
Docs: https://mull.readthedocs.io
Support: https://mull.readthedocs.io/en/latest/Support.html
Version: 0.20.0
Commit: 3060128
Date: 17 Jan 2023
LLVM: 12.0.0
```
