#!/usr/bin/python3

import feedparser
import json
import qbittorrent
from os import environ
import vpn_check
import sys
from pathlib import Path


def preconditions():
  pid = vpn_check.get_pid("qbittorrent-nox")
  if pid:
      if not vpn_check.is_safe():
          vpn_check.kill_process(pid)
          sys.exit("vpn not running")
  else:
      sys.exit("qb not running")    
      

def add_torrents(magnets_list):
    qb = qbittorrent.Client('http://localhost:8080/')
    qb.login(environ['QBIT_NAME'], environ['QBIT_PW'])
    [qb.download_from_link(ct) for ct in magnets_list]


def get_json(json_file):
  with open(json_file, 'r') as f:
    data = json.load(f)
  return data


def get_feed(rss_address):
  feed = feedparser.parse(rss_address)
  entries = feed['entries'] 
  return {entry['title']:entry['links'][0]['href'] for entry in entries}


def get_list_to_get(wants, already_got):
  to_get = dict()
  for site, want in wants.items():
    shows_feed = get_feed(site)
    for new_show, magnet in shows_feed.items():
      for want_show in want:
        if all(s in new_show for s in want_show) and ("(Batch)" not in new_show): 
          if new_show not in already_got:
            to_get[new_show] = magnet
  return to_get


def main():
  preconditions()
  base_path = Path(__file__).parent.absolute()
  have_file = base_path/'have.json'
  wants_file = base_path/'want.json'
  wants = get_json(wants_file)
  have_list = get_json(have_file) if have_file.exists() else []
  to_get = get_list_to_get(wants, have_list)

  if to_get:
    have_list.extend(to_get.keys())        
    add_torrents(to_get.values())
    with open(have_file, 'w') as f:
      json.dump(have_list, f)


if __name__ == "__main__":
  main()
  