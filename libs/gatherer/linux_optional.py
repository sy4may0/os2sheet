from libs.utils import CommandRunner
from libs.defines import \
    RSYSLOG_CONF_FILE, RSYSLOG_CONF_D, \
    SSHD_CONF_FILE, SSHD_CONF_D, \
    LOGROTATE_CONF_FILE, LOGROTATE_CONF_D, \
    CRON_CONF_D, USER_CRON_CONF_D, \
    CHRONY_CONF_FILE, \
    DNF_CONF_FILE, \
    DNF_REPO_D, DNF_REPO_EXCLUSION, \
    SUDOERS_CONF, SUDOERS_CONF_D
from .gatherer_utils import \
    remove_comment
import re
import configparser

def rsyslog(runner: CommandRunner) -> dict[str, list]:
    result = {}
    target_file_list = [RSYSLOG_CONF_FILE]
    rsyslog_conf_d = runner.exec(f'find {RSYSLOG_CONF_D}')
    for line in rsyslog_conf_d.splitlines():
        if line.startswith('/etc') and re.match(r'.+\.conf$', line):
            target_file_list.append(line.strip())

    for conf_file_path in target_file_list:
        conf_text = runner.exec(f'cat {conf_file_path}')
        result[conf_file_path] = remove_comment(conf_text)

    return result

def __parse_sshd_config(text: str) -> list:
    result = []
    fixed_text_lines = remove_comment(text)
    for line in fixed_text_lines:
        spl = line.split()
        result.append({
            'key': spl[0],
            'value': ' '.join(spl[1:])
        })

    return result

def sshd(runner: CommandRunner) -> dict[str, list]:
    result = {}
    target_file_list = [SSHD_CONF_FILE]
    sshd_conf_d = runner.exec(f'find {SSHD_CONF_D}')
    for line in sshd_conf_d.splitlines():
        if line.startswith('/etc') and re.match(r'.+\.conf$', line):
            target_file_list.append(line.strip())

    for conf_file_path in target_file_list:
        conf_text = runner.exec(f'cat {conf_file_path}')
        result[conf_file_path] = __parse_sshd_config(conf_text)

    return result


def __parse_logrotate_config(text: str):
    lines = remove_comment(text)
    files = []
    for line in lines:
        if re.match(r'^/\S+', line):
            files.append(line.replace('{', '').strip())
    config_block = re.findall(r'\{((.|\s)*)\}','\n'.join(lines))
    fixed_config = remove_comment(
        ' '.join(config_block[0]).replace('\t', '    '))
    
    return {
        'target': files,
        'config': fixed_config
    }


def logrotated(runner: CommandRunner) -> dict[str, dict]:
    result = {}
    target_file_list = runner.exec(f'find {LOGROTATE_CONF_D} | egrep -v "{LOGROTATE_CONF_D}$"')

    conf_text = runner.exec(f'cat {LOGROTATE_CONF_FILE}')
    result[LOGROTATE_CONF_FILE] = {
        'target': ['default'],
        'config': remove_comment(conf_text)
    }
    
    for conf_file_path in target_file_list.splitlines():
        conf_text = runner.exec(f'cat {conf_file_path}')
        result[conf_file_path] = __parse_logrotate_config(conf_text)

    return result

def cron(runner: CommandRunner) -> dict[str, str]:
    result = {}
    cron_conf_d = runner.exec(
        f'find {CRON_CONF_D} | egrep -v "{CRON_CONF_D}$"')
    user_cron_conf_d = runner.exec(
        f'find {USER_CRON_CONF_D} | egrep -v "{USER_CRON_CONF_D}$"')

    target_file_list = []
    target_file_list.extend(remove_comment(cron_conf_d))
    target_file_list.extend(remove_comment(user_cron_conf_d))

    for conf_path in target_file_list:
        conf_text = runner.exec(f'cat {conf_path}')
        result[conf_path] = remove_comment(conf_text)

    return result
    
