from libs.gatherer.zabbix_gatherer import ZabbixOSConfigGatherer
from libs.gatherer.zabbix_gatherer import ZabbixUserGatherer
from libs.gatherer.zabbix_gatherer import ZabbixHostGatherer
from libs.gatherer.zabbix_gatherer import ZabbixTemplateGatherer
from libs.gatherer.zabbix_gatherer import ZabbixAlertGatherer
from libs.excelize.excelizer import Excelizer
from libs.excelize.contents import ContentSheet, ContentCollection, ParentContent, ValueContent


class ZabbixExcelizer(Excelizer):
    def __init__(self,
                 os_config_gatherer: ZabbixOSConfigGatherer,
                 user_gatherer: ZabbixUserGatherer,
                 host_gatherer: ZabbixHostGatherer,
                 template_gatherer: ZabbixTemplateGatherer,
                 alert_gatherer: ZabbixAlertGatherer,
                 write_file: str,
                 client_name: str = "",
                 contractor_name: str = "",
                 project_name: str = "",
                 document_number: str = "",
                 system_name: str = "",
                 document_name: str = "",
                 document_title: str = "",):
        super().__init__(
            write_file,
            client_name,
            contractor_name,
            project_name,
            document_number,
            system_name,
            document_name,
            document_title
        )
        self.__os_config_gatherer = os_config_gatherer
        self.__user_gatherer = user_gatherer
        self.__host_gatherer = host_gatherer
        self.__template_gatherer = template_gatherer
        self.__alert_gatherer = alert_gatherer

    @property
    def os_config_gatherer(self):
        return self.__os_config_gatherer

    @property
    def user_gatherer(self):
        return self.__user_gatherer

    @property
    def host_gatherer(self):
        return self.__host_gatherer

    @property
    def template_gatherer(self):
        return self.__template_gatherer

    @property
    def alert_gatherer(self):
        return self.__alert_gatherer

    def build_os_config_sheet(self):
        contents = []
        server_config = self.os_config_gatherer.get_server_config()
        agent_config = self.os_config_gatherer.get_agent_config()
        merge_config = {**server_config, **agent_config}
        for path, conf in merge_config.items():
            items = []
            for _c in conf:
                items.append(
                    ParentContent(
                        _c['key'],
                        [
                            ValueContent(items=[_c['value']])
                        ],
                        0
                    )
                )
            contents.append(
                ContentCollection(
                    path,
                    items,
                    0
                )
            )
        web_items = []
        for conf in self.os_config_gatherer.get_web_config():
            web_items.append(
                ParentContent(
                    conf['key'],
                    [
                        ValueContent(items=[conf['value']])
                    ],
                    0
                )
            )
        contents.append(
            ContentCollection(
                'Web設定(/etc/zabbix/web/zabbix.conf.php)',
                web_items,
                0
            )
        )

        return contents

    def __build_permissions_content(self, permissions):
        contents = []
        for permission in permissions:
            if not permission['Groups']:
                continue
            for group in permission['Groups']:
                contents.append(
                    ParentContent(
                        group, [
                            ValueContent(items=[permission['Permission']])
                        ],
                        indent=2
                    )
                )
        return contents

    def __build_tag_filters_content(self, tag_filters):
        contents = []
        index = 1
        for tag_filter in tag_filters:
            tag_contents = []
            hostgroup_content = ParentContent(
                'Host group',
                [
                    ValueContent(items=[tag_filter['Host group']])
                ],
                indent=3
            )
            for tag in tag_filter['Tags']:
                tag_contents.append(
                    ValueContent(
                        items=[
                            f"{tag['Tag']}: {tag['Value']}"
                        ]
                    )
                )
            tag_content = ParentContent(
                'Tags',
                tag_contents,
                indent=3
            )
            contents.append(
                ParentContent(
                    f'Tag filter {index}',
                    [
                        hostgroup_content,
                        tag_content
                    ],
                    indent=2
                )
            )
            index += 1

        return contents

    def __build_user_group_content(self, usergrp, conf):
        contents = []
        for key, value in conf.items():
            if key == 'Host permissions':
                contents.append(
                    ParentContent(
                        'Host permissions',
                        self.__build_permissions_content(value),
                        indent=1
                    )
                )
                continue
            if key == 'Tag filters':
                contents.append(
                    ParentContent(
                        'Tag filters',
                        self.__build_tag_filters_content(value),
                        indent=1
                    )
                )
                continue
            if key == 'Template permissions':
                contents.append(
                    ParentContent(
                        'Template permissions',
                        self.__build_permissions_content(value),
                        indent=1
                    )
                )
                continue

            contents.append(
                ParentContent(
                    key,
                    [
                        ValueContent(items=[value])
                    ],
                    indent=1
                )
            )

        return contents

    def build_user_sheet(self):
        contents = []

        usergrp_contents = []
        for usergrp, conf in self.user_gatherer.get_zabbix_usergroups().items():
            usergrp_contents.append(
                ParentContent(
                    usergrp,
                    self.__build_user_group_content(usergrp, conf),
                    indent=0
                )
            )
        contents.append(
            ContentCollection(
                'User groups',
                usergrp_contents,
                0
            )
        )

        return contents

    def build_main_sheet(self):
        self.add_sheet(
            ContentSheet('設定ファイル', self.build_os_config_sheet(), '設定ファイル')
        )

        self.add_sheet(
            ContentSheet('ユーザ設定', self.build_user_sheet(), 'ユーザ設定')
        )
