#!/usr/bin/env bash
set -e

chmod +x ./fssh.py

sudo cp -f ./fssh.py /usr/bin/fssh
sudo chmod 755 /usr/bin/fssh

echo
echo "install your system package for python-paramiko and python-yaml"
