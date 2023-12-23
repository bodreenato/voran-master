## VORUN 
### Description
Tool for downloading files via Torrent on a remote server and transfer it back to local machine using SSH connection
### Pre requirements:
`aria2c` installed on remote
```bash
sudo apt-get install aria2
```
### Interface
* `--link`, `-l` - magnet link to download
* `--local_dir`, `-w` (optional) - path to local working folder
* `--host`, `-w` - remote host
* `--user` - remote username
* `--password` - remote password
* `--ssh_key` - pass to private ssh key file

### TODO
To indicate progress of transferring
