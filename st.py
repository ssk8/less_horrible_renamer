#!/usr/bin/python3
from vpn_check import is_safe
from subprocess import Popen


def main():
    if is_safe():
        print("all clear")
        Popen("qbittorrent-nox")
    else:
        print("NoT toDay, wOOdy!")


if __name__ == "__main__":
    main()
