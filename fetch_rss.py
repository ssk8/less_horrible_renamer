#!/usr/bin/python3

from bs4 import BeautifulSoup
import requests
import json
import qbittorrent
from os import environ


def add_torrents(magnets_list):
    qb = qbittorrent.Client('http://localhost:8080/')
    qb.login(environ['QBIT_NAME'], environ['QBIT_PW'])
    [qb.download_from_link(ct) for ct in magnets_list]


def get_json(json_file):
  with open(json_file, 'r') as f:
    data = json.load(f)
  return data


def get_feed(rss_address):
  url = requests.get(rss_address)
  soup = BeautifulSoup(url.content, "xml")
  items = soup.find_all('item')
  return {i.title.text:i.link.text for i in items}


def main():
  wants = get_json('want.json')
  have_list = get_json('have.json')
  to_get = dict()
  for site, want in wants.items():
    shows_feed = get_feed(site)
    for new_show, magnet in shows_feed.items():
      for want_show in want:
        if all(s in new_show for s in want_show) and ("(Batch)" not in new_show): 
          if new_show not in have_list:
            to_get[new_show] = magnet

  if to_get:
    have_list.extend(to_get.keys())        
    add_torrents(to_get.values())
    with open("have.json", 'w') as f:
      json.dump(have_list, f)


if __name__ == "__main__":
  main()
