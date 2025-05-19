from libs.utils import CommandRunner
from libs.excelize.excelizer import *
from libs.excelize.excelizers.linux_os_excelizer import LinuxOSExcelizer
from libs.excelize.excelizers.linux_oss_excelizer import LinuxOSSExcelizer
from libs.gatherer import *
from pprint import pprint
import os

username = os.getenv('OS2SHEET_LINUX_USERNAME')
password = os.getenv('OS2SHEET_LINUX_PASSWORD')
root_password = os.getenv('OS2SHEET_LINUX_ROOT_PASSWORD')
ip = os.getenv('OS2SHEET_LINUX_IP')


# linux_os_gatherer = LinuxOSGatherer(
#    ip, username, password=password, root_password=root_password
# )
# linux_os_gatherer.connect()
#
# excelizer = LinuxOSExcelizer(
#    linux_os_gatherer,
#    './test.xlsx',
#    'CLIENTNAME', 'CONTRACTORNAME', 'PROJECTNAME',
#    'DOCUMENTNUMBER', 'SYSTEMNAME', 'DOCUMENTNAME', 'DOCUMENTTITLE'
# )
#

linux_oss_gatherer = LinuxOSSGatherer(
    ip, username, password=password, root_password=root_password
)
linux_oss_gatherer.connect()

excelizer = LinuxOSSExcelizer(
    linux_oss_gatherer,
    './test.xlsx',
    'CLIENTNAME', 'CONTRACTORNAME', 'PROJECTNAME',
    'DOCUMENTNUMBER', 'SYSTEMNAME', 'DOCUMENTNAME', 'DOCUMENTTITLE'
)


excelizer.build_main_sheet()
excelizer.write()
excelizer.save_and_close()


pprint(excelizer.get_dict())
