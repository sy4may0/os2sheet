from libs.gatherer.zabbix_gatherer.zabbix_api_gatherer import ZabbixAPIGatherer
from libs.defines.zabbix_key_map import MESSAGE_TEMPLATE_KEYMAP, MEDIATYPE_EMAIL_KEYMAP, TRIGGER_ACTION_KEYMAP, OPERATION_SENDMSG_KEYMAP, ACTION_CONDITION_KEYMAP, ACTION_CONDITION_OPERATOR_KEYMAP, ACTION_EVAL_TYPE_KEYMAP, TRIGGER_SEVERITY_KEYMAP
from libs.defines.zabbix_key_map import BOOL_KEYMAP, BOOL_KEYMAP_REVERSE
from pprint import pprint


class ZabbixAlertGatherer(ZabbixAPIGatherer):
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

        self.mediatypes = None
        self.actions = None

    def __parse_email_mediatype(self, mediatype: dict):
        mediatype_result = self.parse_api_result(
            mediatype, MEDIATYPE_EMAIL_KEYMAP
        )
        mediatype_result['Message templates'] = []
        message_templates = mediatype['message_templates']

        for message_template in message_templates:
            message_template = self.parse_api_result(
                message_template, MESSAGE_TEMPLATE_KEYMAP
            )
            # fix message_type
            message_template['Message type'] = ' '.join(
                [
                    message_template['Event source'],
                    message_template['Recovery'],
                ]
            )
            del message_template['Event source']
            del message_template['Recovery']

            mediatype_result['Message templates'].append(message_template)

        return mediatype_result

    def get_mediatypes(self):
        if self.mediatypes:
            return self.mediatypes
        else:
            self.mediatypes = {}

        mediatypes = self.get_by_filter(
            {'status': '0'},
            'mediatype',
            output='extend',
            selectMessageTemplates='extend',
        )

        for mediatype in mediatypes:
            if mediatype['type'] == '0':
                self.mediatypes[mediatype['name']
                                ] = self.__parse_email_mediatype(mediatype)

        return self.mediatypes

    def __resolve_opmessage_grp(self, groups: list):
        result = []
        for group in groups:
            usergroup = self.get_by_filter(
                {'usrgrpid': group['usrgrpid']},
                'usergroup',
                output='extend',
            )
            result.append(usergroup[0]['name'])

        return result

    def __resolve_opmessage_user(self, users: list):
        result = []
        for user in users:
            user = self.get_by_filter(
                {'userid': user['userid']},
                'user',
                output='extend',
            )
            result.append(user[0]['name'])

        return result

    def __resolve_opmessage(self, opmessage: dict):
        result = {}
        result['Custom_message'] = BOOL_KEYMAP_REVERSE[opmessage['default_msg']]
        if opmessage['mediatypeid'] == '0':
            result['Send to media types'] = 'All available'
        else:
            mediatype = self.get_by_filter(
                {'mediatypeid': opmessage['mediatypeid']},
                'mediatype',
                output='extend',
            )
            result['Send to media types'] = mediatype[0]['name']
        if opmessage['default_msg'] != '1':
            result['Subject'] = opmessage['subject']
            result['Message'] = opmessage['message']

        return result

    def __parse_sendmsg_operations(self, operations: list, is_esc: bool = False):
        results = []
        for operation in operations:
            if is_esc:
                result = self.parse_api_result(
                    operation, OPERATION_SENDMSG_KEYMAP
                )
            else:
                result = {}

            if operation['operationtype'] == '11':
                result['Operation'] = 'Notify all involved'
                return result
            elif operation['operationtype'] == '0':
                result['Operation'] = 'Send message'
            else:
                return None

            result['Send to user groups'] = self.__resolve_opmessage_grp(
                operation['opmessage_grp']
            )
            result['Send to users'] = self.__resolve_opmessage_user(
                operation['opmessage_usr']
            )
            result.update(self.__resolve_opmessage(operation['opmessage']))

            results.append(result)

        return results

    def __parse_hostgroup_condition_filter(self, filter: dict):
        result = self.parse_api_result(
            filter, ACTION_CONDITION_KEYMAP
        )
        hostgroup = self.get_by_filter(
            {'groupid': filter['value']},
            'hostgroup',
            output='extend',
        )
        operator = ACTION_CONDITION_OPERATOR_KEYMAP[filter['operator']]
        result['Condition'] = f"Host group {operator} {hostgroup[0]['name']}"

        return result

    def __parse_host_condition_filter(self, filter: dict):
        result = self.parse_api_result(
            filter, ACTION_CONDITION_KEYMAP
        )
        host = self.get_by_filter(
            {'hostid': filter['value']},
            'host',
            output='extend',
        )
        operator = ACTION_CONDITION_OPERATOR_KEYMAP[filter['operator']]
        result['Condition'] = f"Host {operator} {host[0]['name']}"
        return result

    def __parse_trigger_condition_filter(self, filter: dict):
        result = self.parse_api_result(
            filter, ACTION_CONDITION_KEYMAP
        )
        trigger = self.get_by_filter(
            {'triggerid': filter['value']},
            'trigger',
            output='extend',
            selectHosts='extend',
        )
        hostname = trigger[0]['hosts'][0]['name']
        operator = ACTION_CONDITION_OPERATOR_KEYMAP[filter['operator']]
        result['Condition'] = f"Trigger {operator} {hostname}: {trigger[0]['description']}"
        return result

    def __parse_event_name_condition_filter(self, filter: dict):
        result = self.parse_api_result(
            filter, ACTION_CONDITION_KEYMAP
        )
        operator = ACTION_CONDITION_OPERATOR_KEYMAP[filter['operator']]
        result['Condition'] = f"Event name {operator} {filter['value']}"
        return result

    def __parse_trigger_severity_condition_filter(self, filter: dict):
        result = self.parse_api_result(
            filter, ACTION_CONDITION_KEYMAP
        )
        operator = ACTION_CONDITION_OPERATOR_KEYMAP[filter['operator']]
        result['Condition'] = f"Trigger severity {operator} {TRIGGER_SEVERITY_KEYMAP[filter['value']]}"
        return result

    def __parse_time_period_condition_filter(self, filter: dict):
        result = self.parse_api_result(
            filter, ACTION_CONDITION_KEYMAP
        )
        operator = ACTION_CONDITION_OPERATOR_KEYMAP[filter['operator']]
        result['Condition'] = f"Time period {operator} {filter['value']}"
        return result

    def __parse_host_template_condition_filter(self, filter: dict):
        result = self.parse_api_result(
            filter, ACTION_CONDITION_KEYMAP
        )
        template = self.get_by_filter(
            {'templateid': filter['value']},
            'template',
            output='extend',
        )
        operator = ACTION_CONDITION_OPERATOR_KEYMAP[filter['operator']]
        result['Condition'] = f"Host template {operator} {template[0]['name']}"
        return result

    def __parse_problem_suppressed_condition_filter(self, filter: dict):
        result = self.parse_api_result(
            filter, ACTION_CONDITION_KEYMAP
        )
        if ACTION_CONDITION_OPERATOR_KEYMAP[filter['operator']] == 'Yes':
            result['Condition'] = 'Problem is suppressed'
        else:
            result['Condition'] = 'Problem is not suppressed'
        return result

    def __parse_event_tag_condition_filter(self, filter: dict):
        result = self.parse_api_result(
            filter, ACTION_CONDITION_KEYMAP
        )
        operator = ACTION_CONDITION_OPERATOR_KEYMAP[filter['operator']]
        result['Condition'] = f"Tag name {operator} {filter['value']}"
        return result

    def __parse_event_tag_value_condition_filter(self, filter: dict):
        result = self.parse_api_result(
            filter, ACTION_CONDITION_KEYMAP
        )
        operator = ACTION_CONDITION_OPERATOR_KEYMAP[filter['operator']]
        result['Condition'] = f"Value of tag {filter['value2']} {operator} {filter['value']}"

        return result

    def __parse_trigger_action_filter(self, filter: list):
        result = {}

        result['Type of calculation'] = ACTION_EVAL_TYPE_KEYMAP[filter['evaltype']]
        if filter['evaltype'] == '3':
            result['Formula'] = filter['formula']
        else:
            result['Formula'] = filter['eval_formula']

        result['Conditions'] = []
        for condition in filter['conditions']:
            if condition['conditiontype'] == '0':
                result['Conditions'].append(
                    self.__parse_hostgroup_condition_filter(condition)
                )
            elif condition['conditiontype'] == '1':
                result['Conditions'].append(
                    self.__parse_host_condition_filter(condition)
                )
            elif condition['conditiontype'] == '2':
                result['Conditions'].append(
                    self.__parse_trigger_condition_filter(condition)
                )
            elif condition['conditiontype'] == '3':
                result['Conditions'].append(
                    self.__parse_event_name_condition_filter(condition)
                )
            elif condition['conditiontype'] == '4':
                result['Conditions'].append(
                    self.__parse_trigger_severity_condition_filter(condition)
                )
            elif condition['conditiontype'] == '6':
                result['Conditions'].append(
                    self.__parse_time_period_condition_filter(condition)
                )
            elif condition['conditiontype'] == '13':
                result['Conditions'].append(
                    self.__parse_host_template_condition_filter(condition)
                )
            elif condition['conditiontype'] == '16':
                result['Conditions'].append(
                    self.__parse_problem_suppressed_condition_filter(condition)
                )
            elif condition['conditiontype'] == '25':
                result['Conditions'].append(
                    self.__parse_event_tag_condition_filter(condition)
                )
            elif condition['conditiontype'] == '26':
                result['Conditions'].append(
                    self.__parse_event_tag_value_condition_filter(condition)
                )
        return result

    def get_trigger_actions(self):
        if self.actions:
            return self.actions
        else:
            self.actions = {}

        actions = self.get_by_filter(
            {'status': '0'},
            'action',
            output='extend',
            selectFilter='extend',
            selectOperations='extend',
            selectRecoveryOperations='extend',
            selectUpdateOperations='extend',
        )

        for action in actions:

            if action['eventsource'] != '0':
                continue

            action_result = self.parse_api_result(
                action, TRIGGER_ACTION_KEYMAP
            )
            action_result['Operations'] = self.__parse_sendmsg_operations(
                action['operations'], is_esc=True
            )
            action_result['Recovery operations'] = self.__parse_sendmsg_operations(
                action['recovery_operations'], is_esc=False
            )
            action_result['Update operations'] = self.__parse_sendmsg_operations(
                action['update_operations'], is_esc=False
            )
            action_result['Filter'] = self.__parse_trigger_action_filter(
                action['filter']
            )

            self.actions[action['name']] = action_result

        return self.actions
