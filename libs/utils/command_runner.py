from pexpect import pxssh

CMD_RUNNER_UNLOGIN = 0
CMD_RUNNER_LOGIN = 1
CMD_RUNNER_ROOTLOGIN = 2

DEFAULT_EXPECT_PROMPT = r'\[.+\][\$,#] '
DEFAULT_EXPECT_PASSWORD = r'Password:'
DEFAULT_SU_CMD = 'su'
DEFAULT_EXIT_CMD = 'exit'

OSTYPE_LINUX = 'linux'

class CommandRunner():
    def __init__(
        self, server: str, username: str, port: int = 22,
        password: str = None, keyfile: str = None,
        su_cmd: str = DEFAULT_SU_CMD,
        expect_prompt: str = DEFAULT_EXPECT_PROMPT,
        expect_password: str = DEFAULT_EXPECT_PASSWORD, 
        exit_cmd: str = DEFAULT_EXIT_CMD,
        ostype: str = OSTYPE_LINUX
    ):
        self.status = CMD_RUNNER_UNLOGIN
        self.ssh = pxssh.pxssh()
        self.ssh.login(
            server=server, username=username, port=port,
            password=password, ssh_key=keyfile
        )
        self.status = CMD_RUNNER_LOGIN

        self.su_cmd = su_cmd
        self.expect_prompt = expect_prompt
        self.expect_password = expect_password
        self.exit_cmd = exit_cmd
        self.ostype = ostype

    def su(
        self, password: str, 
        lang_c: bool = True
    ):
        if lang_c:
            self.ssh.sendline('LANG=C')
        self.ssh.sendline(self.su_cmd)
        self.ssh.expect(self.expect_password, timeout=60)
        self.ssh.sendline(password + '\r')
        self.ssh.expect(self.expect_prompt,timeout=60)
        self.status = CMD_RUNNER_ROOTLOGIN

    def __exec(
        self, command: str, encoding: str = 'utf-8'
    ) -> str:
        self.ssh.sendline(command)
        self.ssh.expect(self.expect_prompt,timeout=60)
        raw_result = self.ssh.after.decode(encoding=encoding)
        return raw_result

    def __exec_linux(
        self, command: str, encoding: str = 'utf-8'
    ) -> str:
        self.ssh.sendline(
            "{ " + command + "; echo; }" +
            '| while IFS= read -r line; do echo "//CMD_RESULT $line"; done'
        )
        self.ssh.expect(self.expect_prompt,timeout=60)
        raw_result = self.ssh.after.decode(encoding=encoding)
        fixed_result = []
        for l in raw_result.splitlines():
            if l.startswith('//CMD_RESULT '):
                fixed_result.append(l.replace('//CMD_RESULT ', '', 1))

        return '\n'.join(fixed_result)

    def exec(
        self, command: str, encoding: str = 'utf-8'
    ) -> str:
        if self.ostype == OSTYPE_LINUX:
            return self.__exec_linux(command, encoding)
        else:
            return self.__exec(command, encoding)

    def __del__(self):
        if self.status == CMD_RUNNER_ROOTLOGIN:
            self.ssh.sendline(self.exit_cmd)
        self.ssh.logout()


