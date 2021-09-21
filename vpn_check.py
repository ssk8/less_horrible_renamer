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
        from subprocess import check_output, CalledProcessError
        try:
            kill(int(check_output(["pidof", proc])), SIGKILL)
            print("killed the offender")
        except CalledProcessError:
            print("no worries")


def is_safe():
    home_address = get_home_address()
    current_ip = get_current_ip()
    return home_address != current_ip


def main():
    if not is_safe():
        kill_process("qbittorrent-nox")


if __name__ == "__main__":
    main()
