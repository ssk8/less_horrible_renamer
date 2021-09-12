#!/usr/bin/python3
from pathlib import Path
import qbittorrent
from os import environ
import paramiko
import re

kodi_address = "192.168.1.110"
kodi_hd_path = Path("/media/sda1-ata-WDC_WD20EZRZ-00Z")


def get_new_name(old_name):
    current_name = re.sub(r"^\[.+\] ", '', old_name)
    season_search = re.search("S[0-9]{1,2} ", current_name)
    if season_search:
        current_season = current_name[season_search.start()+1]
        current_name = current_name.replace(' S{}'.format(current_season), '')
    else:
        current_season = 1
    name_index = re.search(r" - [0-9]{1,2} [\[, (]", current_name).start()
    current_dir_name = current_name[0:name_index]
    current_name = '{} - S0{}E{}'.format(current_name[:name_index], current_season, current_name[name_index + 3:])
    return current_name, current_dir_name


def get_remote(sftp_client, path, dirs=True):
    mode = 16877*dirs or 33188
    files = list()
    return [f.filename for f in sftp_client.listdir_attr(str(path)) if f.st_mode==mode]


def unfinished_torrents():
    qb = qbittorrent.Client('http://localhost:8080/')
    qb.login(environ['QBIT_NAME'], environ['QBIT_PW'])
    return [t['name'] for t in qb.torrents() if t['amount_left']]

def get_finished_downloads(path, unfinished):
    downloads_files = [f for f in path.iterdir() if f.is_file()]
    return [f for f in downloads_files if f.name not in unfinished]

def main():
    ssh_client=paramiko.SSHClient()
    ssh_client.load_host_keys("/home/pi/.ssh/known_hosts")
    ssh_client.connect(hostname=kodi_address, username='root')
    sftp_client = ssh_client.open_sftp()

    tv_dirs = get_remote(sftp_client, kodi_hd_path / "TV Shows")

    unfinished = unfinished_torrents()

    downloads_path = Path("/home/pi/Downloads/")

    finished_downloads = get_finished_downloads(downloads_path, unfinished)
    for f in finished_downloads:
        new_name, dir_name = get_new_name(f.name)
        new_file_path = kodi_hd_path / 'TV Shows' / dir_name
        print(f"\"{f.name}\" to \"{new_name}\" in kodi directory \"{dir_name}\" which did{(dir_name not in tv_dirs)*' not'} exist")
        if dir_name not in tv_dirs:
            sftp_client.mkdir(str(new_file_path))
        current_files = get_remote(sftp_client, new_file_path, dirs=False)
        if new_name not in current_files:
            print(f"moving {f} to {new_file_path / new_name}")
            sftp_client.put(str(f), str(new_file_path / new_name))
        else:
            print(f"{f.name} is already there!!!")

if __name__ == "__main__":
    main()
