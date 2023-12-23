

class SshResponse(tuple):

    @property
    def stdin(self):
        return self[0]

    @property
    def stdout(self):
        return self[1].read().decode()

    @property
    def stderr(self):
        return self[2].read().decode()