def __parse_chrony_config(text: str) -> list:
    result = []
    fixed_text_lines = remove_comment(text)
    for line in fixed_text_lines:
        spl = line.split()
        result.append({
            'key': spl[0],
            'value': ' '.join(spl[1:])
        })

    return result

def chrony(runner: CommandRunner) -> list[dict]:
    conf_text = runner.exec(f'cat {CHRONY_CONF_FILE}')
    return __parse_chrony_config(conf_text)

def dnf(runner: CommandRunner) -> dict[dict]:
    conf_text = runner.exec(f'cat {DNF_CONF_FILE}')
    parser = configparser.ConfigParser()
    parser.read_string(conf_text)
    conf_dict = {
        section: dict(parser.items(section)) 
            for section in parser.sections()
    }

    return conf_dict

def dnf_repo(runner: CommandRunner) -> dict[dict]:
    result = {}
    target_files = runner.exec(f'find {DNF_REPO_D} | egrep -v "{DNF_REPO_D}$"')
    for conf_file_path in target_files.splitlines():
        if conf_file_path.split('/')[-1] in DNF_REPO_EXCLUSION:
            continue

        conf_text = runner.exec(f'cat {conf_file_path}')
        parser = configparser.ConfigParser()
        parser.read_string(conf_text)
        conf_dict = {
            section: dict(parser.items(section))
                for section in parser.sections()
        }
        result[conf_file_path] = conf_dict

    return result

def __remove_comment_sudoers(text: str):
    result = []
    for l in text.splitlines():
        stripped_l = l.strip()
        if not stripped_l or re.match('^#+($|\s)', stripped_l):
            continue

        result.append(l.replace('\t', '    '))

    return result

def sudoers(runner: CommandRunner) -> dict[list]:
    result = {}
    target_files = [SUDOERS_CONF]
    sudoers_d = runner.exec(
        f'find {SUDOERS_CONF_D} | egrep -v "{SUDOERS_CONF_D}$"'
    )
    for line in sudoers_d.splitlines():
        target_files.append(line)

    for conf_path in target_files:
        conf_text = runner.exec(f'cat {conf_path}')
        result[conf_path] = __remove_comment_sudoers(conf_text)

    return result

def __firewalld_get_opts(
    runner: CommandRunner, zone: str
) -> (list, list):
    services = []
    rich_rules = []

    services_text = runner.exec(
        f'firewall-cmd --zone={zone} --list-services'
    )
    for line in services_text.splitlines():
        services.extend(line.strip().split())

    rich_rule_text = runner.exec(
        f'firewall-cmd --zone={zone} --list-rich-rules'
    )
    for line in rich_rule_text.splitlines():
        if re.match('^rule', line.strip()):
            rich_rules.append(line.strip())

    return services, rich_rules

def firewalld(runner: CommandRunner) -> dict[str, dict]:
    result = {}
    active_zones_text = runner.exec('firewall-cmd --get-active-zones') 

    zone = None
    for line in active_zones_text.splitlines():
        if re.match('^\S+', line):
            zone = line.strip()
            services, rich_rules = __firewalld_get_opts(
                runner, zone
            )
            result[zone] = {
                'interfaces': [],
                'services': services,
                'rich_rules': rich_rules
            }
        if not zone:
            continue

        if re.match('^\s+interfaces:', line):
            interfaces = line.strip().split()[1:]
            result[zone]['interfaces'] = interfaces

    return result


def sysconfig_grub(runner: CommandRunner) -> dict[str, str]:
    result = {}
    sysconfig_grub_config = runner.exec('cat /etc/sysconfig/grub')
    print(sysconfig_grub_config)

    for line in sysconfig_grub_config.splitlines():
        if re.match(r'^[A-Z]+', line):
            sep = line.split('=')
            result[sep[0]] = sep[1]

    return result

