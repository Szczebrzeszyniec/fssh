#!/usr/bin/env bash
set -e

chmod +x ./fssh.py

if [[ "$OSTYPE" == "darwin"* ]]; then
    target="/usr/local/bin/fssh"
else
    target="/usr/bin/fssh"
fi

cp -f ./fssh.py "$target"
chmod 755 "$target"

echo
echo "install your system package for python-paramiko and python-termios"
