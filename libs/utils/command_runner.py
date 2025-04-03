import paramiko
import re
import socket
import select

CMD_RUNNER_UNLOGIN = 0
CMD_RUNNER_LOGIN = 1
CMD_RUNNER_ROOTLOGIN = 2

OSTYPE_LINUX = 'linux'
PARAMIKO_RECV_BUFFER_SIZE = 4096

class OS2SheetCommandRunnerException(Exception):
    def __init__(self, 
        message: str,
        host: str = None, 
        user: str = None,
        port: int = None,
        prompt_pattern: str = None,
        password_prompt: str = None,
        su_command: str = None,
        exit_command: str = None,
        os_type: str = None,
        encoding: str = None,
        command: str = None,
        stdout: str = None
    ):
        
        """
        Initializes the OS2SheetCommandRunnerException instance.

        Args:
            message (str): The error message.
            host (str, optional): The hostname or IP address of the target server. Defaults to None.
            user (str, optional): The username for SSH authentication. Defaults to None.
            port (int, optional): The port for SSH connection. Defaults to None.
            prompt_pattern (str, optional): The regex pattern for detecting the command prompt. Defaults to None.
            password_prompt (str, optional): The regex pattern for detecting the password prompt. Defaults to None.
            su_command (str, optional): The command to switch to the root user. Defaults to None.
            exit_command (str, optional): The command to exit the shell. Defaults to None.
            os_type (str, optional): The operating system type of the target server. Defaults to None.
            encoding (str, optional): The encoding for command execution. Defaults to None.
            command (str, optional): The command that caused the exception. Defaults to None.
            stdout (str, optional): The stdout of the command that caused the exception. Defaults to None.
        """
        super().__init__(message)
        self.host = host
        self.user = user
        self.port = port
        self.prompt_pattern = prompt_pattern
        self.password_prompt = password_prompt
        self.su_command = su_command
        self.exit_command = exit_command
        self.os_type = os_type
        self.encoding = encoding
        self.command = command
        self.stdout = stdout

