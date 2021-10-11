# automate the fun stuff

Keys will need to be in place for kodi machine:
```bash
ssh-copy-id root@kodi_address
```
and add web controll creds to .bashrc on the t-box like this:

```bash
export QBIT_NAME='user'
export QBIT_PW='password'
export HOME_DOMAIN_NAME="dymanic DNS name"
```
and for cron (crontab -e) on the t-box like this:

```bash
QBIT_NAME='user'
QBIT_PW='password'
HOME_DOMAIN_NAME="dymanic DNS name"
*/5 * * * * /home/pi/tbox_helpers/vpn_check.py
20 * * * * /home/pi/tbox_helpers/fetch_rss.py
```