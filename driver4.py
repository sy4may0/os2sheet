from libs.utils import CommandRunner
from libs.excelize.excelizer import *
from libs.excelize.excelizers.zabbix_excelizer import ZabbixExcelizer
from libs.gatherer.zabbix_gatherer import *
from libs.gatherer import *
from pprint import pprint
import os

username = os.getenv('OS2SHEET_LINUX_USERNAME')
password = os.getenv('OS2SHEET_LINUX_PASSWORD')
root_password = os.getenv('OS2SHEET_LINUX_ROOT_PASSWORD')
ip = os.getenv('OS2SHEET_LINUX_IP')

os_config_gatherer = ZabbixOSConfigGatherer(
    ip, username, password=password, root_password=root_password
)
os_config_gatherer.connect()


excelizer = ZabbixExcelizer(
    os_config_gatherer,
    ZabbixUserGatherer(
        ip, username, password=password, root_password=root_password,
        zabbix_api_url=f"http://{ip}/zabbix/api_jsonrpc.php",
        zabbix_api_user="Admin",
        zabbix_api_password="zabbix"
    ),
    ZabbixHostGatherer(
        ip, username, password=password, root_password=root_password,
        zabbix_api_url=f"http://{ip}/zabbix/api_jsonrpc.php",
        zabbix_api_user="Admin",
        zabbix_api_password="zabbix"
    ),
    ZabbixTemplateGatherer(
        ip, username, password=password, root_password=root_password,
        zabbix_api_url=f"http://{ip}/zabbix/api_jsonrpc.php",
        zabbix_api_user="Admin",
        zabbix_api_password="zabbix"
    ),
    ZabbixAlertGatherer(
        ip, username, password=password, root_password=root_password,
        zabbix_api_url=f"http://{ip}/zabbix/api_jsonrpc.php",
        zabbix_api_user="Admin",
        zabbix_api_password="zabbix"
    ),
    './test.xlsx',
    'CLIENTNAME', 'CONTRACTORNAME', 'PROJECTNAME',
    'DOCUMENTNUMBER', 'SYSTEMNAME', 'DOCUMENTNAME', 'DOCUMENTTITLE'
)

excelizer.build_main_sheet()
excelizer.write()
excelizer.save_and_close()


pprint(excelizer.get_dict())
