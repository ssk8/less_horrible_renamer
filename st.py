#!/usr/bin/python3
from vpn_check import is_safe
from subprocess import run

def main():
    if is_safe():
        print("all clear")
        run("qbittorrent-nox &", shell=True)
    else:
        print("NoT toDay, wOOdy!")


if __name__ == "__main__":
    main()
