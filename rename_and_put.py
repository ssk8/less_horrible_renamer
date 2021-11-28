#!/usr/bin/python3

from itertools import chain
from pathlib import Path
import qbittorrentapi
from os import environ
import paramiko
import re
from typing import List
import logging

downloads_path = Path("/home/pi/Downloads/")
kodi_address = "192.168.1.110"
kodi_hd_path = Path("/media/sda1-ata-WDC_WD20EZRZ-00Z")
file_types = ["*.mkv", "*.avi", "*.ass", "*.srt", "*.mp4"]

base_path = Path(__file__).parent.absolute()
have_file = base_path / 'have.json'
wants_file = base_path / 'want.json'

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

file_handler = logging.FileHandler(base_path / 'logs' / 'rename.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)

log.addHandler(file_handler)
log.addHandler(stream_handler)


def get_new_name(old_name: str) -> (str, str):
    current_name = re.sub(r"^\[.{0,18}\] ", '', old_name)
    formated_index = re.search(r"[ ._-]{0,3}[Ss]\d{1,2}[ ]{0,1}[Ee]\d{1,2}", current_name)
    if formated_index:
        current_dir_name = current_name[0:formated_index.start()]
        current_dir_name = re.sub(r"[._]", " ", current_dir_name)
    else:
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


def get_remote(sftp_client: paramiko.sftp_client.SFTPClient, path, dirs=True) -> List[str]:
    """returns a list of remote directories at 'path' on 'sftp_client' if 'dirs' or list of files if not 'dirs'"""
    mode = 16877*dirs or 33188
    return [f.filename for f in sftp_client.listdir_attr(str(path)) if f.st_mode==mode]


def unfinished_torrents() -> List[str]:
    qb = qbittorrentapi.Client(host='localhost', port=8080, username=environ['QBIT_NAME'], password=environ['QBIT_PW'])
    qb.auth_log_in()
    hashes = [t.hash for t in qb.torrents_info()]
    return [t.name for h in hashes for t in qb.torrents_files(h) if t.progress!=1]


def get_finished_downloads(path: Path, unfinished: List[str]) -> List[Path]:
    unfinished_files = [path / uf for uf in unfinished]
    finished_files = [f for f in chain(*[path.rglob(ft) for ft in file_types]) if f not in unfinished_files]
    return finished_files


def get_sftp_client(address: str) -> paramiko.sftp_client.SFTPClient:
    ssh_client=paramiko.SSHClient()
    ssh_client.load_host_keys("/home/pi/.ssh/known_hosts")
    ssh_client.connect(hostname=address, username='root')
    return ssh_client.open_sftp()


def put_files(files, sftp_client: paramiko.sftp_client.SFTPClient) -> None:
    tv_dirs = get_remote(sftp_client, kodi_hd_path / "TV Shows")
    for f in files:
        try:
            new_name, dir_name = get_new_name(f.name)
        except AttributeError:
            log.info(f"{f.name} didn't fit a known pattern")
            continue
        new_file_path = kodi_hd_path / 'TV Shows' / dir_name
        if dir_name not in tv_dirs:
            sftp_client.mkdir(str(new_file_path))
            tv_dirs.append(dir_name)
        current_files = get_remote(sftp_client, new_file_path, dirs=False)
        if new_name not in current_files:
            log.info(f"\"{f.name}\" to \"{new_name}\" in kodi directory \"{dir_name}\"")
            sftp_client.put(str(f), str(new_file_path / new_name))


def main():
    kodi_sftp = get_sftp_client(kodi_address)
    finished_downloads = get_finished_downloads(downloads_path, unfinished_torrents())
    put_files(finished_downloads, kodi_sftp)


if __name__ == "__main__":
    main()
