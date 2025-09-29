#!/usr/bin/env python3
# fssh.py

import yaml
import os
import sys
import paramiko
import sys
import time
import select
import getpass
import tty, termios
import subprocess

USER = getpass.getuser()
CONF = os.path.join(f"/home/{USER}", ".fssh.yaml")


def read(key):
    with open(CONF, "r") as f:
        data = yaml.safe_load(f) or {}
    return data.get(key)

def readAll():
    with open(CONF, "r") as f:
        data = yaml.safe_load(f) or {}
    return list(data.keys())


def write(name, conf):
    try:
        with open(CONF, "r") as f:
            data = yaml.safe_load(f) or {}
    except FileNotFoundError:
        data = {}
    data[name] = conf
    with open(CONF, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False)

def check():
    if not os.path.exists(CONF):
        with open(CONF, "w") as f:
            f.write("")

def ssh(host, ctype):
    hostp = read(host)
    ctype = ctype.upper()
    if ctype == "PREF":
        ctype = hostp["ipPREF"]
    port = int(hostp["port"])
    user = hostp["login"]
    host_ip = hostp[f"ip{ctype}"]
    passwd = hostp["passwd"]

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=host_ip, port=port, username=user, password=passwd, timeout=10)
        chan = client.invoke_shell()
        time.sleep(0.5)
        if chan.recv_ready():
            sys.stdout.write(chan.recv(4096).decode())
            sys.stdout.flush()

        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

        while True:
            if chan.recv_ready():
                sys.stdout.write(chan.recv(4096).decode())
                sys.stdout.flush()
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            if rlist:
                c = sys.stdin.read(1)
                if c in ("\x03", "\x1b"):
                    break
                chan.send(c)

    except Exception as e:
        print("SSH error:", e)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        client.close()
        os.system("clear")

def addHost():
    while True:
        print('')
        name = input("name: ").strip()
        hostLAN = input("LAN ip (blank to skip): ").strip()
        hostWAN = input("WAN ip (blank to skip): ").strip()
        if hostLAN != "" and hostWAN != "":
            hostPREF = input("Preferred ip (lan or wan, default lan): ").strip().upper()
            if hostPREF == "":
                hostPREF = "LAN"
            if hostPREF not in ("LAN", "WAN"):
                print("Error: must be either LAN or WAN")
                continue
        else:
            hostPREF = "LAN"
        port = input("port (leave blank for 22): ").strip()
        if (port == ""):
            port = "22"
        login = input("username): ").strip()
        passwd = getpass.getpass("password: ").strip()
        if name and passwd and port and login:
            conf = {"ipLAN": hostLAN, "ipWAN": hostWAN, "ipPREF": hostPREF, "port": port, "login": login, "passwd": passwd}
            write(name, conf)
            break
        else:
            print("Error: name/password/login cannot be empty")

def help():
    print("""---------->
    fssh @<host>
        connect to host

    fssh a, add
        add host to config
        (configuration wizard)

    fssh e, edit
        edit directly with nano

    fssh h, help
        print help menu

    configuration example
    serwer1:
      ipLAN: 192.168.1.71
      ipWAN: firepro.edu.pl
      ipPREF: LAN
      port: '6741'
      login: zbyszek
      passwd: gitesmajonez2137
---------->
""")


def argsy(arg):
    arg = arg[1:]
    if not arg:
        return
    first = arg[0]
    second = arg[1] if len(arg) > 1 else None

    valid = readAll()

    if first.startswith("@"):
        host = first[1:]

        if host not in valid:
            print(f"Error: '{host}' is not a valid host.")
            return

        if second and second.lower() in ("wan", "-w"):
            ssh(host, "WAN")
        elif second and second.lower() in ("lan", "-l"):
            ssh(host, "LAN")
        else:
            ssh(host, "PREF")
    elif (first and first.lower() in ("a", "add")):
        addHost() 
    elif (first and first.lower() in ("e", "edit")):
        subprocess.Popen(f'nano {CONF}', shell=True, stdout=sys.stdout, stderr=sys.stderr).wait()
    elif (first and first.lower() in ("h", "help")):
        help()
    else:
        print("wrong arg :(")


    




def main():
    check()
    # print(readAll())
    if(len(sys.argv) == 1):
        help()
        # print(sys.argv)
    argsy(sys.argv)

if __name__ == "__main__":
    main()
