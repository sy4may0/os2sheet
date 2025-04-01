RSYSLOG_CONF_FILE = '/etc/rsyslog.conf'
RSYSLOG_CONF_D = '/etc/rsyslog.d/'
SSHD_CONF_FILE = '/etc/ssh/sshd_config'
SSHD_CONF_D = '/etc/ssh/sshd_config.d'
LOGROTATE_CONF_FILE = '/etc/logrotate.conf'
LOGROTATE_CONF_D = '/etc/logrotate.d'
CRON_CONF_D = '/etc/cron.d'
USER_CRON_CONF_D = '/var/spool/cron'
CHRONY_CONF_FILE = '/etc/chrony.conf'
DNF_CONF_FILE = '/etc/dnf/dnf.conf'
DNF_REPO_D = '/etc/yum.repos.d'
DNF_REPO_EXCLUSION = [
    'redhat.repo',
    'almalinux-appstream.repo',
    'almalinux-baseos.repo'
]
SUDOERS_CONF = '/etc/sudoers'
SUDOERS_CONF_D = '/etc/sudoers.d'
