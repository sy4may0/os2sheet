from libs.gatherer.zabbix_gatherer.abstract_host import ZabbixAbstractHostGatherer
from libs.defines.zabbix_key_map import TEMPLATE_KEYMAP


class ZabbixTemplateGatherer(ZabbixAbstractHostGatherer):
    def __init__(
        self,
        host: str,
        user: str,
        port: int = 22,
        password: str = None,
        root_password: str = None,
        keyfile: str = None,
        zabbix_api_url: str = None,
        zabbix_api_user: str = None,
        zabbix_api_password: str = None
    ):
        super().__init__(
            host,
            user,
            port,
            password,
            root_password,
            keyfile,
            zabbix_api_url,
            zabbix_api_user,
            zabbix_api_password
        )

        self.templategroups = None
        self.templates = None

    def get_templategroups(self):
        if self.templategroups:
            return self.templategroups

        templategroups = self.cached_zapi_get(
            "templategroup", output="extend"
        )

        self.templategroups = [
            group['name'] for group in templategroups
        ]

        return self.templategroups

    def get_templates(self, target_template: list = []):
        if self.templates:
            return self.templates
        else:
            self.templates = []

        templates = self.get_by_filter(
            {
                "host": target_template
            },
            "template", output="extend",
            selectGroups="extend",
            selectTags="extend",
            selectParentTemplates="extend",
            selectItems=['itemid'],
            selectDiscoveries=['itemid'],
            selectTriggers=['triggerid'],
            selectGraphs=['graphid'],
            selectMacros="extend",
            selectValueMaps="extend",
            selectDashboards="extend",
        )

        for template in templates:
            template_item = self.parse_api_result(
                template,
                TEMPLATE_KEYMAP
            )

            template_item['Host groups'] = self.parse_host_groups(
                template['groups']
            )
            template_item['Templates'] = self.parse_host_parent_templates(
                template['parentTemplates']
            )
            template_item['Macros'] = self.parse_macros(
                template['macros'])
            template_item['Value maps'] = self.parse_value_maps(
                template['valuemaps']
            )
            template_item['Tags'] = self.parse_tags(template['tags'])

            template_item['Items'] = []
            for itemid in template['items']:
                item = self.get_item(template['templateid'], itemid['itemid'], {
                                     'templated': True, 'inherited': False})

                if item:
                    template_item['Items'].append(item)

            template_item['Triggers'] = []
            for triggerid in template['triggers']:
                trigger = self.get_trigger(template['templateid'], triggerid['triggerid'], {
                    'templated': True, 'inherited': False
                })
                if trigger:
                    template_item['Triggers'].append(trigger)

            self.templates.append(template_item)

            template_item['Graphs'] = []
            for graphid in template['graphs']:
                graph = self.get_graph(template['templateid'], graphid['graphid'], {
                    'templated': True, 'inherited': False
                })

                if graph:
                    template_item['Graphs'].append(graph)

            template_item['Discovery'] = []
            for itemid in template['discoveries']:
                discovery = self.get_lld_rules(template['templateid'], itemid['itemid'], {
                    'templated': True, 'inherited': False
                })

                if discovery:
                    template_item['Discovery'].append(discovery)

        return self.templates
