from libs.gatherer.gatherer import Gatherer
from libs.defines import \
    CONF_ZABBIX_SERVER_CONF, \
    CONF_ZABBIX_AGENT_CONF, \
    CONF_ZABBIX_WEB_CONF


class ZabbixOSConfigGatherer(Gatherer):
    def __init__(
        self,
        host: str,
        user: str,
        port: int = 22,
        password: str = None,
        root_password: str = None,
        keyfile: str = None,
    ):
        """
        Initialize the ZabbixGatherer.

        Args:
            host: The host to connect to.
            user: The user to connect to.
            port: The port to connect to.
            password: The password to connect to.
            root_password: The root password to connect to.
            keyfile: The keyfile to connect to.
        """
        super().__init__(
            host,
            user,
            port,
            password,
            keyfile,
            root_password=root_password
        )
        self.server_config = None
        self.agent_config = None
        self.web_config = None
        self.usergroups = None
        self.users = None
        self.roles = None

    def __search_include_files(self, include_path: str) -> list[str]:
        if include_path.endswith('/'):
            cmd = f'find {include_path} -maxdepth 1 -type f'
        else:
            part = include_path.split('/')
            filepart = part.pop()
            dirpart = '/'.join(part)
            cmd = f"find {dirpart} -maxdepth 1 -type f -name '{filepart}'"

        files_text = self.runner.exec(cmd)
        files = files_text.splitlines()

        return files

    def __read_zabbix_config(self, config_file: str):
        result = {}

        conf_text = self.runner.exec(
            f'cat {config_file}'
        )
        result[config_file] = self.parse_ini_style_nosection(
            conf_text
        )

        include_files = []
        for _v in result[config_file]:
            if _v['key'] == 'Include':
                include_files.extend(
                    self.__search_include_files(_v['value'])
                )

        for include_file in include_files:
            conf_text = self.runner.exec(
                f'cat {include_file}'
            )
            result[include_file] = self.parse_ini_style_nosection(conf_text)

        return result

    def get_server_config(self):
        """
        Get the server configuration.

        Returns:
            dict: The server configuration.
        """
        if self.server_config:
            return self.server_config

        self.server_config = self.__read_zabbix_config(CONF_ZABBIX_SERVER_CONF)
        return self.server_config

    def get_agent_config(self):
        """
        Get the agent configuration.

        Returns:
            dict: The agent configuration.
        """
        if self.agent_config:
            return self.agent_config

        self.agent_config = self.__read_zabbix_config(CONF_ZABBIX_AGENT_CONF)
        return self.agent_config

    def get_web_config(self):
        """
        Get the web configuration.

        Returns:
            dict: The web configuration.
        """
        if self.web_config:
            return self.web_config

        result = []

        web_config_text = self.runner.exec(
            f'cat {CONF_ZABBIX_WEB_CONF}'
        )

        web_config_lines = self.remove_cstyle_comment(web_config_text)
        for line in web_config_lines:
            if not line.strip().startswith('$'):
                continue

            key, value = line.strip().split('=', 1)

            result.append(
                {
                    'key': key.strip(),
                    'value': value.strip()
                }
            )
        self.web_config = result

        return self.web_config
