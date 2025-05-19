import json
from libs.defines import NMCLI_TARGET_PROPS, \
    RSYSLOG_CONF_FILE, RSYSLOG_CONF_D, \
    SSHD_CONF_FILE, SSHD_CONF_D
from libs.defines import CRON_CONF_D, LOGROTATE_CONF_D, LOGROTATE_CONF_FILE, USER_CRON_CONF_D
from libs.defines.linux_props import CHRONY_CONF_FILE, DNF_CONF_FILE, DNF_REPO_D, DNF_REPO_EXCLUSION, SUDOERS_CONF, SUDOERS_CONF_D, SYSCTL_CONF, SYSCTL_CONF_D
from libs.defines import AUTHSELECT_TARGET, AUTHSELECT_PATH
from .gatherer import Gatherer
import re


class LinuxOSGatherer(Gatherer):
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
        Initializes the LinuxGeneralGatherer instance.

        Args:
            host (str): The hostname or IP address of the target server.
            user (str): The username for SSH authentication.
            port (int, optional): The port for SSH connection. Defaults to 22.
            password (str, optional): The password for SSH authentication. Defaults to None.
            root_password (str, optional): The password for the root user. Defaults to None.
            keyfile (str, optional): The path to the private key file for key-based authentication. Defaults to None.
        """
        super().__init__(
            host, user, port, password,
            keyfile, root_password=root_password)

        self.hostname = None
        self.domainname = None
        self.selinux = None
        self.nmcli_connections = None
        self.localdisks = None
        self.default_target = None
        self.timezone = None
        self.locale = None
        self.groups = None
        self.users = None
        self.systemd_units = None
        self.rpm_packages = None
        self.rhel_version = None
        self.cpu = None
        self.mem = None
        self.fstab = None
        self.rsyslog = None
        self.sshd = None
        self.logrotate = None
        self.cron = None
        self.chrony = None
        self.dnf = None
        self.dnf_repo = None
        self.sudoers = None
        self.firewalld = None
        self.sysconfig_grub = None
        self.sysctl = None

    def get_hostname(self) -> str:
        """
        Get the hostname.

        Returns:
            The hostname.
        """
        if self.hostname:
            return self.hostname

        hostname = self.runner.exec('hostname')
        self.hostname = hostname

        return self.hostname

    def get_domainname(self) -> str:
        """
        Get the domain name.

        Returns:
            The domain name.
        """
        if self.domainname:
            return self.domainname

        domainname = self.runner.exec('domainname')
        self.domainname = domainname

        return self.domainname

    def get_selinux(self) -> dict[str, str]:
        """
        Gather SELinux settings from /etc/selinux/config.

        Args:
            runner: A CommandRunner instance.

        Returns:
            A dictionary with two keys:
                - SELINUX: The value of SELINUX in /etc/selinux/config.
                - SELINUXTYPE: The value of SELINUXTYPE in /etc/selinux/config.
        """
        if self.selinux:
            return self.selinux

        selinux_settings = {}
        config_text = self.runner.exec('cat /etc/selinux/config')

        for line in config_text.splitlines():
            if line.startswith('SELINUX='):
                selinux_settings['SELINUX'] = line.split('=')[1].strip()
            elif line.startswith('SELINUXTYPE='):
                selinux_settings['SELINUXTYPE'] = line.split('=')[1].strip()

        self.selinux = selinux_settings
        return self.selinux

    def __parse_nmcli_line(self, line: str) -> tuple[str, str]:
        """Parses a line of nmcli output and returns a tuple of (property, value) or None if the line is not a valid property."""
        for prop in NMCLI_TARGET_PROPS:
            if line.startswith(f"{prop}:"):
                return prop, " ".join(line.split()[1:])
        return (None, None)

    def get_nmcli_connections(self) -> dict[str, dict]:
        """
        Gather network configuration from nmcli.

        Args:
            runner: A CommandRunner instance.

        Returns:
            A dictionary where each key is a network connection name and each value is a dictionary of network connection properties.
        """
        if self.nmcli_connections:
            return self.nmcli_connections

        connections = {}
        nmcli_output = self.runner.exec('nmcli -t --colors no con show')

        for line in nmcli_output.splitlines():
            if re.match(r'.+:(.+ethernet|vlan|bond|bridge):', line):
                connection_name = line.split(':')[0]
                connections[connection_name] = {}

                connection_details = self.runner.exec(
                    f'nmcli --colors no con show "{connection_name}"')
                for detail in connection_details.splitlines():
                    prop, value = self.__parse_nmcli_line(detail)
                    if prop and value:
                        connections[connection_name][prop] = value

        self.nmcli_connections = connections
        return self.nmcli_connections

    def __remove_lsblk_prefix(self, line: str) -> str:
        """Removes the prefix from a line of 'lsblk' output if it matches a specific pattern."""
        if re.match(r'[`|]-', line):
            return line[2:]
        else:
            return line

    def get_localdisks(self) -> dict[str, dict]:
        """
        Gather information about local disks from lsblk.

        Args:
            runner: A CommandRunner instance.

        Returns:
            A dictionary where each key is a disk name and each value is a dictionary containing the disk's name, size, and a list of its partitions. Each partition is a dictionary with the partition's name, uuid, size, type, and mountpoint. If the partition is an LVM, it also contains a list of its volumes, each of which is a dictionary with the volume's name, uuid, size, type, and mountpoint.
        """
        if self.localdisks:
            return self.localdisks

        disks = {}
        lsblk_output = self.runner.exec(
            'lsblk -o NAME,UUID,SIZE,TYPE,MOUNTPOINT')

        current_disk = None
        current_part = None
        for line in lsblk_output.splitlines():
            columns = line.split()

            if len(columns) > 2 and columns[2] == 'disk':
                current_disk = self.__remove_lsblk_prefix(columns[0])
                disks[current_disk] = {
                    'name': current_disk,
                    'size': columns[1],
                    'partition': [],
                }

            if not current_disk:
                continue

            target_types = ['part']
            if not len(columns) > 3:
                continue
            if columns[3] in target_types:
                partition_name = self.__remove_lsblk_prefix(columns[0])
                partition_info = {
                    'name': partition_name,
                    'uuid': columns[1],
                    'size': columns[2],
                    'type': columns[3],
                    'volumes': []
                }
                if len(columns) > 4:
                    partition_info['mountpoint'] = columns[4]

                disks[current_disk]['partition'].append(partition_info)
                current_part = partition_info

            target_lvm_types = ['lvm', 'lvm2', 'crypt']
            if current_part and columns[3] in target_lvm_types:
                volume_name = self.__remove_lsblk_prefix(columns[0])
                volume_info = {
                    'name': volume_name,
                    'uuid': columns[1],
                    'size': columns[2],
                    'type': columns[3],
                }
                if len(columns) > 4:
                    volume_info['mountpoint'] = columns[4]

                current_part['volumes'].append(volume_info)

        self.localdisks = disks
        return self.localdisks

    def get_default_target(self) -> str:
        """
        Get the default target of the given host.

        Args:
            runner: A CommandRunner instance.

        Returns:
            The name of the default target, or None if it cannot be determined.
        """
        if self.default_target:
            return self.default_target

        output = self.runner.exec('systemctl get-default')
        for line in output.splitlines():
            if '.target' in line:
                self.default_target = line.strip()
                return self.default_target
        return None

    def get_timezone(self) -> str:
        """
        Get the timezone of the given host.

        Args:
            runner: A CommandRunner instance.

        Returns:
            The name of the timezone, or None if it cannot be determined.
        """
        if self.timezone:
            return self.timezone
        output = self.runner.exec('timedatectl')
        for line in output.splitlines():
            if 'Time zone:' in line:
                self.timezone = ' '.join(line.split()[2:])
                return self.timezone
        return None

    def get_locale(self) -> str:
        """
        Get the locale of the given host.

        Args:
            runner: A CommandRunner instance.

        Returns:
            The name of the locale, or None if it cannot be determined.
        """
        if self.locale:
            return self.locale

        output = self.runner.exec('localectl')
        for line in output.splitlines():
            if 'System Locale:' in line:
                self.locale = ' '.join(line.split()[2:])
                return self.locale
        return None

    def get_groups(self) -> list[dict]:
        """
        Get a list of groups and their GIDs from the given host.

        Args:
            runner: A CommandRunner instance.

        Returns:
            A list of dictionaries, where each dictionary contains the keys 'name'
            and 'gid', which are the group name and GID, respectively.
        """
        if self.groups:
            return self.groups

        group_config = self.runner.exec('cat /etc/group')
        groups = []
        for line in group_config.splitlines():
            if re.match('.+:.+:.+:', line):
                group_info = line.split(':')
                groups.append({
                    'name': group_info[0],
                    'gid': group_info[2],
                })

        self.groups = groups
        return self.groups

    def __get_user_subgroup(
        self, username: str, primary_group: str
    ) -> list[dict]:
        """Get the subgroups of a given user."""
        user_id_output = self.runner.exec(f'id {username}')
        group_entries = []

        for line in user_id_output.splitlines():
            if 'groups=' in line:
                group_entries = line.split()[2].split('=')[1].split(',')

        subgroups = []
        for entry in group_entries:
            if primary_group not in entry:
                gid, name = entry.split('(')
                subgroups.append({
                    'gid': gid,
                    'name': name.rstrip(')')
                })

        return subgroups

    def __get_group_by_gid(self, group_id: str) -> dict[str, str]:
        """Get the group information from the given group ID."""
        group_info_output = self.runner.exec(f'getent group {group_id}')
        group_info = {}
        for line in group_info_output.splitlines():
            if f':{group_id}' in line:
                group_fields = line.split(':')
                group_info = {
                    'gid': group_fields[2],
                    'name': group_fields[0],
                }
                break

        return group_info

    def get_users(self) -> list[dict]:
        """
        Get a list of users and their properties from the given host.

        Args:
            runner: A CommandRunner instance.

        Returns:
            A list of dictionaries, where each dictionary contains the keys 'name',
            'uid', 'group', 'description', 'home_directory', 'shell', and 'groups'.
            The 'groups' key is a list of subgroups of the user, if any.
        """
        if self.users:
            return self.users

        passwd_output = self.runner.exec('cat /etc/passwd')
        users = []
        for entry in passwd_output.splitlines():
            if re.match(r'.+:.+:.+:.+:.+:.+', entry):
                fields = entry.split(':')
                user_groups = self.__get_user_subgroup(fields[0], fields[3])
                users.append({
                    'name': fields[0],
                    'uid': fields[2],
                    'group': self.__get_group_by_gid(fields[3]),
                    'description': fields[4],
                    'home_directory': fields[5],
                    'shell': fields[6],
                    'groups': user_groups,
                })

        self.users = users
        return self.users

    def get_systemd_units(self) -> list[dict]:
        """
        Retrieve the list of systemd unit files and their states from the given host.

        Args:
            runner: A CommandRunner instance to execute the command.

        Returns:
            A list of dictionaries, where each dictionary contains:
                - 'name': The name of the systemd unit.
                - 'state': The state of the systemd unit.
        """
        if self.systemd_units:
            return self.systemd_units
        unit_status = self.runner.exec('systemctl list-unit-files')
        units = []
        for line in unit_status.splitlines():
            if not line.startswith('UNIT FILE'):
                if 'unit files listed' in line:
                    break
                fields = line.split()
                if len(fields) < 2:
                    continue
                unit_name, unit_state = fields[0], fields[1]
                units.append({
                    'name': unit_name,
                    'state': unit_state,
                })

        self.systemd_units = units
        return self.systemd_units

    def get_rpm_packages(self) -> dict[str, list]:
        """
        Retrieve a list of installed RPM packages on the host.

        Args:
            runner: A CommandRunner instance to execute the command.

        Returns:
            A list of strings, where each string is the name of an installed RPM package.
        """
        if self.rpm_packages:
            return self.rpm_packages

        package_list = self.runner.exec('dnf list installed')
        packages = {}
        for line in package_list.splitlines():
            if len(line.split()) < 3:
                continue
            package, version, source = line.split()[:3]
            if source not in packages.keys():
                packages[source] = []
            packages[source].append({
                'name': package,
                'version': version
            })

        self.rpm_packages = packages
        return self.rpm_packages

    def get_rhel_version(self) -> str:
        """
        Retrieve the version of RHEL installed on the host.

        Args:
            runner: A CommandRunner instance to execute the command.

        Returns:
            A string representing the version of RHEL installed on the host.
        """
        if self.rhel_version:
            return self.rhel_version
        redhat_release = self.runner.exec('cat /etc/redhat-release')
        version = None
        for line in redhat_release.splitlines():
            version = line.strip()

        self.rhel_version = version
        return self.rhel_version

    def get_cpu(self) -> dict[str, str]:
        """
        Retrieve CPU information from the host.

        Args:
            runner: A CommandRunner instance to execute the command.

        Returns:
            A dictionary with the following CPU details:
                - 'Model name': The name of the CPU model.
                - 'Thread(s) per core': The number of threads per core.
                - 'Core(s) per socket': The number of cores per socket.
                - 'Socket(s)': The number of sockets.
        """
        if self.cpu:
            return self.cpu

        cpu_info = {}
        lscpu_output = self.runner.exec('LANG=C;lscpu')
        for line in lscpu_output.splitlines():
            fields = line.strip().split(':')
            if len(fields) != 2:
                continue
            key = fields[0].strip()
            value = fields[1].strip()
            if key in {'Model name', 'Thread(s) per core', 'Core(s) per socket', 'Socket(s)'}:
                cpu_info[key] = value

        self.cpu = cpu_info
        return self.cpu

    def get_mem(self) -> str:
        """
        Retrieve the total memory available on the host.

        Args:
            runner: A CommandRunner instance to execute the command.

        Returns:
            A string representing the total memory in kilobytes, followed by '[kb]'.
        """
        if self.mem:
            return self.mem

        free_output = self.runner.exec('LANG=C;free')
        memory_info = None
        for line in free_output.splitlines():
            if line.startswith('Mem: '):
                memory_info = line.split()[1] + ' [kb]'

        self.mem = memory_info
        return self.mem

    def get_fstab(self) -> list[dict]:
        """
        Retrieve the list of mounted filesystems from the host's /etc/fstab.

        Args:
            runner: A CommandRunner instance to execute the command.

        Returns:
            A list of dictionaries, each containing the following information about a mounted filesystem:
                - 'device': The device name of the filesystem.
                - 'mountpoint': The path where the filesystem is mounted.
                - 'filesystem': The type of the filesystem.
                - 'options': The mount options for the filesystem.
                - 'dump': Whether the filesystem should be dumped.
                - 'fsck': The fsck pass for the filesystem.
        """
        if self.fstab:
            return self.fstab

        fstab_config = self.runner.exec('cat /etc/fstab')
        fstab_entries = []

        for line in self.remove_comment(fstab_config):
            fields = line.split()
            if len(fields) < 6:
                continue

            fstab_entry = {
                'device': fields[0],
                'mountpoint': fields[1],
                'filesystem': fields[2],
                'options': fields[3],
                'dump': fields[4],
                'fsck': fields[5],
            }
            fstab_entries.append(fstab_entry)

        self.fstab = fstab_entries
        return self.fstab

    def get_rsyslog(self):
        """
        Retrieve the contents of the rsyslog configuration files.

        Returns:
            A dictionary with the path of each rsyslog configuration file as the key and the contents of the file as the value.
            The contents of the file are processed to remove comments.
        """
        if self.rsyslog:
            return self.rsyslog

        rsyslog = {}
        target_file_list = [RSYSLOG_CONF_FILE]
        rsyslog_conf_d = self.runner.exec(f'find {RSYSLOG_CONF_D}')
        for line in rsyslog_conf_d.splitlines():
            if line.startswith('/etc') and re.match(r'.+\.conf$', line):
                target_file_list.append(line.strip())

        for conf_file_path in target_file_list:
            conf_text = self.runner.exec(f'cat {conf_file_path}')
            rsyslog[conf_file_path] = self.remove_comment(conf_text)

        self.rsyslog = rsyslog
        return self.rsyslog

    def get_sshd(self) -> dict[str, list]:
        """
        Retrieve the contents of the SSHD configuration files.

        Returns:
            A dictionary with the path of each SSHD configuration file as the key and a list of dictionaries as the value.
            Each dictionary in the list represents a configuration option in the file, with keys 'key' and 'value'.
        """
        if self.sshd:
            return self.sshd

        sshd = {}
        target_file_list = [SSHD_CONF_FILE]
        sshd_conf_d = self.runner.exec(f'find {SSHD_CONF_D}')
        for line in sshd_conf_d.splitlines():
            if line.startswith('/etc') and re.match(r'.+\.conf$', line):
                target_file_list.append(line.strip())

        for conf_file_path in target_file_list:
            conf_text = self.runner.exec(f'cat {conf_file_path}')
            sshd[conf_file_path] = self.parse_unix_style(conf_text)

        self.sshd = sshd

        return self.sshd

    def __parse_logrotate_config(self, text: str):
        lines = self.remove_comment(text)
        if not lines:
            return {
                'target': [],
                'config': ''
            }
        files = []
        for line in lines:
            if re.match(r'^/\S+', line):
                files.append(line.replace('{', '').strip())
        config_block = re.findall(r'\{((.|\s)*)\}', '\n'.join(lines))
        fixed_config = self.remove_comment(
            ' '.join(config_block[0]).replace('\t', '    '))

        return {
            'target': files,
            'config': fixed_config
        }

    def get_logrotate(self) -> dict[str, dict]:
        """
        Retrieve the contents of the logrotate configuration files.

        Returns:
            A dictionary with the path of each logrotate configuration file as the key and a dictionary as the value.
            The dictionary contains the keys 'target' and 'config'.
            The 'target' key is a list of target files.
            The 'config' key is a string of the logrotate configuration.
        """
        if self.logrotate:
            return self.logrotate

        result = {}
        target_file_list = self.runner.exec(
            f'find {LOGROTATE_CONF_D} | egrep -v "{LOGROTATE_CONF_D}$"')
        conf_text = self.runner.exec(f'cat {LOGROTATE_CONF_FILE}')

        result[LOGROTATE_CONF_FILE] = {
            'target': ['default'],
            'config': self.remove_comment(conf_text)
        }

        for conf_file_path in target_file_list.splitlines():
            conf_text = self.runner.exec(f'cat {conf_file_path}')
            result[conf_file_path] = self.__parse_logrotate_config(conf_text)

        self.logrotate = result
        return self.logrotate

    def __parse_cron_config(self, text: str):
        lines = self.remove_comment(text)
        result = {
            'environment': [],
            'job': []
        }
        for line in lines:
            if re.match(r'^\S+=\S+', line):
                part = line.split('=')
                result['environment'].append({
                    'env': part[0],
                    'value': part[1]
                })

            if re.match(r'([0-9\*\/\-,]+\s+){4}', line):
                part = line.split()
                result['job'].append({
                    'schedule': ' '.join(part[0:5]),
                    'command': ' '.join(part[5:])
                })

        return result

    def get_cron(self):
        """
        Retrieve the contents of the cron configuration files.

        Returns:
            A dictionary with the path of each cron configuration file as the key and a dictionary as the value.
            The dictionary contains the keys 'environment' and 'job'.
        """
        if self.cron:
            return self.cron
        result = {}
        cron_conf_d = self.runner.exec(
            f'find {CRON_CONF_D} | egrep -v "{CRON_CONF_D}$"')
        user_cron_conf_d = self.runner.exec(
            f'find {USER_CRON_CONF_D} | egrep -v "{USER_CRON_CONF_D}$"')

        target_file_list = []
        target_file_list.extend(cron_conf_d.splitlines())
        target_file_list.extend(user_cron_conf_d.splitlines())

        for conf_path in target_file_list:
            conf_text = self.runner.exec(f'cat {conf_path}')
            result[conf_path] = self.__parse_cron_config(conf_text)

        self.cron = result
        return self.cron

    def get_chrony(self):
        """
        Retrieve the contents of the chrony configuration files.

        Returns:
            A dictionary with the path of each chrony configuration file as the key and a dictionary as the value.
            The dictionary contains the keys 'key' and 'value'.
        """
        if self.chrony:
            return self.chrony

        conf_text = self.runner.exec(f'cat {CHRONY_CONF_FILE}')
        result = self.parse_unix_style(conf_text)

        self.chrony = result
        return self.chrony

    def get_dnf(self) -> dict[str, dict]:
        """
        Retrieve the contents of the dnf configuration files.

        Returns:
            A dictionary with the path of each dnf configuration file as the key and a dictionary as the value.
            The dictionary contains the keys 'key' and 'value'.
        """
        if self.dnf:
            return self.dnf

        conf_text = self.runner.exec(f'cat {DNF_CONF_FILE}')

        self.dnf = self.parse_ini_style(conf_text)
        return self.dnf

    def get_dnf_repo(self) -> dict[str, dict]:
        """
        Retrieve the contents of the dnf repository configuration files.

        Returns:
            A dictionary with the path of each dnf repository configuration file as the key and a dictionary as the value.
            The dictionary contains the keys 'key' and 'value'.
        """
        if self.dnf_repo:
            return self.dnf_repo

        result = {}
        target_files = self.runner.exec(
            f'find {DNF_REPO_D} | egrep -v "{DNF_REPO_D}$"')
        for conf_file_path in target_files.splitlines():
            if (
                conf_file_path.split('/')[-1] in DNF_REPO_EXCLUSION or
                not conf_file_path.endswith('.repo')
            ):
                continue

            conf_text = self.runner.exec(f'cat {conf_file_path}')
            result[conf_file_path] = self.parse_ini_style(conf_text)

        self.dnf_repo = result
        return self.dnf_repo

    def __remove_comment_sudoers(self, text: str) -> list[str]:
        result = []
        for l in text.splitlines():
            stripped_l = l.strip()
            if not stripped_l or re.match('^#+($|\s)', stripped_l):
                continue

            result.append(l.replace('\t', '    '))

        return result

    def get_sudoers(self) -> dict[str, list[dict]]:
        """
        Retrieve the contents of the sudoers configuration files.

        Returns:
            A dictionary with the path of each sudoers configuration file as the key and a list of dictionaries as the value.
            Each dictionary in the list represents a configuration option in the file.
        """
        if self.sudoers:
            return self.sudoers

        result = {}
        target_files = [SUDOERS_CONF]
        sudoers_conf_d = self.runner.exec(
            f'find {SUDOERS_CONF_D} | egrep -v "{SUDOERS_CONF_D}$"'
        )
        for line in sudoers_conf_d.splitlines():
            target_files.append(line)

        for conf_path in target_files:
            conf_text = self.runner.exec(f'cat {conf_path}')
            result[conf_path] = self.__remove_comment_sudoers(conf_text)

        self.sudoers = result
        return self.sudoers

    def __firewalld_get_interfaces(self, zone: str) -> list:
        interfaces = []

        interfaces_text = self.runner.exec(
            f"firewall-cmd --zone={zone} --list-interfaces"
        )

        for line in interfaces_text.splitlines():
            interfaces.extend(line.strip().split())

        return interfaces

    def __firewalld_get_services(self, zone: str) -> list:
        services = []

        services_text = self.runner.exec(
            f"firewall-cmd --zone={zone} --list-services"
        )

        for line in services_text.splitlines():
            services.extend(line.strip().split())

        return services

    def __firewalld_get_rich_rules(self, zone: str) -> list:
        rich_rules = []

        rich_rule_text = self.runner.exec(
            f'firewall-cmd --zone={zone} --list-rich-rules'
        )
        for line in rich_rule_text.splitlines():
            if re.match('^rule', line.strip()):
                rich_rules.append(line.strip())

        return rich_rules

    def get_firewalld(self) -> dict[str, dict]:
        """
        Retrieve the contents of the firewalld configuration files.

        Returns:
            A dictionary with the path of each firewalld configuration file as the key and a dictionary as the value.
            The dictionary contains the keys 'interfaces', 'services', and 'rich_rules'.
        """
        if self.firewalld:
            return self.firewalld

        result = {}
        active_zone_text = self.runner.exec('firewall-cmd --get-active-zones')

        for line in active_zone_text.splitlines():
            if not re.match('^\S+', line):
                continue

            zone = line.strip()

            interfaces = self.__firewalld_get_interfaces(zone)
            services = self.__firewalld_get_services(zone)
            rich_rules = self.__firewalld_get_rich_rules(zone)

            result[zone] = {
                'interfaces': interfaces,
                'services': services,
                'rich_rules': rich_rules
            }

        self.firewalld = result
        return self.firewalld

    def get_sysconfig_grub(self) -> dict[str, str]:
        """
        Retrieve the contents of the sysconfig/grub configuration file.

        Returns:
            A dictionary with the path of the sysconfig/grub configuration file as the key and a string as the value.
        """
        if self.sysconfig_grub:
            return self.sysconfig_grub

        sysconfig_grub_config = self.runner.exec('cat /etc/sysconfig/grub')

        self.sysconfig_grub = self.parse_ini_style_nosection(
            sysconfig_grub_config)
        return self.sysconfig_grub

    def get_sysctl(self) -> dict[str, list]:
        """
        Retrieve the contents of the sysctl configuration files.

        Returns:
            A dictionary with the path of each sysctl configuration file as the key and a list of dictionaries as the value.
            Each dictionary in the list represents a configuration option in the file.
        """
        if self.sysctl:
            return self.sysctl

        result = {}
        target_files = [SYSCTL_CONF]
        sysctl_conf_d = self.runner.exec(
            f'find {SYSCTL_CONF_D} | egrep -v "{SYSCTL_CONF_D}$"'
        )
        for _f in sysctl_conf_d.splitlines():
            target_files.append(_f)

        for sysctl_conf in target_files:
            conf_text = self.runner.exec(f'cat {sysctl_conf}')
            result[sysctl_conf] = self.parse_unix_style(conf_text)

        self.sysctl = result
        return self.sysctl

    def __parse_pam_conf(self, text: str) -> dict[str, list]:
        module_types = []
        controls = []
        modules = []
        arguments = []
        conditions = []
        remarks = []

        lines = text.splitlines()
        for line in lines:
            if re.match(r'^\{.*\}$', line.strip()):
                remarks.append('')
                conditions.append(line.strip())
                modules.append('')
                arguments.append('')
                controls.append('')
                module_types.append('')
                continue

            if not re.match(r'^(\S+)\s+(\S+|\[.+\])\s+(\S+)($|.+)', line):
                continue

            con_match = re.match(r'^.+({.+}?)$', line)
            if con_match:
                conditions.append(con_match.groups()[0].strip())
                line = re.sub(r'\{[^{}]*\}$', '', line, 1)
            else:
                conditions.append('')

            mod_match = re.match(r'^(\S+)\s+(\[.+\]|\S+)\s+(\S+)($|.+)', line)
            if mod_match:
                module_types.append(mod_match.groups()[0].strip())
                controls.append(mod_match.groups()[1].strip())
                modules.append(mod_match.groups()[2].strip())
                if len(mod_match.groups()) > 3:
                    arguments.append(mod_match.groups()[3].strip())
                else:
                    arguments.append('')
                remarks.append('')

        return {
            'module_types': module_types,
            'controls': controls,
            'modules': modules,
            'arguments': arguments,
            'conditions': conditions,
            'remarks': remarks
        }

    def get_pam(self) -> dict[str, list]:
        """
        Retrieve the contents of the pam configuration files.

        Returns:
            A dictionary with the path of each pam configuration file as the key and a list of dictionaries as the value.
            Each dictionary in the list represents a configuration option in the file.
        """
        authselect = self.runner.exec('authselect current')

        profile = None
        features = []
        custom_prof = {}

        for line in authselect.splitlines():
            prof_match = re.match('^Profile ID: (\S+)$', line)
            if prof_match:
                profile = prof_match.groups()[0]

            if line == 'Enabled features: None':
                break

            fe_match = re.match('^- (\S+)$', line)
            if fe_match:
                features.append(fe_match.groups()[0])

        for target in AUTHSELECT_TARGET:
            path = f'{AUTHSELECT_PATH}{profile}/{target}'

            pam_conf = self.runner.exec(f'cat {path}')

            if pam_conf:
                custom_prof[path] = self.__parse_pam_conf(pam_conf)

        return {
            'profile': profile,
            'features': features,
            'prof_pam_conf': custom_prof
        }

    def save_to_json(self, file_path):
        """
        Save the gathered data to a JSON file.

        Args:
            file_path (str): The path to the JSON file to save the data to.
        """
        data = {
            'hostname': self.get_hostname(),
            'domainname': self.get_domainname(),
            'selinux': self.get_selinux(),
            'nmcli': self.get_nmcli_connections(),
            'localdisks': self.get_localdisks(),
            'fstab': self.get_fstab(),
            'rsyslog': self.get_rsyslog(),
            'sshd': self.get_sshd(),
            'logrotate': self.get_logrotate(),
            'cron': self.get_cron(),
            'chrony': self.get_chrony(),
            'dnf': self.get_dnf(),
            'dnf_repo': self.get_dnf_repo(),
            'sudoers': self.get_sudoers(),
            'firewalld': self.get_firewalld(),
            'sysconfig_grub': self.get_sysconfig_grub(),
            'sysctl': self.get_sysctl(),
            'pam': self.get_pam()
        }

        with open(file_path, 'w') as f:
            json.dump(data, f)

    def load_from_json(self, file_path):
        """
        Load the gathered data from a JSON file.

        Args:
            file_path (str): The path to the JSON file to load the data from.
        """
        with open(file_path, 'r') as f:
            data = json.load(f)

        self.hostname = data.get('hostname')
        self.domainname = data.get('domainname')
        self.selinux = data.get('selinux')
        self.nmcli = data.get('nmcli')
        self.localdisks = data.get('localdisks')
        self.fstab = data.get('fstab')
        self.rsyslog = data.get('rsyslog')
        self.sshd = data.get('sshd')
        self.logrotate = data.get('logrotate')
        self.cron = data.get('cron')
        self.chrony = data.get('chrony')
        self.dnf = data.get('dnf')
        self.dnf_repo = data.get('dnf_repo')
        self.sudoers = data.get('sudoers')
        self.firewalld = data.get('firewalld')
        self.sysconfig_grub = data.get('sysconfig_grub')
        self.sysctl = data.get('sysctl')
        self.pam = data.get('pam')
