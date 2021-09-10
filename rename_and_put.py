#!/usr/bin/python3
from pathlib import Path
import qbittorrent
from os import environ, sys
import paramiko

torrent_box_web_address = 'http://192.168.1.106:8080/'
kodi_address = "192.168.1.110"
kodi_path = Path("/storage/test")

ssh_client=paramiko.SSHClient()
ssh_client.load_host_keys("/home/pi/.ssh/known_hosts")
ssh_client.connect(hostname=kodi_address,username='root')
sftp_client = ssh_client.open_sftp()
dir_list = sftp_client.listdir(str(kodi_path))
print(dir_list)


def check_torrents():
    qb = qbittorrent.Client(torrent_box_web_address)
    qb.login(environ['QBIT_NAME'], environ['QBIT_PW'])
    return qb.torrents()


torrents = check_torrents()

for torrent in torrents:
    print(f"{torrent['name']} is done: {not bool(torrent['amount_left'])}")

