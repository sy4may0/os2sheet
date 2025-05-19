from libs.gatherer.zabbix_gatherer.zabbix_api_gatherer import ZabbixAPIGatherer
from libs.defines.zabbix_key_map import ACTION_CONDITION_OPERATOR_KEYMAP, ACTION_EVAL_TYPE_KEYMAP, HOST_ENCRYPTION_KEYMAP, HOST_INTERFACE_KEYMAP, HOST_INTERFACE_DETAILS_V3_KEYMAP, HOST_INTERFACE_DETAILS_V1V2_KEYMAP, LLD_OPERATION_KEYMAP, LLD_OVERRIDE_KEYMAP, VALUEMAP_TYPE_KEYMAP, ITEM_KEYMAP, OPTIONAL_ITEM_KEYMAP, HOST_INVENTORY_KEYMAP, TRIGGER_KEYMAP, PREPROCESSING_KEYMAP, GRAPH_KEYMAP, GLAPH_ITEM_KEYMAP, LLD_LIFETIME_KEYMAP
import re


class ZabbixAbstractHostGatherer(ZabbixAPIGatherer):
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

    def parse_macros(self, macros):
        result = []

        for macro in macros:
            if macro.get('value'):
                value = macro['value']
            else:
                value = '*****(hidden)'

            result.append({
                'macro': macro['macro'],
                'value': value
            })

        return result

    def parse_value_maps(self, value_maps):
        result = []

        for value_map in value_maps:
            mappings = [
                {
                    'type': VALUEMAP_TYPE_KEYMAP[mapping['type']],
                    'value': f"{mapping['value']} => {mapping['newvalue']}"
                } for mapping in value_map['mappings']
            ]

            result.append({
                'name': value_map['name'],
                'mappings': mappings
            })

        return result

    def parse_host_groups(self, host_groups):
        return [group['name'] for group in host_groups]

    def parse_host_parent_templates(self, parent_templates):
        return [tpl['host'] for tpl in parent_templates]

    def parse_tags(self, tags):
        return [
            {
                'tag': tag['tag'],
                'value': tag['value']
            } for tag in tags
        ]

    def __resolve_item_name(self, itemid: str):

        item = self.get_by_filter(
            {
                "itemid": itemid
            },
            "item",
            output=['name', 'hostid'],
        )
        if not item:
            item = self.get_by_filter(
                {
                    "itemid": itemid
                },
                "itemprototype",
                output=['name', 'hostid'],
            )

        host = self.get_by_filter(
            {
                "templateid": item[0]['hostid']
            },
            "template",
            output='extend',
        )
        if not host:
            host = self.get_by_filter(
                {
                    "hostid": item[0]['hostid']
                },
                "host",
                output='extend',
            )

        hostname = host[0]['host']

        if item:
            return f"{hostname}: {item[0]['name']}"

        return None

    def __resolve_preprocessing(self, preprocessings: list):
        result = []

        for preprocessing in preprocessings:
            item = self.parse_api_result(preprocessing, PREPROCESSING_KEYMAP)
            if item['Parameters']:
                params = item['Parameters'].split('\n')
                params_dict = {}
                i = 1
                for param in params:
                    params_dict[f'param{i}'] = param
                    i += 1

                item['Parameters'] = params_dict
            else:
                item['Parameters'] = {}

            result.append(item)

        return result

    def __resolve_general_item_params(self, item: dict):
        if item['Type of information'] not in ['numeric float', 'numeric unsigned']:
            del item['Units']
            del item['Trends']

        if item['Type of information'] != 'log':
            del item['Log time format']
        else:
            del item['Populates host inventory field']

        if item['Type of information'] not in ['numeric float', 'numeric unsigned', 'character']:
            del item['Value mapping']

        if item['History'] == '0':
            item['History'] = 'Do not store'

        if 'Timeout' in item and item['Timeout'] is None:
            item['Timeout'] = 'Use global timeout'

        if (
            'Update interval' in item and
            re.match(r'^[0-9]+.*;.*', item['Update interval'])
        ):
            part = item['Update interval'].split(';')
            item['Update interval'] = part[0]
            item['Custom timeout'] = part[1:]

        if item.get('Populates host inventory field') and item['Populates host inventory field'] in HOST_INVENTORY_KEYMAP:
            item['Populates host inventory field'] = HOST_INVENTORY_KEYMAP[item['Populates host inventory field']]
        else:
            item['Populates host inventory field'] = '-None-'

        if 'Units' in item and item['Units'] is None:
            item['Units'] = ''

        if 'Log time format' in item and item['Log time format'] is None:
            item['Log time format'] = ''

        if 'Master item' in item and item['Master item']:
            item['Master item'] = self.__resolve_item_name(
                item['Master item'])

    def parse_item(self, item: dict):
        result = self.parse_api_result(item, ITEM_KEYMAP)
        if result['Type'] in OPTIONAL_ITEM_KEYMAP:
            result.update(self.parse_api_result(
                item, OPTIONAL_ITEM_KEYMAP[result['Type']]))
        else:
            result.update({'error': 'Unsupported item type'})

        if 'Value mapping' in result and result['Value mapping'] != '0':
            result['Value mapping'] = item['valuemap']['name']

        if 'tags' in item:
            result['Tags'] = self.parse_tags(item['tags'])

        if 'preprocessing' in item:
            result['Preprocessing'] = self.__resolve_preprocessing(
                item['preprocessing'])

        self.__resolve_general_item_params(result)

        return result

    def get_item(
            self, hostid: str,
            itemid: str,
            params: dict = {},
            prototype: bool = False
    ):
        method = 'item'
        if prototype:
            method = 'itemprototype'

        items = self.get_by_dual_layer_filter(
            {
                "hostid": hostid
            },
            {
                "itemid": itemid
            },
            method,
            output="extend",
            selectPreprocessing="extend",
            selectTags="extend",
            selectDiscoveryRule="extend",
            selectValueMap="extend",
            **params
        )
        if len(items) == 0:
            return None

        item = items[0]

        if item['discoveryRule'] and not prototype:
            return None

        result = self.parse_item(item)
        if result:
            return result

        return None

    def __resolve_dependent_trigger(self, dependent_triggers: list):
        result = []

        for dependent_trigger in dependent_triggers:
            triggerid = dependent_trigger['triggerid']
            trigger = self.cached_zapi_get(
                filter={
                    'triggerid': triggerid
                },
                method='trigger',
                output='extend',
                selectHosts='extend',
            )
            if not trigger:
                trigger = self.cached_zapi_get(
                    filter={
                        'triggerid': triggerid
                    },
                    method='triggerprototype',
                    output='extend',
                    selectHosts='extend',
                )
            host = trigger[0]['hosts'][0]['host']
            trigger_name = trigger[0]['description']

            result.append(
                f'{host}: {trigger_name}'
            )

        return result

    def __build_function_map(self, functions: list):
        result = {}

        for function in functions:
            item = self.cached_zapi_get(
                filter={
                    'itemid': function['itemid']
                },
                method='item',
                output='extend',
                selectHosts='extend',
            )
            if not item:
                item = self.cached_zapi_get(
                    filter={
                        'itemid': function['itemid']
                    },
                    method='itemprototype',
                    output='extend',
                    selectHosts='extend',
                )
            host = item[0]['hosts'][0]['host']
            key = item[0]['key_']
            param = function['parameter'].split(',')
            if len(param) >= 1 and param[0] == '$':
                param.pop(0)
            func_args = ','.join([
                f"/{host}/{key}",
                *param
            ])
            text_function = f"{function['function']}({func_args})"
            result[function['functionid']] = text_function
        return result

    def __resolve_expression(self, expression: str, functions: list):
        func_map = self.__build_function_map(functions)

        for itemid, text_function in func_map.items():
            expression = expression.replace('{'+itemid+'}', text_function)

        return expression

    def parse_trigger(self, trigger: dict):
        result = self.parse_api_result(trigger, TRIGGER_KEYMAP)
        for key, value in result.items():
            if value is None:
                result[key] = ''

        if result['OK event generation'] != 'Recovery expression':
            del result['Recovery expression']

        if 'Expression' in result and result['Expression']:
            result['Expression'] = self.__resolve_expression(
                result['Expression'],
                trigger['functions']
            )

        if 'Recovery expression' in result and result['Recovery expression']:
            result['Recovery expression'] = self.__resolve_expression(
                result['Recovery expression'],
                trigger['functions']
            )

        if 'tags' in trigger:
            result['Tags'] = self.parse_tags(trigger['tags'])

        if 'dependencies' in trigger:
            result['Dependencies'] = self.__resolve_dependent_trigger(
                trigger['dependencies'])

        return result

    def get_trigger(
            self, hostid: str,
            triggerid: str,
            params: dict = {},
            prototype: bool = False
    ):
        method = 'trigger'
        if prototype:
            method = 'triggerprototype'

        triggers = self.get_by_dual_layer_filter(
            {
                "hostid": hostid
            },
            {
                "triggerid": triggerid
            },
            method,
            output="extend",
            selectFunctions="extend",
            selectDependencies="extend",
            selectDiscoveryRule="extend",
            selectTags="extend",
            **params
        )
        if len(triggers) == 0:
            return None

        trigger = triggers[0]

        if trigger['discoveryRule'] and not prototype:
            return None

        result = self.parse_trigger(trigger)
        return result

    def __parse_graph_items(self, graph_items: list, gtype: str):
        result = []
        for graph_item in graph_items:
            gitem = self.parse_api_result(graph_item, GLAPH_ITEM_KEYMAP)
            if gtype == 'Normal':
                del gitem['Type']

            if gtype == 'Stacked':
                del gitem['Draw type']
                del gitem['Type']

            if gtype == 'Pie' or gtype == 'Exploded':
                del gitem['Draw type']
                del gitem['Y axis side']

            gitem['Item'] = self.__resolve_item_name(gitem['Item'])

            result.append(gitem)

        return result

    def parse_graph(self, graph: dict):
        result = self.parse_api_result(graph, GRAPH_KEYMAP)

        if result['Y axis MAX value'] == 'Calculated':
            result.pop('Y axis MAX', None)
            result.pop('Y axis MAX value item', None)

        if result['Y axis MIN value'] == 'Calculated':
            result.pop('Y axis MIN', None)
            result.pop('Y axis MIN value item', None)

        if result['Y axis MAX value'] == 'item':
            result.pop('Y axis MAX', None)
            result['Y axis MAX value item'] = self.__resolve_item_name(
                result['Y axis MAX value item'])

        if result['Y axis MIN value'] == 'item':
            result.pop('Y axis MIN', None)
            result['Y axis MIN value item'] = self.__resolve_item_name(
                result['Y axis MIN value item'])

        if result['Y axis MAX value'] == 'Fixed':
            result.pop('Y axis MAX value item', None)

        if result['Y axis MIN value'] == 'Fixed':
            result.pop('Y axis MIN value item', None)

        if result['Graph type'] == 'Normal':
            result.pop('Show 3D', None)

        if result['Graph type'] == 'Stacked':
            result.pop('Show 3D', None)
            result.pop('Percentile line(left)', None)
            result.pop('Percentile line(right)', None)

        if result['Graph type'] == 'Pie' or result['Graph type'] == 'Exploded':
            result.pop('Show working time', None)
            result.pop('Show triggers', None)
            result.pop('Percentile line(left)', None)
            result.pop('Percentile line(right)', None)
            result.pop('Y axis MAX', None)
            result.pop('Y axis MIN', None)
            result.pop('Y axis MAX value', None)
            result.pop('Y axis MIN value', None)
            result.pop('Y axis MAX value item', None)
            result.pop('Y axis MIN value item', None)

        graph_items = self.__parse_graph_items(
            graph['gitems'], result['Graph type'])
        result['Graph items'] = graph_items

        return result

    def get_graph(
            self, hostid: str,
            graphid: str, params: dict = {},
            prototype: bool = False
    ):
        method = 'graph'
        if prototype:
            method = 'graphprototype'

        graphs = self.get_by_dual_layer_filter(
            {
                "hostid": hostid
            },
            {
                "graphid": graphid
            },
            method,
            output="extend",
            selectGraphItems="extend",
            selectDiscoveryRule="extend",
            **params
        )

        if len(graphs) == 0:
            return None

        graph = graphs[0]

        if graph['discoveryRule'] and not prototype:
            return None

        result = self.parse_graph(graph)

        return result

    def __resolve_lld_lifetime(self, item: dict):
        result = {}
        result['Delete lost resources'] = {
            'type': LLD_LIFETIME_KEYMAP[item['lifetime_type']],
            'param': item['lifetime']
        }
        if result['Delete lost resources']['type'] != 'After':
            del result['Delete lost resources']['param']

        result['Disable lost resources'] = {
            'type': LLD_LIFETIME_KEYMAP[item['enabled_lifetime_type']],
            'param': item['enabled_lifetime']
        }
        if result['Disable lost resources']['type'] != 'After':
            del result['Disable lost resources']['param']

        return result

    def __resolve_lld_macro_paths(self, lld_macro_paths: list):
        result = [
            {'macro': _m['lld_macro'], 'path': _m['path']}
            for _m in lld_macro_paths
        ]

        return result

    def __resolve_lld_filter(self, filter: dict):
        result = {
            'Type of calculation': ACTION_EVAL_TYPE_KEYMAP[filter['evaltype']],
        }
        if filter['evaltype'] != '3':
            result['Formula'] = filter['eval_formula']
        else:
            result['Formula'] = filter['formula']

        result['Conditions'] = []
        for condition in filter['conditions']:
            result['Conditions'].append({
                'Label': condition['formulaid'],
                'Macro': condition['macro'],
                'Operator': ACTION_CONDITION_OPERATOR_KEYMAP[condition['operator']],
                'Regular expression': condition['value']
            })

        return result

    def __resolve_lld_operations(self, operations: dict):
        result = []
        for operation in operations:
            _o = self.parse_api_result(operation, LLD_OPERATION_KEYMAP)

            result.append(_o)

        return result

    def __resolve_lld_overrides(self, overrides: list):
        result = []
        for override in overrides:
            _o = self.parse_api_result(override, LLD_OVERRIDE_KEYMAP)

            _o['Filter'] = self.__resolve_lld_filter(override['filter'])
            _o['Operations'] = self.__resolve_lld_operations(
                override['operations'])

            result.append(_o)

        return result

    def __resolve_lld_subobjects(self, item: dict, hostid: str):
        result = {
            'Items': [],
            'Triggers': [],
            'Graphs': [],
        }
        for itemid in item['items']:
            _i = self.get_item(hostid, itemid['itemid'], prototype=True)
            if _i:
                result['Items'].append(_i)

        for triggerid in item['triggers']:
            _t = self.get_trigger(
                hostid, triggerid['triggerid'], prototype=True)
            if _t:
                result['Triggers'].append(_t)

        for graphid in item['graphs']:
            _g = self.get_graph(hostid, graphid['graphid'], prototype=True)
            if _g:
                result['Graphs'].append(_g)

        return result

    def parse_lld_rule(self, item: dict, hostid: str):
        result = self.parse_api_result(item, ITEM_KEYMAP)
        if result['Type'] in OPTIONAL_ITEM_KEYMAP:
            result.update(self.parse_api_result(
                item, OPTIONAL_ITEM_KEYMAP[result['Type']]))
        else:
            result.update({'error': 'Unsupported item type'})

        if 'preprocessing' in item:
            result['Preprocessing'] = self.__resolve_preprocessing(
                item['preprocessing'])

        self.__resolve_general_item_params(result)

        del result['History']
        del result['Type of information']

        result.update(self.__resolve_lld_lifetime(item))

        result['LLD macros'] = self.__resolve_lld_macro_paths(
            item['lld_macro_paths'])

        result['Filter'] = self.__resolve_lld_filter(item['filter'])

        result['Overrides'] = self.__resolve_lld_overrides(item['overrides'])

        result.update(self.__resolve_lld_subobjects(item, hostid))

        return result

    def get_lld_rules(self, hostid: str, itemid: str, params: dict = {}):
        lld_rules = self.get_by_dual_layer_filter(
            {
                "hostid": hostid
            },
            {
                "itemid": itemid
            },
            "discoveryrule",
            output="extend",
            selectPreprocessing="extend",
            selectLLDMacroPaths="extend",
            selectFilter="extend",
            selectOverrides="extend",
            selectItems=['itemid'],
            selectTriggers=['triggerid'],
            selectGraphs=['graphid'],
            **params
        )

        if len(lld_rules) == 0:
            return None

        result = self.parse_lld_rule(lld_rules[0], hostid)

        return result
