NMCLI_TARGET_PROPS = [
    'connection.id',
    'connection.uuid',
    'connection.interface-name',
    'connection.autoconnect',
    'connection.autoconnect-priority',
    'ipv4.addresses',
    'ipv4.gateway',
    'ipv4.dns',
    'ipv4.method',
    'ipv6.addresses',
    'ipv6.gateway',
    'ipv6.dns',
    'ipv6.method',
    'connection.master',
    'connection.slave-type',
    'bond.mode',
    'bond.miimon',
    'bond.lacp_rate',
    'bond.xmit_hash_policy',
]
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
    'almalinux-crb.repo',
    'almalinux-highavailability.repo',
    'almalinux-plus.repo',
    'almalinux-rt.repo',
    'almalinux-saphana.repo',
    'almalinux-baseos.repo',
    'almalinux-extras.repo',
    'almalinux-nfv.repo',
    'almalinux-resilientstorage.repo',
    'almalinux-sap.repo'
]
SUDOERS_CONF = '/etc/sudoers'
SUDOERS_CONF_D = '/etc/sudoers.d'
SYSCTL_CONF = '/etc/sysctl.conf'
SYSCTL_CONF_D = '/etc/sysctl.d'
AUTHSELECT_PATH = '/etc/authselect/'
AUTHSELECT_TARGET = [
    'fingerprint-auth',
    'password-auth',
    'smartcard-auth',
    'system-auth',
]