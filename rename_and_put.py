#!/usr/bin/python3
from pathlib import Path
import qbittorrent
from os import environ
import paramiko
import re

downloads_path = Path("/home/pi/Downloads/")
kodi_address = "192.168.1.110"
kodi_hd_path = Path("/media/sda1-ata-WDC_WD20EZRZ-00Z")


def get_new_name(old_name):
    current_name = re.sub(r"^\[.+\] ", '', old_name)
    season_search = re.search("S[0-9]{1,2} ", current_name)
    if season_search:
        current_season = current_name[season_search.start()+1]
        current_name = current_name.replace(f' S{current_season}', '')
    else:
        current_season = 1
    name_index = re.search(r" - [0-9]{1,2} [\[, (]", current_name).start()
    current_dir_name = current_name[0:name_index]
    current_name = f'{current_name[:name_index]} - S0{current_season}E{current_name[name_index + 3:]}'
    return current_name, current_dir_name


def get_remote(sftp_client, path, dirs=True):
    """returns a list of remote directories at 'path' on 'sftp_client' if 'dirs' or list of files if not 'dirs'"""
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


def get_sftp_client(address):
    ssh_client=paramiko.SSHClient()
    ssh_client.load_host_keys("/home/pi/.ssh/known_hosts")
    ssh_client.connect(hostname=kodi_address, username='root')
    return ssh_client.open_sftp()


def main():
    kodi_sftp = get_sftp_client(kodi_address)
    tv_dirs = get_remote(kodi_sftp, kodi_hd_path / "TV Shows")
    finished_downloads = get_finished_downloads(downloads_path, unfinished_torrents())
    for f in finished_downloads:
        try:
            new_name, dir_name = get_new_name(f.name)
        except AttributeError:
            print(f"{f.name} didn't fint a known pattern")
            continue
        new_file_path = kodi_hd_path / 'TV Shows' / dir_name
        print(f"\"{f.name}\" to \"{new_name}\" in kodi directory \"{dir_name}\" which did{(dir_name not in tv_dirs)*' not'} exist")
        if dir_name not in tv_dirs:
            kodi_sftp.mkdir(str(new_file_path))
        current_files = get_remote(kodi_sftp, new_file_path, dirs=False)
        if new_name not in current_files:
            print(f"moving {f} to {new_file_path / new_name}")
            kodi_sftp.put(str(f), str(new_file_path / new_name))
        else:
            print(f"{new_name} is already there!!!")

if __name__ == "__main__":
    main()
