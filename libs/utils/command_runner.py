import paramiko
import re
import socket
import select
from typing import Optional, Tuple, List
from contextlib import contextmanager
import logging

CMD_RUNNER_UNLOGIN = 0
CMD_RUNNER_LOGIN = 1
CMD_RUNNER_ROOTLOGIN = 2

OSTYPE_LINUX = 'linux'
PARAMIKO_RECV_BUFFER_SIZE = 4096

logger = logging.getLogger(__name__)


class OS2SheetCommandRunnerException(Exception):
    def __init__(self,
                 message: str,
                 host: Optional[str] = None,
                 user: Optional[str] = None,
                 port: Optional[int] = None,
                 prompt_pattern: Optional[str] = None,
                 password_prompt: Optional[str] = None,
                 su_command: Optional[str] = None,
                 exit_command: Optional[str] = None,
                 os_type: Optional[str] = None,
                 encoding: Optional[str] = None,
                 command: Optional[str] = None,
                 stdout: Optional[str] = None,
                 original_exception: Optional[Exception] = None
                 ):
        """
        Initializes the OS2SheetCommandRunnerException instance.

        Args:
            message (str): The error message.
            host (str, optional): The hostname or IP address of the target server.
            user (str, optional): The username for SSH authentication.
            port (int, optional): The port for SSH connection.
            prompt_pattern (str, optional): The regex pattern for detecting the command prompt.
            password_prompt (str, optional): The regex pattern for detecting the password prompt.
            su_command (str, optional): The command to switch to the root user.
            exit_command (str, optional): The command to exit the shell.
            os_type (str, optional): The operating system type of the target server.
            encoding (str, optional): The encoding for command execution.
            command (str, optional): The command that caused the exception.
            stdout (str, optional): The stdout of the command that caused the exception.
            original_exception (Exception, optional): The original exception that caused this exception.
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
        self.original_exception = original_exception


class CommandRunner:
    def __init__(
        self, host: str, user: str, port: int = 22,
        password: Optional[str] = None, keyfile: Optional[str] = None,
        su_command: str = 'su',
        prompt_pattern: str = r'\[.+\][\$,#] $',
        password_prompt: str = r'Password: $',
        exit_command: str = 'exit',
        timeout: int = 60,
        encoding: str = 'utf-8',
        os_type: str = OSTYPE_LINUX
    ):
        """
        Initializes the CommandRunner instance.

        Args:
            host (str): The hostname or IP address of the target server.
            user (str): The username for SSH authentication.
            port (int, optional): The port for SSH connection. Defaults to 22.
            password (str, optional): The password for SSH authentication.
            keyfile (str, optional): The path to the private key file for key-based authentication.
            su_command (str, optional): The command to switch to the root user. Defaults to 'su'.
            prompt_pattern (str, optional): The regex pattern for detecting the command prompt.
            password_prompt (str, optional): The regex pattern for detecting the password prompt.
            exit_command (str, optional): The command to exit the shell. Defaults to 'exit'.
            timeout (int, optional): The timeout for the SSH connection in seconds. Defaults to 60.
            encoding (str, optional): The encoding for command execution. Defaults to 'utf-8'.
            os_type (str, optional): The operating system type of the target server. Defaults to OSTYPE_LINUX.

        Raises:
            ValueError: If host or user is empty.
        """
        if not host or not user:
            raise ValueError("host and user must not be empty")

        self.status = CMD_RUNNER_UNLOGIN
        self.host = host
        self.user = user
        self.port = port
        self.password = password
        self.keyfile = keyfile
        self.su_command = su_command
        self.prompt_pattern = prompt_pattern
        self.password_prompt = password_prompt
        self.exit_command = exit_command
        self.timeout = timeout
        self.encoding = encoding
        self.os_type = os_type

        self.ssh: Optional[paramiko.SSHClient] = None
        self.channel: Optional[paramiko.Channel] = None
        self._is_connected = False

        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}")

    def __enter__(self):
        """Context manager entry point."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point."""
        self.close()

    @property
    def is_connected(self) -> bool:
        """Check if the SSH connection is active."""
        if not self._is_connected or not self.ssh or not self.channel:
            return False
        try:
            # Check if the channel is still active
            if not self.channel.active:
                self._is_connected = False
                return False
            # Try to get the exit status of the last command
            self.channel.exit_status_ready()
            return True
        except (socket.error, paramiko.SSHException):
            self._is_connected = False
            return False

    def connect(self) -> None:
        """
        Establishes an SSH connection to the target server.

        Raises:
            OS2SheetCommandRunnerException: If the SSH connection fails.
            ValueError: If the connection parameters are invalid.
        """
        if self.is_connected or self.status != CMD_RUNNER_UNLOGIN:
            return

        if not self.host or not self.user:
            raise ValueError("host and user must not be empty")

        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Validate connection parameters
            if not self.password and not self.keyfile:
                raise ValueError("Either password or keyfile must be provided")

            self.ssh.connect(
                self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                key_filename=self.keyfile,
                timeout=self.timeout
            )
            self.channel = self.ssh.invoke_shell()
            self.status = CMD_RUNNER_LOGIN
            self._is_connected = True
            # プロンプト表示まで待機
            self.read_until_prompt(self.prompt_pattern)
            self.logger.info(
                f"Successfully connected to {self.host} as {self.user}")
        except (paramiko.SSHException, socket.error) as e:
            self._is_connected = False
            error_msg = f"Failed to connect to {self.host}: {str(e)}"
            self.logger.error(error_msg)
            raise OS2SheetCommandRunnerException(
                message=error_msg,
                host=self.host,
                user=self.user,
                port=self.port,
                os_type=self.os_type,
                original_exception=e
            )

    def read_until_prompt(self, prompt: str, timeout: Optional[int] = None) -> str:
        """
        Reads data from the SSH channel until a specified prompt is detected.

        Args:
            prompt (str): The regex pattern that indicates the end of the output.
            timeout (int, optional): The timeout in seconds. If None, uses the default timeout.

        Returns:
            str: The complete output received from the SSH channel.

        Raises:
            OS2SheetCommandRunnerException: If a timeout occurs or the connection is lost.
        """
        if not self.is_connected:
            raise OS2SheetCommandRunnerException(
                message="Not connected to the server",
                host=self.host,
                user=self.user
            )

        stdout = ''
        stdout_gotten = False
        if timeout is None:
            timeout = self.timeout

        try:
            while True:
                ready, _, _ = select.select([self.channel], [], [], timeout)
                if self.channel in ready:
                    try:
                        stdout_buffer = self.channel.recv(
                            PARAMIKO_RECV_BUFFER_SIZE)
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
                        timeout_message = f'Timeout while waiting for prompt: {prompt}'
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
                        stdout=stdout
                    )
        except (socket.error, paramiko.SSHException) as e:
            self._is_connected = False
            error_msg = f"Connection lost while reading output: {str(e)}"
            self.logger.error(error_msg)
            raise OS2SheetCommandRunnerException(
                message=error_msg,
                host=self.host,
                user=self.user,
                original_exception=e,
                stdout=stdout
            )

        return stdout

    def su(self, root_password: str, set_lang_c: bool = True) -> None:
        """
        Switches to the root user and sets the LANG environment variable to 'C' if specified.

        Args:
            root_password (str): The password for the root user.
            set_lang_c (bool): True to set the LANG environment variable to 'C', False otherwise.

        Raises:
            OS2SheetCommandRunnerException: If the su command fails or the connection is lost.
        """
        if not self.is_connected:
            raise OS2SheetCommandRunnerException(
                message="Not connected to the server",
                host=self.host,
                user=self.user
            )

        try:
            if set_lang_c:
                self.channel.send('LANG=C\n')
                self.read_until_prompt(self.prompt_pattern)

            self.channel.send(f'{self.su_command}\n')
            self.read_until_prompt(self.password_prompt)

            self.channel.send(f'{root_password}\n')
            self.read_until_prompt(self.prompt_pattern)

            self.status = CMD_RUNNER_ROOTLOGIN
            self.logger.info(
                f"Successfully switched to root user on {self.host}")
        except (socket.error, paramiko.SSHException) as e:
            self._is_connected = False
            error_msg = f"Failed to switch to root user: {str(e)}"
            self.logger.error(error_msg)
            raise OS2SheetCommandRunnerException(
                message=error_msg,
                host=self.host,
                user=self.user,
                original_exception=e
            )

    def __exec(self, command: str, timeout: Optional[int] = None) -> str:
        """
        Execute a command on the target system and return the output.

        Args:
            command (str): The command to execute.
            timeout (int, optional): The timeout for the command in seconds.

        Returns:
            str: The output of the command.

        Raises:
            OS2SheetCommandRunnerException: If the command execution fails or the connection is lost.
        """
        if not self.is_connected:
            raise OS2SheetCommandRunnerException(
                message="Not connected to the server",
                host=self.host,
                user=self.user
            )

        try:
            self.channel.send(command + '\n')
            output = self.read_until_prompt(self.prompt_pattern, timeout)
            return output
        except (socket.error, paramiko.SSHException) as e:
            self._is_connected = False
            error_msg = f"Failed to execute command '{command}': {str(e)}"
            self.logger.error(error_msg)
            raise OS2SheetCommandRunnerException(
                message=error_msg,
                host=self.host,
                user=self.user,
                command=command,
                original_exception=e
            )

    def __exec_linux(self, command: str, timeout: Optional[int] = None) -> str:
        """
        Execute a command on a Linux system and return the output.

        Args:
            command (str): The command to be executed.
            timeout (int, optional): The timeout in seconds for the read operation.

        Returns:
            str: The output of the command.

        Raises:
            OS2SheetCommandRunnerException: If the command execution fails or the connection is lost.
        """
        if not self.is_connected:
            raise OS2SheetCommandRunnerException(
                message="Not connected to the server",
                host=self.host,
                user=self.user
            )

        try:
            self.channel.send(
                f"{{ {command}; echo; }} | "
                "while IFS= read -r line; do "
                "echo \"//CMD_RESULT $line\"; done\n"
            )
            output = self.read_until_prompt(self.prompt_pattern, timeout)
            result_lines = []
            for line in output.splitlines():
                if line.startswith('//CMD_RESULT $line"; done'):
                    continue
                if line.startswith('//CMD_RESULT '):
                    result_lines.append(line.replace('//CMD_RESULT ', '', 1))

            return '\n'.join(result_lines)
        except (socket.error, paramiko.SSHException) as e:
            self._is_connected = False
            error_msg = f"Failed to execute Linux command '{command}': {str(e)}"
            self.logger.error(error_msg)
            raise OS2SheetCommandRunnerException(
                message=error_msg,
                host=self.host,
                user=self.user,
                command=command,
                original_exception=e
            )

    def exec(self, command: str, timeout: Optional[int] = None) -> str:
        """
        Execute a command on the target system and return the output.

        Args:
            command (str): The command to execute.
            timeout (int, optional): The timeout for the command in seconds.

        Returns:
            str: The output of the command.

        Raises:
            OS2SheetCommandRunnerException: If the command execution fails or the connection is lost.
        """
        if not command:
            raise ValueError("Command must not be empty")

        if self.os_type == OSTYPE_LINUX:
            return self.__exec_linux(command, timeout)
        else:
            return self.__exec(command, timeout)

    def close(self) -> None:
        """
        Close SSH channel and SSH client connection.

        This method is called when the CommandRunner object is garbage collected.
        It is recommended to call this method explicitly when you finish using the CommandRunner object.
        """
        try:
            if self.channel:
                self.channel.close()
            if self.ssh:
                self.ssh.close()
        except Exception as e:
            self.logger.warning(f"Failed to close connection: {str(e)}")
        finally:
            self.channel = None
            self.ssh = None
            self._is_connected = False
            self.status = CMD_RUNNER_UNLOGIN

    def __del__(self):
        """Destructor to ensure proper cleanup."""
        self.close()
