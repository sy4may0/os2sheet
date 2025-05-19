from libs.gatherer.zabbix_gatherer.abstract_host import ZabbixAbstractHostGatherer
from libs.defines.zabbix_key_map import HOST_KEYMAP, HOST_IPMI_KEYMAP, HOST_ENCRYPTION_KEYMAP, HOST_INTERFACE_KEYMAP, HOST_INTERFACE_DETAILS_V3_KEYMAP, HOST_INTERFACE_DETAILS_V1V2_KEYMAP, VALUEMAP_TYPE_KEYMAP


class ZabbixHostGatherer(ZabbixAbstractHostGatherer):
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

        self.hostgroups = None
        self.hosts = None

    def get_hostgroups(self):
        if self.hostgroups:
            return self.hostgroups
        else:
            self.hostgroups = []

        hostgroups = self.cached_zapi_get(
            'hostgroup',
            output='extend'
        )

        for hostgroup in hostgroups:
            self.hostgroups.append(hostgroup['name'])

        return self.hostgroups

    def __resolve_tls_accept(self, host):
        result = {
            'No encryption': 'No',
            'PSK': 'No',
            'Certificate': 'No',
        }

        binary = format(int(host['tls_accept']), '03b')

        if binary[2] == '1':
            result['No encryption'] = 'Yes'
        if binary[1] == '1':
            result['PSK'] = 'Yes'
        if binary[0] == '1':
            result['Certificate'] = 'Yes'

        return result

    def __parse_host_encryption(self, host):
        encryption = self.parse_api_result(
            host,
            HOST_ENCRYPTION_KEYMAP
        )

        encryption['Connections from host'] = self.__resolve_tls_accept(host)

        if (
            host['tls_accept'] == '1' or
            encryption['Connections from host']['PSK'] == 'Yes'
        ):
            encryption['PSK identity'] = '*******(hidden)'
            encryption['PSK passphrase'] = '*******(hidden)'

        if (
            host['tls_accept'] == 2 or
            encryption['Connections from host']['Certificate'] == 'Yes'
        ):
            encryption['Issuer'] = host['tls_issuer']
            encryption['Subject'] = host['tls_subject']

        return encryption

    def __parse_host_interfaces(self, interfaces):
        result = []

        for interface in interfaces:
            interface_item = self.parse_api_result(
                interface,
                HOST_INTERFACE_KEYMAP
            )

            if interface['details']:
                if interface['details']['version'] == '3':
                    interface_item['SNMP'] = self.parse_api_result(
                        interface['details'],
                        HOST_INTERFACE_DETAILS_V3_KEYMAP
                    )
                else:
                    interface_item['SNMP'] = self.parse_api_result(
                        interface['details'],
                        HOST_INTERFACE_DETAILS_V1V2_KEYMAP
                    )

            result.append(interface_item)

        return result

    def get_hosts(self):
        if self.hosts:
            return self.hosts
        else:
            self.hosts = []

        hosts = self.cached_zapi_get(
            'host',
            output='extend',
            selectGroups='extend',
            selectInterfaces='extend',
            selectMacros='extend',
            selectTags='extend',
            selectParentTemplates='extend',
            selectInventory='extend',
            selectValueMaps='extend',
            selectItems=['itemid'],
            selectTriggers=['triggerid'],
            selectGraphs=['graphid'],
            selectDiscoveries=['itemid']
        )

        for host in hosts:
            host_item = self.parse_api_result(
                host,
                HOST_KEYMAP
            )

            host_item['IPMI'] = self.parse_api_result(
                host,
                HOST_IPMI_KEYMAP
            )

            host_item['Encryption'] = self.__parse_host_encryption(host)
            host_item['Interfaces'] = self.__parse_host_interfaces(
                host['interfaces'])

            host_item['Host groups'] = self.parse_host_groups(host['groups'])
            host_item['Templates'] = self.parse_host_parent_templates(
                host['parentTemplates']
            )
            host_item['Macros'] = self.parse_macros(host['macros'])
            host_item['Value maps'] = self.parse_value_maps(
                host['valuemaps']
            )
            host_item['Tags'] = self.parse_tags(host['tags'])

            host_item['Items'] = []
            for itemid in host['items']:
                item = self.get_item(host['hostid'], itemid['itemid'], {
                    'templated': False, 'inherited': False,
                    'monitored': True
                })

                if item:
                    host_item['Items'].append(item)

            host_item['Triggers'] = []
            for triggerid in host['triggers']:
                trigger = self.get_trigger(host['hostid'], triggerid['triggerid'], {
                    'templated': False, 'inherited': False,
                    'monitored': True
                })
                if trigger:
                    host_item['Triggers'].append(trigger)

            host_item['Graphs'] = []
            for graphid in host['graphs']:
                graph = self.get_graph(host['hostid'], graphid['graphid'], {
                    'templated': False, 'inherited': False,
                    'monitored': True
                })
                if graph:
                    host_item['Graphs'].append(graph)

            self.hosts.append(host_item)

            host_item['Discovery'] = []
            for itemid in host['discoveries']:
                discovery = self.get_lld_rules(host['hostid'], itemid['itemid'], {
                    'templated': False, 'inherited': False,
                    'monitored': True
                })
                if discovery:
                    host_item['Discovery'].append(discovery)

        return self.hosts
