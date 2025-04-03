from libs.utils import CommandRunner
from libs.defines import NMCLI_TARGET_PROPS
from .gatherer_utils import remove_comment
import re

def selinux(runner: CommandRunner) -> dict[str, str]:
    """
    Gather SELinux settings from /etc/selinux/config.

    Args:
        runner: A CommandRunner instance.

    Returns:
        A dictionary with two keys:
            - SELINUX: The value of SELINUX in /etc/selinux/config.
            - SELINUXTYPE: The value of SELINUXTYPE in /etc/selinux/config.
    """
    selinux_settings = {}
    config_text = runner.exec('cat /etc/selinux/config')

    for line in config_text.splitlines():
        if line.startswith('SELINUX='):
            selinux_settings['SELINUX'] = line.split('=')[1].strip()
        elif line.startswith('SELINUXTYPE='):
            selinux_settings['SELINUXTYPE'] = line.split('=')[1].strip()

    return selinux_settings

def __parse_nmcli_line(line: str) -> tuple[str, str]:
    """Parses a line of nmcli output and returns a tuple of (property, value) or None if the line is not a valid property."""
    for prop in NMCLI_TARGET_PROPS:
        if line.startswith(f"{prop}:"):
            return prop, " ".join(line.split()[1:])
    return (None, None)

def nmcli(runner: CommandRunner) -> dict[str, dict]:
    """
    Gather network configuration from nmcli.

    Args:
        runner: A CommandRunner instance.

    Returns:
        A dictionary where each key is a network connection name and each value is a dictionary of network connection properties.
    """
    connections = {}
    nmcli_output = runner.exec('nmcli -t --colors no con show')

    for line in nmcli_output.splitlines():
        if re.match(r'.+:(.+ethernet|vlan|bond|bridge):', line):
            connection_name = line.split(':')[0]
            connections[connection_name] = {}

            connection_details = runner.exec(f'nmcli --colors no con show "{connection_name}"')
            for detail in connection_details.splitlines():
                prop, value = __parse_nmcli_line(detail)
                if prop and value:
                    connections[connection_name][prop] = value

    return connections

def __remove_lsblk_prefix(line: str) -> str:
    """Removes the prefix from a line of 'lsblk' output if it matches a specific pattern."""
    if re.match(r'[`|]-', line):
        return line[2:]
    else:
        return line

def localdisk(runner: CommandRunner) -> dict[str, dict]:
    """
    Gather information about local disks from lsblk.

    Args:
        runner: A CommandRunner instance.

    Returns:
        A dictionary where each key is a disk name and each value is a dictionary containing the disk's name, size, and a list of its partitions. Each partition is a dictionary with the partition's name, uuid, size, type, and mountpoint. If the partition is an LVM, it also contains a list of its volumes, each of which is a dictionary with the volume's name, uuid, size, type, and mountpoint.
    """
    disks = {}
    lsblk_output = runner.exec('lsblk -o NAME,UUID,SIZE,TYPE,MOUNTPOINT')

    current_disk = None
    current_part = None
    for line in lsblk_output.splitlines():
        columns = line.split()

        if len(columns) > 2 and columns[2] == 'disk':
            current_disk = __remove_lsblk_prefix(columns[0])
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
            partition_name = __remove_lsblk_prefix(columns[0])
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
            volume_name = __remove_lsblk_prefix(columns[0])
            volume_info = {
                'name': volume_name,
                'uuid': columns[1],
                'size': columns[2],
                'type': columns[3],
            }
            if len(columns) > 4:
                volume_info['mountpoint'] = columns[4]
            
            current_part['volumes'].append(volume_info)

    return disks

def default_target(runner: CommandRunner) -> str:
    """
    Get the default target of the given host.

    Args:
        runner: A CommandRunner instance.

    Returns:
        The name of the default target, or None if it cannot be determined.
    """
    output = runner.exec('systemctl get-default')
    for line in output.splitlines():
        if '.target' in line:
            return line.strip()
    return None

def timezone(runner: CommandRunner) -> str:
    """
    Get the timezone of the given host.

    Args:
        runner: A CommandRunner instance.

    Returns:
        The name of the timezone, or None if it cannot be determined.
    """
    output = runner.exec('timedatectl')
    for line in output.splitlines():
        if 'Time zone:' in line:
            return ' '.join(line.split()[2:])
    return None

def locale(runner: CommandRunner) -> str:
    """
    Get the locale of the given host.

    Args:
        runner: A CommandRunner instance.

    Returns:
        The name of the locale, or None if it cannot be determined.
    """
    output = runner.exec('localectl')
    for line in output.splitlines():
        if 'System Locale:' in line:
            return ' '.join(line.split()[2:])
    return None