class CommandRunner():
    def __init__(
        self, host: str, user: str, port: int = 22,
        password: str = None, keyfile: str = None,
        su_command: str = 'su',
        prompt_pattern: str = r'\[.+\][\$,#] $',
        password_prompt: str = r'Password: $',
        exit_command: str = 'exit',
        timeout: int = 60,
        encoding: str = 'utf-8',
        os_type: str = OSTYPE_LINUX
    ):
        """
        Initializes the CommandRunner instance and establishes an SSH connection.
    
        Args:
            host (str): The hostname or IP address of the target server.
            user (str): The username for SSH authentication.
            port (int, optional): The port for SSH connection. Defaults to 22.
            password (str, optional): The password for SSH authentication. Defaults to None.
            keyfile (str, optional): The path to the private key file for key-based authentication. Defaults to None.
            su_command (str, optional): The command to switch to the root user. Defaults to 'su'.
            prompt_pattern (str, optional): The regex pattern for detecting the command prompt. Defaults to r'\[.+\][\$,#] $'.
            password_prompt (str, optional): The regex pattern for detecting the password prompt. Defaults to r'Password: $'.
            exit_command (str, optional): The command to exit the shell. Defaults to 'exit'.
            timeout (int, optional): The timeout for the SSH connection in seconds. Defaults to 60.
            encoding (str, optional): The encoding for command execution. Defaults to 'utf-8'.
            os_type (str, optional): The operating system type of the target server. Defaults to OSTYPE_LINUX.
    
        Raises:
            paramiko.SSHException: If the SSH connection fails.
        """
        self.status = CMD_RUNNER_UNLOGIN
        self.host = host
        self.user = user
        self.port = port
        self.su_command = su_command
        self.prompt_pattern = prompt_pattern
        self.password_prompt = password_prompt
        self.exit_command = exit_command
        self.timeout = timeout
        self.encoding = encoding
        self.os_type = os_type

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(
            self.host,
            port=self.port,
            username=self.user,
            password=password,
            key_filename=keyfile,
            timeout=self.timeout
        )
        self.channel = self.ssh.invoke_shell()

        self.status = CMD_RUNNER_LOGIN

    def read_until_prompt(self, prompt: str, timeout: int = None) -> str:
        """
        Reads data from the SSH channel until a specified prompt is detected.
    
        Args:
            prompt (str): The regex pattern that indicates the end of the output.
    
        Returns:
            str: The complete output received from the SSH channel up to and including the line where the prompt is detected.
    
        Raises:
            OS2SheetCommandRunnerException: If a timeout occurs while waiting for the prompt.
    
        Note:
            This method expects the SSH channel to be open and authenticated prior to calling.
        """
        stdout = ''
        stdout_gotten = False
        if timeout is not None:
            timeout = self.timeout
        while True:
            ready, _, _ = select.select([self.channel], [], [], timeout)
            if self.channel in ready:
                try:
                    stdout_buffer = self.channel.recv(PARAMIKO_RECV_BUFFER_SIZE)
                    if not stdout_buffer:
                        break
                    stdout += stdout_buffer.decode(self.encoding)
                    stdout_gotten = True
                    if re.search(prompt, stdout.splitlines()[-1]):
                        break
                except socket.timeout:
                    pass
            else:
                if stdout_gotten:
                    timeout_message = 'Timeout while waiting for prompt: {prompt}'
                else:
                    timeout_message = 'Timeout while waiting for output'
                raise OS2SheetCommandRunnerException(
                    message=timeout_message,
                    host=self.host,
                    user=self.user,
                    port=self.port,
                    prompt_pattern=self.prompt_pattern,
                    password_prompt=self.password_prompt,
                    su_command=self.su_command,
                    exit_command=self.exit_command,
                    os_type=self.os_type,
                    encoding=self.encoding,
                    command=None,
                    stdout=stdout
                )
        return stdout
                
    def su(
        self, root_password: str, 
        set_lang_c: bool = True
    ) -> None:
        """
        Switches to the root user and sets the LANG environment variable to 'C' if specified.
    
        Args:
            root_password (str): The password for the root user.
            set_lang_c (bool): True to set the LANG environment variable to 'C', False otherwise.
        """
        if set_lang_c:
            self.channel.send('LANG=C\n')
            self.read_until_prompt(self.prompt_pattern)
        
        self.channel.send(f'{self.su_command}\n')
        self.read_until_prompt(self.password_prompt)
        
        self.channel.send(f'{root_password}\n')
        self.read_until_prompt(self.prompt_pattern)
        
        self.status = CMD_RUNNER_ROOTLOGIN

    def __exec(
        self, command: str, timeout: int = None
    ) -> str:
        """
        Execute a command on the target system and return the output.

        Args:
            command (str): The command to execute.
            timeout (int): The timeout for the command in seconds.

        Returns:
            str: The output of the command.
        """
        self.channel.send(command + '\n')
        output = self.read_until_prompt(self.prompt_pattern, timeout)
        return output

    def __exec_linux(
        self, command: str, timeout: int = None
    ) -> str:
        """
        Execute a command on a Linux system and return the output.

        This method prefixes the command with a special prefix to detect the end of the command's output.
        It reads the output from the SSH channel until it detects the prefix, and then returns the rest of the output.

        Args:
            command (str): The command to be executed.
            timeout (int): The timeout in seconds for the read operation.

        Returns:
            str: The output of the command.

        Raises:
            OS2SheetCommandRunnerException: If a timeout occurs while waiting for the output.
        """
        self.channel.send(
            f"{{ {command}; echo; }} | "
            "while IFS= read -r line; do "
            "echo \"//CMD_RESULT $line\"; done\n"
        )
        output = self.read_until_prompt(self.prompt_pattern, timeout)
        result_lines = []
        for line in output.splitlines():
            # Handling cases where line breaks due to the tty window width
            # cause the command's prefix to appear at the beginning.
            if line.startswith('//CMD_RESULT $line"; done'):
                continue
            if line.startswith('//CMD_RESULT '):
                result_lines.append(line.replace('//CMD_RESULT ', '', 1))

        return '\n'.join(result_lines)

    def exec(
        self, command: str, timeout: int = None
    ) -> str:
        """
        Execute a command on the target system and return the output.

        Args:
            command (str): The command to execute.
            timeout (int): The timeout for the command in seconds.

        Returns:
            str: The output of the command.

        Raises:
            OS2SheetCommandRunnerException: If a timeout occurs while waiting for the output.
        """
        if self.os_type == OSTYPE_LINUX:
            return self.__exec_linux(command, timeout)
        else:
            return self.__exec(command, timeout)

    def close(self):
        """
        Close SSH channel and SSH client connection.

        This method is called when the CommandRunner object is garbage collected.
        It is recommended to call this method explicitly when you finish using the CommandRunner object.

        """
        if self.ssh is not None:
            self.ssh.close()

    def __del__(self):
        self.close()



