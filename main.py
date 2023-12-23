import argparse
import os

from utils.vorunner import VoRunner

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--local_dir', "-w", help='Path to local working folder', required=False)
    parser.add_argument('--link', "-l", help='Magnet link to download', required=True)
    parser.add_argument('--host', help='Remote host', required=False)
    parser.add_argument('--user', "-u", help='Remote user', required=False)
    parser.add_argument('--password', "-p", help='Remote password', required=False)
    parser.add_argument('--ssh_key', help='Pass to private ssh key file', required=False)
    args = parser.parse_args()
    with VoRunner(host=args.host,
                  username=args.user,
                  password=args.password,
                  private_key_path=args.ssh_key,
                  local_work_dir=args.local_dir or os.getcwd()) as vorunner:
        vorunner.download(args.link)

