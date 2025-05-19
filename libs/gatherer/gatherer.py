from libs.utils import CommandRunner, OSTYPE_LINUX
import re
import json


class Gatherer():
    def __init__(
        self, host: str, user: str, port: int = 22,
        password: str = None, keyfile: str = None,
        su_command: str = 'su',
        prompt_pattern: str = r'\[.+\][\$,#] $',
        password_prompt: str = r'Password: $',
        exit_command: str = 'exit',
        timeout: int = 60,
        encoding: str = 'utf-8',
        os_type: str = OSTYPE_LINUX,
        root_password: str = None
    ):
        """
        Initializes the Gatherer instance.

        Args:
            host (str): The hostname or IP address of the target server.
            user (str): The username for SSH authentication.
            port (int, optional): The port for SSH connection. Defaults to 22.
            password (str, optional): The password for SSH authentication. Defaults to None.
            keyfile (str, optional): The path to the private key file for key-based authentication. Defaults to None.
            su_command (str, optional): The command to use for su authentication. Defaults to 'su'.
            prompt_pattern (str, optional): The pattern to use for prompt detection. Defaults to r'\[.+\][\$,#] $'.
            password_prompt (str, optional): The prompt for password input. Defaults to r'Password: $'.
            exit_command (str, optional): The command to use for exiting the su session. Defaults to 'exit'.
            timeout (int, optional): The timeout for SSH connection. Defaults to 60.
            encoding (str, optional): The encoding for SSH connection. Defaults to 'utf-8'.
            os_type (str, optional): The type of operating system. Defaults to OSTYPE_LINUX.
            root_password (str, optional): The password for the root user. Defaults to None.
        """
        self.runner = CommandRunner(
            host, user, port, password, keyfile,
            su_command, prompt_pattern, password_prompt,
            exit_command, timeout, encoding,
            os_type
        )
        self.root_password = root_password

    def connect(self):
        """
        Establishes an SSH connection and optionally switches to root user.

        Raises:
            paramiko.SSHException: If the SSH connection fails.
        """
        self.runner.connect()
        if self.root_password:
            self.runner.su(self.root_password)

    def remove_comment(self, text: str, comment: str = '#') -> list[str]:
        """
        Removes comments from a given text.

        Args:
            text (str): The text to remove comments from.
            comment (str, optional): The comment character. Defaults to '#'.

        Returns:
            list[str]: A list of lines with comments removed.
        """
        result = []
        for l in text.splitlines():
            stripped_l = l.strip()
            if not stripped_l or stripped_l.startswith(comment):
                continue

            comment_index = l.find(comment)
            if not comment_index == -1:
                l = l[:comment_index].rstrip()

            result.append(l)

        return result

    def remove_cstyle_comment(self, text: str) -> list[str]:
        """
        Removes C-style comments (// or /* */) from a given text.

        Args:
            text (str): The text to remove comments from.

        Returns:
            list[str]: A list of lines with comments removed.
        """
        is_comment_block = False
        result = []
        for l in text.splitlines():
            comment_start_index = l.find('/*')
            comment_end_index = l.find('*/')
            if comment_start_index != -1 and comment_end_index != -1:
                l = re.sub(r'/\*.*?\*/', '', l)
                if not l.strip():
                    continue

            elif comment_start_index != -1:
                is_comment_block = True
                continue

            elif comment_end_index != -1:
                is_comment_block = False
                continue

            if is_comment_block:
                continue

            stripped_l = l.strip()
            if not stripped_l or stripped_l.startswith('//'):
                continue

            comment_index = l.find('//')
            if not comment_index == -1:
                l = l[:comment_index].rstrip()

            result.append(l)

        return result

    def parse_ini_style(self, conf_text: str) -> dict[str, dict]:
        """
        Parses an INI-style configuration file.

        Args:
            conf_text (str): The text to parse.

        Returns:
            dict[str, dict]: A dictionary of sections and their key-value pairs.
        """
        lines = self.remove_comment(conf_text)
        result = {}
        section = None

        for line in lines:
            if re.match(r'^\[.+\]$', line.strip()):
                section = line.strip()[1:-1]
                result[section] = []
                continue

            if section:
                part = line.strip().split('=')
                if len(part) >= 2:
                    result[section].append({
                        'key': part[0].strip(),
                        'value': '='.join(part[1:]).strip()
                    })

        return result

    def parse_ini_style_nosection(self, conf_text: str) -> list[dict]:
        """
        Parses an INI-style configuration file without sections.

        Args:
            conf_text (str): The text to parse.

        Returns:
            list[dict]: A list of key-value pairs.
        """
        lines = self.remove_comment(conf_text)
        result = []
        for line in lines:
            part = line.strip().split('=')
            if len(part) >= 2:
                result.append({
                    'key': part[0].strip(),
                    'value': '='.join(part[1:]).strip()
                })

        return result

    def parse_unix_style(self, conf_text: str) -> list[dict]:
        """
        Parses a Unix-style configuration file.

        Args:
            conf_text (str): The text to parse.

        Returns:
            list[dict]: A list of key-value pairs.
        """
        lines = self.remove_comment(conf_text)
        result = []
        for line in lines:
            part = line.strip().split()
            key = part[0]
            if len(part) < 2:
                value = 'yes'
            else:
                value = ' '.join(part[1:]).strip()

            result.append({
                'key': key,
                'value': value
            })

        return result

    def save_to_json(self, file_path):
        pass

    def load_from_json(self, file_path):
        pass
