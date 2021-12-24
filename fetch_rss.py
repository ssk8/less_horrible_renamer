#!/usr/bin/python3

import feedparser
import json
import qbittorrentapi
from os import environ
import vpn_check
import sys
from pathlib import Path
import logging

base_path = Path(__file__).parent.absolute()
have_file = base_path / "have.json"
wants_file = base_path / "want.json"

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s:%(name)s:%(message)s")

file_handler = logging.FileHandler(base_path / "logs" / "fetch.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)

log.addHandler(file_handler)
log.addHandler(stream_handler)


def preconditions():
    pid = vpn_check.get_pid("qbittorrent-nox")
    if pid:
        if not vpn_check.is_safe():
            vpn_check.kill_process(pid)
            log.warning("VPN is down, stopping here!")
            sys.exit("vpn not running")
    else:
        log.warning("qb down")
        sys.exit("qb not running")


def add_torrents(magnets):
    qb = qbittorrentapi.Client(
        host="localhost",
        port=8080,
        username=environ["QBIT_NAME"],
        password=environ["QBIT_PW"],
    )
    qb.auth_log_in()
    qb.torrents_add(urls=magnets)


def get_json(json_file):
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        log.exception(f"{json_file} is missing!")
    except json.decoder.JSONDecodeError:
        log.exception(f"problem parsing json file {json_file}")
    return data


def get_feed(rss_address):
    feed = feedparser.parse(rss_address)
    entries = feed["entries"]
    return {entry["title"]: entry["links"][0]["href"] for entry in entries}


def get_list_to_get(wants, already_got):
    to_get = dict()
    for site, want in wants.items():
        shows_feed = get_feed(site)
        for new_show, magnet in shows_feed.items():
            for want_show in want:
                if all(s in new_show for s in want_show) and (
                    "(Batch)" not in new_show
                ):
                    if new_show not in already_got:
                        to_get[new_show] = magnet
    return to_get


def main():
    log.info("checking in")
    preconditions()
    wants = get_json(wants_file)
    have_list = get_json(have_file) if have_file.exists() else []
    to_get = get_list_to_get(wants, have_list)

    if to_get:
        for k in to_get.keys():
            log.info(f"fetching {k}")
        have_list.extend(to_get.keys())
        add_torrents(to_get.values())
        with open(have_file, "w") as f:
            json.dump(have_list, f)


if __name__ == "__main__":
    main()
