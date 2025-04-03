from libs.utils import CommandRunner
from libs.gatherer import linux_general
from libs.gatherer import linux_optional
from pprint import pprint

ip = '192.168.56.102'
user = 'sy4may0'

cmd_runner = CommandRunner(ip, user, password='sy4/yoshinon')
cmd_runner.su('root00')

#selinux_config = linux_general.selinux(cmd_runner)
#print(selinux_config)
#
#nmcli_config = linux_general.nmcli(cmd_runner)
#pprint(nmcli_config)
#
#localdisk_config = linux_general.localdisk(cmd_runner)
#pprint(localdisk_config)
#
#default_target_config = linux_general.default_target(cmd_runner)
#print(default_target_config)
#
#timezone_config = linux_general.timezone(cmd_runner)
#print(timezone_config)
#
#locale_config = linux_general.locale(cmd_runner)
#print(locale_config)
#
#group_config = linux_general.group(cmd_runner)
#pprint(group_config)
#
#user_config = linux_general.user(cmd_runner)
#pprint(user_config)

systemd_config = linux_general.systemd_units(cmd_runner)
pprint(systemd_config)

rpm_pkgs = linux_general.rpm_packages(cmd_runner)
pprint(rpm_pkgs)

version = linux_general.rhel_version(cmd_runner)
print(version)

cpu = linux_general.cpu(cmd_runner)
pprint(cpu)

mem = linux_general.mem(cmd_runner)
pprint(mem)

fstab_config = linux_general.fstab(cmd_runner)
pprint(fstab_config)

#rsyslog_config = linux_optional.rsyslog(cmd_runner)
#pprint(rsyslog_config)
#
#sshd_config = linux_optional.sshd(cmd_runner)
#pprint(sshd_config)
#
#logrotate_config = linux_optional.logrotated(cmd_runner)
#pprint(logrotate_config)
#

#cron_config = linux_optional.cron(cmd_runner)
#pprint(cron_config)
#
#chrony_config = linux_optional.chrony(cmd_runner)
#pprint(chrony_config)
#
#dnf_config = linux_optional.dnf(cmd_runner)
#pprint(dnf_config)
#
#dnf_repo = linux_optional.dnf_repo(cmd_runner)
#pprint(dnf_repo)
#
#sudoers = linux_optional.sudoers(cmd_runner)
#pprint(sudoers)
#
#firewalld = linux_optional.firewalld(cmd_runner)
#pprint(firewalld)