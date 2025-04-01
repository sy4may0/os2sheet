from libs.utils import CommandRunner, remove_comment
from libs.defines import NMCLI_TARGET_PROPS
import re

def selinux(runner: CommandRunner) -> dict[str, str]:
    result = {}
    selinux_config = runner.exec('cat /etc/selinux/config')

    for line in selinux_config.splitlines():
        if line.startswith('SELINUX='):
            result['SELINUX'] = line.split('=')[1]
        if line.startswith('SELINUXTYPE='):
            result['SELINUXTYPE'] = line.split('=')[1]

    return result

def sysconfig_grub(runner: CommandRunner) -> dict[str, str]:
    result = {}
    sysconfig_grub_config = runner.exec('cat /etc/sysconfig/grub')

    for line in sysconfig_grub_config.splitlines():
        if re.match(r'^[A-Z]+', line):
            sep = line.split('=')
            result[sep[0]] = sep[1]

    return result

def __read_nmcli_config(line):
    result_prop = None
    result_value = None
    for prop in NMCLI_TARGET_PROPS:
        if line.startswith(prop+':'):
            result_prop = prop
            result_value = ' '.join(line.split()[1:])
            break
    
    return result_prop, result_value

def nmcli(runner: CommandRunner) -> dict[str, dict]:
    result = {}
    nmcli_if_list = runner.exec('nmcli --colors no con show')

    for line in nmcli_if_list.splitlines():
        if re.match(r'.+\s+(ethernet|vlan|bond)\s+', line):
            conname = line.split()[0]
        else:
            continue
        
        result[conname] = {}
        nmcli_config = runner.exec(f'nmcli --colors no con show {conname}')

        for conf in nmcli_config.splitlines():
            prop, value = __read_nmcli_config(conf)
            if prop and value:
                result[conname][prop] = value

    return result

def localdisk(runner: CommandRunner) -> dict[str, dict]:
    result = {}
    localdisk_config = runner.exec('lsblk -o NAME,UUID,SIZE,TYPE,MOUNTPOINT')

    diskname = None
    for line in localdisk_config.splitlines():
        spl = line.split()

        if len(spl) > 2 and spl[2] == 'disk':
            diskname = spl[0]
            result[diskname] = {
                'name': diskname,
                'size': spl[1],
                'partition': [],
            }

        if not diskname:
            continue

        if len(spl) > 3 and spl[3] == 'part':
            name = re.findall('[a-z0-9A-Z]+', spl[0])[0]
            partition = {
                'name': name,
                'uuid': spl[1],
                'size': spl[2],
            }
            if len(spl) > 4:
                partition['mountpoint'] = spl[4]

            result[diskname]['partition'].append(partition)

    return result

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





            

    
