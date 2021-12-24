#!/usr/bin/python3

import socket, urllib.request, logging
from os import environ, path, mkdir

base_path = path.dirname(path.abspath(__file__))
if not path.exists(base_path + "/logs"):
    mkdir(base_path + "/logs")

log = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")
log.setLevel(logging.INFO)
file_handler = logging.FileHandler(f"{base_path}/logs/vpn_check.log")
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
file_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)

log.addHandler(file_handler)
log.addHandler(stream_handler)


def get_home_address():
    return socket.gethostbyname(environ["HOME_DOMAIN_NAME"])


def get_current_ip():
    return urllib.request.urlopen("https://ipinfo.io/ip").read().decode()


def get_pid(proc):
    from subprocess import check_output, CalledProcessError

    try:
        return int(check_output(["pidof", proc]))
    except CalledProcessError as e:
        log.error(f"qb running?  {e}")


def kill_process(pid):
    from os import kill
    from signal import SIGKILL

    kill(pid, SIGKILL)
    log.warning("VPN was down!")


def is_safe():
    home_address = get_home_address()
    current_ip = get_current_ip()
    log.info(f"home ip: {home_address}, ext ip: {current_ip}")
    return home_address != current_ip


def main():
    pid = get_pid("qbittorrent-nox")
    if pid:
        if not is_safe():
            kill_process(pid)


if __name__ == "__main__":
    main()
