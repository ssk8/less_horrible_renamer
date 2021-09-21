#!/usr/bin/python3
import socket, urllib.request
from os import environ


def get_home_address():
    return socket.gethostbyname(environ["HOME_DOMAIN_NAME"])


def get_current_ip():
    return urllib.request.urlopen("https://ipinfo.io/ip").read().decode()


def kill_process(proc):
        from os import kill
        from signal import SIGKILL
        from subprocess import check_output
        qbpid = int(check_output(["pidof", proc]))
        kill(qbpid, SIGKILL)


def main():
    home_address = get_home_address()
    current_ip = get_current_ip()
    if home_address==current_ip:
        kill_process("qbittorrent-nox")


if __name__ == "__main__":
    main()
