# Automate the fun stuff

These files are intended to be used on a small, headless computer (Raspberry Pi) running a VPN and qbittorrent-nox:
### fetch_rss.py
- gets magnets from rss feeds as specified in "want.json" 
(modify "example_want.json" and save as "want.json")
- starts downloading them to the local machine


note: right now I run this every hour (cron) but TODO... replace the json with a sqlite database with dates and times so it will only runs when necessary
### rename_and_put.py
- moves files from "Downloads" on local machine to a media server (e.g. Kodi)
- renames files and creates folders (if needed) in parseable format
- makes sure files are finished downloading so it can be run by qb on finished downloads
#
Keys will need to be in place for kodi machine:
```bash
ssh-copy-id root@kodi_address
```
and add info to .bashrc on the t-box like this:

```bash
export QBIT_NAME='user'
export QBIT_PW='password'
export HOME_DOMAIN_NAME="dymanic DNS name"
# also handy:
alias wmi="curl ipinfo.io/ip && echo"
alias st="python3 /home/pi/tbox_helpers/st.py"
alias ren="python3 /home/pi/tbox_helpers/rename_and_put.py"
alias fetch="python3 /home/pi/tbox_helpers/fetch_rss.py"
```

and for cron (crontab -e) on the t-box like this:

```bash
QBIT_NAME='user'
QBIT_PW='password'
HOME_DOMAIN_NAME="dymanic DNS name"
*/5 * * * * /home/pi/tbox_helpers/vpn_check.py
20 * * * * /home/pi/tbox_helpers/fetch_rss.py
```
