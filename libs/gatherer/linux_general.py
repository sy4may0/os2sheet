from libs.utils import CommandRunner
from libs.defines import NMCLI_TARGET_PROPS
from .gatherer_utils import remove_comment
import re

def selinux(runner: CommandRunner) -> dict[str, str]:
    selinux_settings = {}
    config_text = runner.exec('cat /etc/selinux/config')

    for line in config_text.splitlines():
        if line.startswith('SELINUX='):
            selinux_settings['SELINUX'] = line.split('=')[1].strip()
        elif line.startswith('SELINUXTYPE='):
            selinux_settings['SELINUXTYPE'] = line.split('=')[1].strip()

    return selinux_settings

def parse_nmcli_line(line: str) -> tuple[str, str]:
    """Parses a line of nmcli output and returns a tuple of (property, value) or None if the line is not a valid property."""
    for prop in NMCLI_TARGET_PROPS:
        if line.startswith(f"{prop}:"):
            return prop, " ".join(line.split()[1:])
    return (None, None)

def nmcli(runner: CommandRunner) -> dict[str, dict]:
    connections = {}
    nmcli_output = runner.exec('nmcli -t --colors no con show')

    for line in nmcli_output.splitlines():
        if re.match(r'.+:(.+ethernet|vlan|bond|bridge):', line):
            connection_name = line.split(':')[0]
            connections[connection_name] = {}

            connection_details = runner.exec(f'nmcli --colors no con show "{connection_name}"')
            for detail in connection_details.splitlines():
                prop, value = parse_nmcli_line(detail)
                if prop and value:
                    connections[connection_name][prop] = value

    return connections

def __remove_lsblk_prefix(line: str) -> str:
    if re.match(r'[`|]-', line):
        return line[2:]
    else:
        return line

def localdisk(runner: CommandRunner) -> dict[str, dict]:
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
    default_target_config = runner.exec('systemctl get-default')
    result = None
    for line in default_target_config.splitlines():
        if '.target' in line:
            result = line.strip()

    return result

def timezone(runner: CommandRunner) -> str:
    timezone_config = runner.exec('timedatectl')
    result = None
    for line in timezone_config.splitlines():
        if 'Time zone:' in line:
            result = ' '.join(line.split()[2:])

    return result

def locale(runner: CommandRunner) -> str:
    locale_config = runner.exec('localectl')
    result = None
    for line in locale_config.splitlines():
        if 'System Locale:' in line:
            result = ' '.join(line.split()[2:])

    return result

def group(runner: CommandRunner) -> list[dict]:
    group_config = runner.exec('cat /etc/group')
    result = []
    for line in group_config.splitlines():
        if re.match('.+:.+:.+:', line):
            spl = line.split(':')
            result.append({
                'name': spl[0],
                'gid': spl[2],
            })

    return result

def __get_user_subgroup(
    runner: CommandRunner, user: str, main_group: str
):
    id_data = runner.exec(f'id {user}')
    groups = []
    for line in id_data.splitlines():
        if 'groups=' in line:
            spl =  line.split()
            groups = spl[2].split('=')[1].split(',')

    results = []
    for group in groups:
        if not main_group in group:
            results.append({
                'gid': group.split('(')[0],
                'name': group.split('(')[1].rstrip(')')
            })

    return results

def __get_group_by_gid(
    runner: CommandRunner, gid: str
):
    id_data = runner.exec(f'getent group {gid}')
    result = {}
    for line in id_data.splitlines():
        if f':{gid}' in line:
            spl = line.split(':')
            result = {
                'gid': spl[2],
                'name': spl[0]
            }

    return result

def user(runner: CommandRunner) -> list[dict]:
    user_config = runner.exec('cat /etc/passwd')
    result = []
    for line in user_config.splitlines():
        if re.match('.+:.+:.+:.+:.+:.+', line):
            spl = line.split(':')
            groups = __get_user_subgroup(runner, spl[0], spl[3])
            result.append({
                'name': spl[0],
                'uid': spl[2],
                'group': __get_group_by_gid(runner, spl[3]),
                'descr': spl[4],
                'home': spl[5],
                'shell': spl[6],
                'groups': groups,
            })

    return result

def systemd_unit(runner: CommandRunner) -> list[dict]:
    systemd_config = runner.exec('systemctl list-unit-files | egrep -v "^UNIT FILE"')
    result = []
    for line in systemd_config.splitlines():
        if re.match('^.+\..+\s+', line):
            spl = line.split()
            result.append({
                'unit': spl[0],
                'state': spl[1],
            })

    return result

def rpm_pkgs(runner: CommandRunner) -> list[str]:
    rpm_packages = runner.exec('rpm -qa')
    result = []
    for line in rpm_packages.splitlines():
        result.append(line)

    return result

def rhel_version(runner: CommandRunner) -> str:
    rhel_version = runner.exec('cat /etc/redhat-release')
    result = None
    for line in rhel_version.splitlines():
        result = line

    return result

def cpu(runner: CommandRunner) -> dict[str, str]:
    lscpu = runner.exec('LANG=C;lscpu')
    result = {}
    for line in lscpu.splitlines():
        if line.strip().startswith('Model name:'):
            result['model'] = line.split(':')[1].strip()
        if line.strip().startswith('Thread(s) per core:'):
            result['thread'] = line.split(':')[1].strip()
        if line.strip().startswith('Core(s) per socket:'):
            result['core'] = line.split(':')[1].strip()
        if line.strip().startswith('Socket(s):'):
            result['socket'] = line.split(':')[1].strip()

    return result

def mem(runner: CommandRunner) -> str:
    free = runner.exec('LANG=C;free')
    result = None
    for line in free.splitlines():
        if line.startswith('Mem: '):
            result = line.split()[1] + '[kb]'

    return result

def fstab(runner: CommandRunner) -> list[dict]:
    fstab = runner.exec('cat /etc/fstab')
    result = []

    for line in remove_comment(fstab):
        spl = line.split()
        result.append({
            'device': spl[0],
            'mountpoint': spl[1],
            'filesystem': spl[2],
            'option': spl[3],
            'dump': spl[4],
            'fsck': spl[5]
        })

    return result





            

    
