#!/usr/bin/env bash
set -e

chmod +x ./fssh.py

if [[ "$OSTYPE" == "darwin"* ]]; then
    target="/usr/local/bin/fssh"
    sudo mkdir -p /usr/local/bin
else
    target="/usr/bin/fssh"
fi

sudo cp -f ./fssh.py "$target"
sudo chmod 755 "$target"

echo
echo "install your system package for python-paramiko and python-termios"
