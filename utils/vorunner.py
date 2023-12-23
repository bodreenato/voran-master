import os
import re
from functools import cached_property
from uuid import uuid4

import paramiko

from utils.ssh_response import SshResponse


class VoRunner:

    def __init__(self, host: str, username: str, password: str, private_key_path: str,
                 local_work_dir: str):
        self.private_key_path = private_key_path
        self.password = password
        self.username = username
        self.local_workdir = os.path.join(local_work_dir, f"vorunnerlocal-{str(uuid4())}")
        print(f"Creating local dir {self.local_workdir}")
        os.mkdir(self.local_workdir)
        self.host = host

    def __enter__(self):
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {self.host}...")
        self.client.connect(self.host, 22, self.username, self.password,
                            pkey=paramiko.RSAKey(filename=self.private_key_path))
        remote_workdir_name = f"vorunnerwork_{str(uuid4())}"
        print(f"Creating remote dir {remote_workdir_name}")
        self.command(f"mkdir {remote_workdir_name}")
        self.remote_workdir = f"~/{remote_workdir_name}"
        self.remote_workdir = self.client.exec_command(f"realpath {self.remote_workdir}")[1].read().decode().replace("\n", "")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Removing remote {self.remote_workdir}")
        self.command(f"rm -r {self.remote_workdir}")
        print("Killing process aria2c")
        self.command("kill aria2c")
        print("Closing SFTP connection")
        self.sftp.close()
        print("Closing SSH connection")
        self.client.close()

    def command(self, cmd: str) -> SshResponse:
        # print(">  " + cmd)
        ssh_response = SshResponse(self.client.exec_command(cmd))
        _ = ssh_response.stdout
        # print(f"{ssh_response.stdout}")
        # print(f"{ssh_response.stderr}")
        return ssh_response

    @cached_property
    def client(self) -> paramiko.SSHClient:
        return paramiko.SSHClient()

    @cached_property
    def sftp(self) -> paramiko.SFTPClient:
        return self.client.open_sftp()

    def transfer_folder(self, remote_path: str, local_path: str) -> None:
        files = self.client.exec_command(f"find {remote_path}")[1].read().decode().split("\n")
        files = [file for file in files if file != ""]
        print(f"Found {len(files)} files to transfer")
        if not os.path.exists(local_path):
            print(f"{local_path} not found, creating...")
            os.mkdir(local_path)
        for file in files:
            if re.match(r".+/.+\..+", file) and not file.endswith(".torrent"):
                try:
                    print(f"Transferring: {file}")
                    self.sftp.get(file, os.path.join(local_path,
                                                     os.path.basename(file)))
                except OSError:
                    print(f"Error transferring {file}")
            else:
                print(f"Skipped: {file}")

    def download(self, link: str):
        print(f"Downloading to remote: {link}")
        self.command(f"aria2c --seed-time=0 -d {self.remote_workdir} \"{link}\"")
        self.transfer_folder(self.remote_workdir,
                             self.local_workdir)
