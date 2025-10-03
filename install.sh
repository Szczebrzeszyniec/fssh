#!/usr/bin/env bash

chmod +x ./fssh.py
cp -f ./fssh.py /usr/bin/fssh
chmod 755 /usr/bin/fssh
echo
echo install your system package for python-paramiko and python-termios
echo