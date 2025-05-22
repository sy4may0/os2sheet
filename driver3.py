from libs.gatherer.zabbix_gatherer import ZabbixUserGatherer
from libs.gatherer.zabbix_gatherer import ZabbixOSConfigGatherer
from libs.gatherer.zabbix_gatherer import ZabbixAlertGatherer
from libs.gatherer.zabbix_gatherer import ZabbixHostGatherer
from libs.gatherer.zabbix_gatherer import ZabbixTemplateGatherer
from pprint import pprint
import os

username = os.getenv('OS2SHEET_LINUX_USERNAME')
password = os.getenv('OS2SHEET_LINUX_PASSWORD')
root_password = os.getenv('OS2SHEET_LINUX_ROOT_PASSWORD')
ip = os.getenv('OS2SHEET_LINUX_IP')


zabbix_user_gatherer = ZabbixUserGatherer(
    host=ip,
    user=username,
    password=password,
    root_password=root_password,
    zabbix_api_url=f"http://{ip}/zabbix/api_jsonrpc.php",
    zabbix_api_user="Admin",
    zabbix_api_password="zabbix"
)
zabbix_user_gatherer.connect()

pprint(zabbix_user_gatherer.get_zabbix_users())
pprint(zabbix_user_gatherer.get_zabbix_usergroups())
pprint(zabbix_user_gatherer.get_zabbix_roles())

zabbix_os_config_gatherer = ZabbixOSConfigGatherer(
    host=ip,
    user=username,
    password=password,
    root_password=root_password,
)
zabbix_os_config_gatherer.connect()

pprint(zabbix_os_config_gatherer.get_server_config())
pprint(zabbix_os_config_gatherer.get_agent_config())
pprint(zabbix_os_config_gatherer.get_web_config())

zabbix_alert_gatherer = ZabbixAlertGatherer(
    host=ip,
    user=username,
    password=password,
    root_password=root_password,
    zabbix_api_url=f"http://{ip}/zabbix/api_jsonrpc.php",
    zabbix_api_user="Admin",
    zabbix_api_password="zabbix"
)
zabbix_alert_gatherer.connect()

pprint(zabbix_alert_gatherer.get_mediatypes())
pprint(zabbix_alert_gatherer.get_trigger_actions())

zabbix_host_gatherer = ZabbixHostGatherer(
    host=ip,
    user=username,
    password=password,
    root_password=root_password,
    zabbix_api_url=f"http://{ip}/zabbix/api_jsonrpc.php",
    zabbix_api_user="Admin",
    zabbix_api_password="zabbix"
)
zabbix_host_gatherer.connect()

pprint(zabbix_host_gatherer.get_hostgroups())
pprint(zabbix_host_gatherer.get_hosts())

zabbix_template_gatherer = ZabbixTemplateGatherer(
    host=ip,
    user=username,
    password=password,
    root_password=root_password,
    zabbix_api_url=f"http://{ip}/zabbix/api_jsonrpc.php",
    zabbix_api_user="Admin",
    zabbix_api_password="zabbix"
)
zabbix_template_gatherer.connect()

pprint(zabbix_template_gatherer.get_templategroups())
pprint(zabbix_template_gatherer.get_templates(
    target_template=["Linux by Zabbix agent active"]
))
