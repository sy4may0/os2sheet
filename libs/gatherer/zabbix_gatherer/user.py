from libs.gatherer.zabbix_gatherer.zabbix_api_gatherer import ZabbixAPIGatherer
from libs.defines.zabbix_key_map import \
    BOOL_KEYMAP, \
    USERGROUP_KEYMAP, \
    USER_KEYMAP, \
    USER_MEDIA_KEYMAP, \
    HOSTGROUP_RIGHT_KEYMAP, \
    ROLE_KEYMAP, \
    ROLE_ACTION_NAME_MAP, \
    ROLE_UI_NAME_MAP, \
    ROLE_API_METHOD_KEYMAP


class ZabbixUserGatherer(ZabbixAPIGatherer):
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
        """
        Initialize the ZabbixGatherer.

        If zabbix_api_url, zabbix_api_user and zabbix_api_password are not set, the ZabbixGatherer will not be able to connect to the Zabbix API.

        Args:
            host: The host to connect to.
            user: The user to connect to.
            port: The port to connect to.
            password: The password to connect to.
            root_password: The root password to connect to.
            keyfile: The keyfile to connect to.
            zabbix_api_url: The URL of the Zabbix API.
            zabbix_api_user: The user to connect to the Zabbix API.
            zabbix_api_password: The password to connect to the Zabbix API.
        """
        super().__init__(
            host,
            user,
            port,
            password,
            root_password=root_password,
            keyfile=keyfile,
            zabbix_api_url=zabbix_api_url,
            zabbix_api_user=zabbix_api_user,
            zabbix_api_password=zabbix_api_password
        )
        self.server_config = None
        self.agent_config = None
        self.web_config = None
        self.usergroups = None
        self.users = None
        self.roles = None

    ### USERGROUP GATHERING ##############
    def __fix_tag_filters(self, tag_filters: list) -> list:
        dict_result = {}
        for tag_filter in tag_filters:
            groupid = tag_filter['groupid']
            group_search = self.get_by_filter(
                {'groupid': groupid},
                'hostgroup',
                output='extend',
            )
            group_name = group_search[0]['name']

            if tag_filter['tag'] == '':
                tag_filter['tag'] = 'all'
            if tag_filter['value'] == '':
                tag_filter['value'] = 'all'

            if not dict_result.get(group_name):
                dict_result[group_name] = []

            dict_result[group_name].append({
                'Tag': tag_filter['tag'],
                'Value': tag_filter['value']
            })

        list_result = []
        for k, v in dict_result.items():
            list_result.append({
                'Host group': k,
                'Tags': v
            })

        return list_result

    def __reverse_permission_dict(self, permission_dict: dict) -> dict:
        result = {key: [] for key in HOSTGROUP_RIGHT_KEYMAP.values()}

        for item in permission_dict:
            result[item['Permission']].append(item['Group'])

        list_result = []
        for k, v in result.items():
            list_result.append({
                'Permission': k,
                'Groups': v
            })

        return list_result

    def __fix_hostgroup_rights(self, rights: list) -> list:
        result = []
        for right in rights:
            group_search = self.get_by_filter(
                {'groupid': right['id']},
                'hostgroup',
                output='extend',
            )
            group_name = group_search[0]['name']

            result.append({
                'Group': group_name,
                'Permission': HOSTGROUP_RIGHT_KEYMAP[right['permission']]
            })

        return self.__reverse_permission_dict(result)

    def __fix_template_rights(self, rights: list) -> list:
        result = []
        for right in rights:
            groupid = right['id']
            group_search = self.get_by_filter(
                {'groupid': groupid},
                'templategroup',
                output='extend',
            )
            group_name = group_search[0]['name']

            result.append({
                'Group': group_name,
                'Permission': HOSTGROUP_RIGHT_KEYMAP[right['permission']]
            })

        return self.__reverse_permission_dict(result)

    def get_zabbix_usergroups(self):
        """
        Get the user groups.

        Returns:
            dict: The user groups.
        """
        if self.usergroups:
            return self.usergroups
        else:
            self.usergroups = {}

        usergroups = self.cached_zapi_get(
            'usergroup',
            output='extend',
            selectHostGroupRights='extend',
            selectTemplateGroupRights='extend',
            selectTagFilters='extend'
        )

        for usergroup in usergroups:
            self.usergroups[usergroup['name']] = \
                self.parse_api_result(
                    usergroup, USERGROUP_KEYMAP)

            self.usergroups[usergroup['name']]['Tag filters'] = \
                self.__fix_tag_filters(
                    usergroup['tag_filters'])

            self.usergroups[usergroup['name']]['Host permissions'] = \
                self.__fix_hostgroup_rights(
                    usergroup['hostgroup_rights'])

            self.usergroups[usergroup['name']]['Template permissions'] = \
                self.__fix_template_rights(
                    usergroup['templategroup_rights'])

        return self.usergroups

    ### USER GATHERING ##############
    def __resolve_mediatype_severity(self, num: int) -> str:
        severity_map = {
            0: 'not classified',
            1: 'information',
            2: 'warning',
            3: 'average',
            4: 'high',
            5: 'disaster'
        }
        result = []
        binary = format(num, '06b')

        for i in range(6):
            if binary[i] == '1':
                result.append(severity_map[i])

        return result

    def __fix_user_medias(self, user: list[dict]):
        result = []
        for media in user['medias']:
            media_item = self.parse_api_result(
                media, USER_MEDIA_KEYMAP
            )

            mediatype = self.search_fk_item(
                'mediatypeid', media['mediatypeid'],
                user['mediatypes']
            )
            media_item['Type'] = mediatype['name']

            media_item['Use if Severity'] = self.__resolve_mediatype_severity(
                int(media['severity'])
            )

            result.append(media_item)

        return result

    def __fix_user_related_groups(self, user: dict):
        return [
            group['name'] for group in user['usrgrps']
        ]

    def __fix_user_role(self, user: dict):
        return user['role']['name']

    def get_zabbix_users(self):
        """
        Get the users.

        Returns:
            dict: The users.
        """
        if self.users:
            return self.users

        result = {}

        users = self.cached_zapi_get(
            'user',
            output='extend',
            selectUsrgrps='extend',
            selectMedias='extend',
            selectMediatypes='extend',
            selectRole='extend'
        )

        for user in users:
            result[user['username']] = self.parse_api_result(
                user, USER_KEYMAP)

            result[user['username']]['Groups'] = self.__fix_user_related_groups(
                user
            )

            result[user['username']]['Medias'] = self.__fix_user_medias(
                user
            )

            result[user['username']]['Role'] = self.__fix_user_role(
                user
            )

        self.users = result
        return self.users

    ### ROLE GATHERING ##############
    def __parse_action_rules(self, rules: list) -> dict:
        result = []
        for rule in rules:
            key = ROLE_ACTION_NAME_MAP[rule['name']]
            status = BOOL_KEYMAP[rule['status']]
            result.append({
                'name': key,
                'status': status,
            })

        return result

    def __fix_role_action_rules(self, rules: dict) -> dict:
        result = {}

        result['Default access to new actions'] = \
            BOOL_KEYMAP[rules['actions.default_access']]

        result['Access to actions'] = \
            self.__parse_action_rules(
                rules['actions']
        )

        return result

    def __parse_ui_rules(self, rules: list) -> dict:
        result = {}
        for rule in rules:
            key = ROLE_UI_NAME_MAP[rule['name']]['name']
            status = BOOL_KEYMAP[rule['status']]
            group = ROLE_UI_NAME_MAP[rule['name']]['group']

            if not result.get(group):
                result[group] = []

            result[group].append({
                'name': key,
                'status': status,
            })

        return result

    def __fix_role_ui_rules(self, rules: dict) -> dict:
        result = {}
        result['Default access to new UI elements'] = \
            BOOL_KEYMAP[rules['ui.default_access']]

        result['Access to UI elements'] = \
            self.__parse_ui_rules(
                rules['ui']
        )

        return result

    def __resolve_module_name(self, moduleid: str) -> str:
        modules = self.get_by_filter(
            {'moduleid': str(moduleid)},
            'module',
            output='extend',
        )

        return modules[0]['id']

    def __fix_role_module_rules(self, rules: dict) -> dict:
        result = {}
        result['Default access to new modules'] = \
            BOOL_KEYMAP[rules['modules.default_access']]

        modules = []
        for rule in rules['modules']:
            modules.append({
                'name': self.__resolve_module_name(rule['moduleid']),
                'status': BOOL_KEYMAP[rule['status']]
            })

        result['Access to modules'] = modules

        return result

    def __fix_role_api_rules(self, rules: dict) -> dict:
        result = {}

        result['Enabled'] = BOOL_KEYMAP[rules['api.access']]
        result['API methods'] = \
            ROLE_API_METHOD_KEYMAP[rules['api.mode']]
        result['API'] = rules['api']

        return {
            'Access to API': result
        }

    def __parse_services_rule_mode(
        self, mode: str, list: list
    ) -> str:
        if mode == '1':
            return 'All'
        elif mode == '0' and len(list) == 0:
            return 'None'
        else:
            return 'Service list'

    def __resolve_service_name(self, serviceid: str) -> str:
        services = self.get_by_filter(
            {'serviceid': serviceid},
            'service',
            output='extend',
        )

        return services[0]['name']

    def __fix_role_services_rules(self, rules: dict) -> dict:
        result = {}

        result['Read-write access to services'] = \
            self.__parse_services_rule_mode(
                rules['services.write.mode'],
                rules['services.write.list']
        )

        result['Read-only access to services'] = \
            self.__parse_services_rule_mode(
                rules['services.read.mode'],
                rules['services.read.list']
        )

        result['Read-write access to service with tag'] = \
            rules['services.write.tag']

        result['Read-only access to service with tag'] = \
            rules['services.read.tag']

        result['Read-write services'] = \
            [
                self.__resolve_service_name(service['serviceid'])
                for service in rules['services.write.list']
        ]

        result['Read-only services'] = \
            [
                self.__resolve_service_name(service['serviceid'])
                for service in rules['services.read.list']
        ]

        return {'Access to services': result}

    def get_zabbix_roles(self):
        """
        Get the roles.

        Returns:
            dict: The roles.
        """
        if self.roles:
            return self.roles

        result = {}

        roles = self.cached_zapi_get(
            'role',
            output='extend',
            selectRules='extend'
        )

        for role in roles:
            result[role['name']] = \
                self.parse_api_result(role, ROLE_KEYMAP)

            if role.get('readonly') == '1':
                continue

            result[role['name']].update(
                self.__fix_role_action_rules(
                    role['rules']
                )
            )

            result[role['name']].update(
                self.__fix_role_ui_rules(
                    role['rules']
                )
            )

            result[role['name']].update(
                self.__fix_role_module_rules(
                    role['rules']
                )
            )

            result[role['name']].update(
                self.__fix_role_api_rules(
                    role['rules']
                )
            )

            result[role['name']].update(
                self.__fix_role_services_rules(
                    role['rules']
                )
            )

        self.roles = result
        return self.roles