def group(runner: CommandRunner) -> list[dict]:
    """
    Get a list of groups and their GIDs from the given host.

    Args:
        runner: A CommandRunner instance.

    Returns:
        A list of dictionaries, where each dictionary contains the keys 'name'
        and 'gid', which are the group name and GID, respectively.
    """
    group_config = runner.exec('cat /etc/group')
    groups = []
    for line in group_config.splitlines():
        if re.match('.+:.+:.+:', line):
            group_info = line.split(':')
            groups.append({
                'name': group_info[0],
                'gid': group_info[2],
            })

    return groups

def __get_user_subgroup(
    runner: CommandRunner, username: str, primary_group: str
) -> list[dict]:
    """Get the subgroups of a given user."""
    user_id_output = runner.exec(f'id {username}')
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

def __get_group_by_gid(runner: CommandRunner, group_id: str) -> dict[str, str]:
    """Get the group information from the given group ID."""
    group_info_output = runner.exec(f'getent group {group_id}')
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

def user(runner: CommandRunner) -> list[dict]:
    """
    Get a list of users and their properties from the given host.

    Args:
        runner: A CommandRunner instance.

    Returns:
        A list of dictionaries, where each dictionary contains the keys 'name',
        'uid', 'group', 'description', 'home_directory', 'shell', and 'groups'.
        The 'groups' key is a list of subgroups of the user, if any.
    """
    passwd_output = runner.exec('cat /etc/passwd')
    users = []
    for entry in passwd_output.splitlines():
        if re.match(r'.+:.+:.+:.+:.+:.+', entry):
            fields = entry.split(':')
            user_groups = __get_user_subgroup(runner, fields[0], fields[3])
            users.append({
                'name': fields[0],
                'uid': fields[2],
                'group': __get_group_by_gid(runner, fields[3]),
                'description': fields[4],
                'home_directory': fields[5],
                'shell': fields[6],
                'groups': user_groups,
            })

    return users

def systemd_units(runner: CommandRunner) -> list[dict]:
    """
    Retrieve the list of systemd unit files and their states from the given host.

    Args:
        runner: A CommandRunner instance to execute the command.

    Returns:
        A list of dictionaries, where each dictionary contains:
            - 'name': The name of the systemd unit.
            - 'state': The state of the systemd unit.
    """

    unit_status = runner.exec('systemctl list-unit-files')
    units = []
    for line in unit_status.splitlines():
        if not line.startswith('UNIT FILE'):
            fields = line.split()
            if len(fields) < 2:
                continue
            unit_name, unit_state = fields[0], fields[1]
            units.append({
                'name': unit_name,
                'state': unit_state,
            })

    return units

def rpm_packages(runner: CommandRunner) -> list[str]:
    """
    Retrieve a list of installed RPM packages on the host.

    Args:
        runner: A CommandRunner instance to execute the command.

    Returns:
        A list of strings, where each string is the name of an installed RPM package.
    """

    package_list = runner.exec('rpm -qa')
    packages = []
    for line in package_list.splitlines():
        packages.append(line.strip())

    return packages

def rhel_version(runner: CommandRunner) -> str:
    """
    Retrieve the version of RHEL installed on the host.

    Args:
        runner: A CommandRunner instance to execute the command.

    Returns:
        A string representing the version of RHEL installed on the host.
    """
    
    redhat_release = runner.exec('cat /etc/redhat-release')
    version = None
    for line in redhat_release.splitlines():
        version = line.strip()

    return version

def cpu(runner: CommandRunner) -> dict[str, str]:
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

    cpu_info = {}
    lscpu_output = runner.exec('LANG=C;lscpu')
    for line in lscpu_output.splitlines():
        fields = line.strip().split(':')
        if len(fields) != 2:
            continue
        key = fields[0].strip()
        value = fields[1].strip()
        if key in {'Model name', 'Thread(s) per core', 'Core(s) per socket', 'Socket(s)'}:
            cpu_info[key] = value

    return cpu_info

def mem(runner: CommandRunner) -> str:
    """
    Retrieve the total memory available on the host.

    Args:
        runner: A CommandRunner instance to execute the command.

    Returns:
        A string representing the total memory in kilobytes, followed by '[kb]'.
    """

    free_output = runner.exec('LANG=C;free')
    memory_info = None
    for line in free_output.splitlines():
        if line.startswith('Mem: '):
            memory_info = line.split()[1] + ' [kb]'

    return memory_info

def fstab(runner: CommandRunner) -> list[dict]:
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
    fstab_config = runner.exec('cat /etc/fstab')
    fstab_entries = []

    for line in remove_comment(fstab_config):
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

    return fstab_entries





            

    
