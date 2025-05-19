BOOL_KEYMAP = {
    '0': 'No',
    '1': 'Yes'
}

BOOL_KEYMAP_REVERSE = {
    '0': 'Yes',
    '1': 'No'
}

TRIGGER_SEVERITY_KEYMAP = {
    '0': 'Not classified',
    '1': 'Information',
    '2': 'Warning',
    '3': 'Average',
    '4': 'High',
    '5': 'Disaster'
}

USERGROUP_GUI_ACCESS_KEYMAP = {
    '0': 'Default',
    '1': 'Internal',
    '2': 'LDAP',
    '3': 'Disabled'
}

USERGROUP_KEYMAP = {
    'name': {'key': 'Group name', 'vmap': None},
    'gui_access': {'key': 'Frontend access', 'vmap': USERGROUP_GUI_ACCESS_KEYMAP},
    'users_status': {'key': 'Enabled', 'vmap': BOOL_KEYMAP_REVERSE},
    'debug_mode': {'key': 'Debug mode', 'vmap': BOOL_KEYMAP},
}

USER_KEYMAP = {
    'username': {'key': 'Username', 'vmap': None},
    'name': {'key': 'Name', 'vmap': None},
    'surname': {'key': 'Last name', 'vmap': None},
    'usrgrps': {'key': 'Groups', 'vmap': None},
    'lang': {'key': 'Language', 'vmap': None},
    'timezone': {'key': 'Time zone', 'vmap': None},
    'theme': {'key': 'Theme', 'vmap': None},
    'autologin': {'key': 'Auto-login', 'vmap': BOOL_KEYMAP},
    'autologout': {'key': 'Auto-logout', 'vmap': None},
    'refresh': {'key': 'Refresh', 'vmap': None},
    'rows_per_page': {'key': 'Rows per page', 'vmap': None},
    'url': {'key': 'URL', 'vmap': None},
}

USER_MEDIA_KEYMAP = {
    'sendto': {'key': 'Send to', 'vmap': None},
    'period': {'key': 'When active', 'vmap': None},
    'severity': {'key': 'Use if Severity', 'vmap': None},
    'active': {'key': 'Status', 'vmap': BOOL_KEYMAP_REVERSE},
}

HOSTGROUP_RIGHT_KEYMAP = {
    '0': 'Deny',
    '2': 'Read-Only',
    '3': 'Read-Write'
}

ROLE_TYPE_KEYMAP = {
    '1': 'User',
    '2': 'Admin',
    '3': 'Super Admin'
}

ROLE_KEYMAP = {
    'name': {'key': 'Name', 'vmap': None},
    'readonly': {'key': 'Read-Only', 'vmap': BOOL_KEYMAP},
    'type': {'key': 'Type', 'vmap': ROLE_TYPE_KEYMAP},
}

ROLE_ACTION_NAME_MAP = {
    'edit_dashboards': 'Create and edit dashboards',
    'edit_maps': 'Create and edit maps',
    'edit_maintenance': 'Create and edit maintenance',
    'add_problem_comments': 'Add problem comments',
    'change_severity': 'Change severity',
    'acknowledge_problems': 'Acknowledge problems',
    'suppress_problems': 'Suppress problems',
    'close_problems': 'Close problems',
    'execute_scripts': 'Execute scripts',
    'manage_api_tokens': 'Manage API tokens',
    'manage_scheduled_reports': 'Manage scheduled reports',
    'manage_sla': 'Manage SLA',
    'invoke_execute_now': 'Invoke Execute Now on read-only hosts',
    'change_problem_ranking': 'Change problem ranking',
}

ROLE_API_METHOD_KEYMAP = {
    '0': 'Deny list',
    '1': 'Allow list'
}

ROLE_UI_NAME_MAP = {
    'monitoring.dashboard': {'name': 'Dashboards', 'group': 'Monitoring'},
    'monitoring.problems': {'name': 'Problems', 'group': 'Monitoring'},
    'monitoring.hosts': {'name': 'Hosts', 'group': 'Monitoring'},
    'monitoring.latest_data': {'name': 'Latest data', 'group': 'Monitoring'},
    'monitoring.maps': {'name': 'Maps', 'group': 'Monitoring'},
    'services.services': {'name': 'Services', 'group': 'Services'},
    'services.sla_report': {'name': 'SLA report', 'group': 'Services'},
    'inventory.overview': {'name': 'Overview', 'group': 'Inventory'},
    'inventory.hosts': {'name': 'Hosts', 'group': 'Inventory'},
    'reports.availability_report': {'name': 'Availability report', 'group': 'Reports'},
    'reports.top_triggers': {'name': 'Top 100 triggers', 'group': 'Reports'},
    'monitoring.discovery': {'name': 'Discovery', 'group': 'Monitoring'},
    'services.sla': {'name': 'SLA', 'group': 'Services'},
    'reports.scheduled_reports': {'name': 'Scheduled reports', 'group': 'Reports'},
    'reports.notifications': {'name': 'Notifications', 'group': 'Reports'},
    'configuration.template_groups': {'name': 'Template groups', 'group': 'Data collection'},
    'configuration.host_groups': {'name': 'Host groups', 'group': 'Data collection'},
    'configuration.templates': {'name': 'Templates', 'group': 'Data collection'},
    'configuration.hosts': {'name': 'Hosts', 'group': 'Data collection'},
    'configuration.maintenance': {'name': 'Maintenance', 'group': 'Data collection'},
    'configuration.discovery': {'name': 'Discovery', 'group': 'Data collection'},
    'configuration.trigger_actions': {'name': 'Trigger actions', 'group': 'Alerts'},
    'configuration.service_actions': {'name': 'Service actions', 'group': 'Alerts'},
    'configuration.discovery_actions': {'name': 'Discovery actions', 'group': 'Alerts'},
    'configuration.autoregistration_actions': {'name': 'Autoregistration actions', 'group': 'Alerts'},
    'configuration.internal_actions': {'name': 'Internal actions', 'group': 'Alerts'},
    'reports.system_info': {'name': 'System information', 'group': 'Reports'},
    'reports.audit': {'name': 'Audit log', 'group': 'Reports'},
    'reports.action_log': {'name': 'Action log', 'group': 'Reports'},
    'configuration.event_correlation': {'name': 'Event correlation', 'group': 'Data collection'},
    'administration.media_types': {'name': 'Media types', 'group': 'Alerts'},
    'administration.scripts': {'name': 'Scripts', 'group': 'Alerts'},
    'administration.user_groups': {'name': 'User groups', 'group': 'Users'},
    'administration.user_roles': {'name': 'User roles', 'group': 'Users'},
    'administration.users': {'name': 'Users', 'group': 'Users'},
    'administration.api_tokens': {'name': 'API tokens', 'group': 'Users'},
    'administration.authentication': {'name': 'Authentication', 'group': 'Users'},
    'administration.general': {'name': 'General', 'group': 'Administration'},
    'administration.audit_log': {'name': 'Audit log', 'group': 'Administration'},
    'administration.housekeeping': {'name': 'Housekeeping', 'group': 'Administration'},
    'administration.proxy_groups': {'name': 'Proxy groups', 'group': 'Administration'},
    'administration.proxies': {'name': 'Proxies', 'group': 'Administration'},
    'administration.macros': {'name': 'Macros', 'group': 'Administration'},
    'administration.queue': {'name': 'Queue', 'group': 'Administration'},
}

EMAIL_PROVIDER_KEYMAP = {
    '0': 'Generic SMTP',
    '1': 'Gmail',
    '2': 'Gmail relay',
    '3': 'Office 365',
    '4': 'Office 365 relay',
}

EMAIL_SECURITY_KEYMAP = {
    '0': 'None',
    '1': 'STARTTLS',
    '2': 'SSL/TLS',
}

EMAIL_MSG_FORMAT_KEYMAP = {
    '0': 'Plain text',
    '1': 'HTML',
}

MEDIATYPE_EMAIL_KEYMAP = {
    'name': {'key': 'Name', 'vmap': None},
    'provider': {'key': 'Provider', 'vmap': EMAIL_PROVIDER_KEYMAP},
    'smtp_server': {'key': 'SMTP server', 'vmap': None},
    'smtp_port': {'key': 'SMTP server port', 'vmap': None},
    'smtp_email': {'key': 'Email', 'vmap': None},
    'smtp_helo': {'key': 'SMTP helo', 'vmap': None},
    'smtp_security': {'key': 'Connection security', 'vmap': EMAIL_SECURITY_KEYMAP},
    'smtp_verify_peer': {'key': 'SSL verify peer', 'vmap': BOOL_KEYMAP},
    'smtp_verify_host': {'key': 'SSL verify host', 'vmap': BOOL_KEYMAP},
    'smtp_authentication': {'key': 'Authentication', 'vmap': BOOL_KEYMAP},
    'username': {'key': 'Username', 'vmap': None},
    'passwd': {'key': 'Password', 'vmap': None},
    'message_format': {'key': 'Message format', 'vmap': EMAIL_MSG_FORMAT_KEYMAP},
    'status': {'key': 'Enabled', 'vmap': BOOL_KEYMAP_REVERSE},
    'maxsessions': {'key': 'Concurrent sessions', 'vmap': None},
    'maxattempts': {'key': 'Max attempts', 'vmap': None},
    'attempt_interval': {'key': 'Attempt interval', 'vmap': None},
}

EVENT_SOURCE_KEYMAP = {
    '0': 'Problem',
    '1': 'Discovery',
    '2': 'Autoregistration',
    '3': 'Internal',
    '4': 'Services'
}

EVENT_RECOVERY_KEYMAP = {
    '0': '',
    '1': 'recovery',
    '2': 'update'
}

MESSAGE_TEMPLATE_KEYMAP = {
    'eventsource': {'key': 'Event source', 'vmap': EVENT_SOURCE_KEYMAP},
    'recovery': {'key': 'Recovery', 'vmap': EVENT_RECOVERY_KEYMAP},
    'subject': {'key': 'Subject', 'vmap': None},
    'message': {'key': 'Message', 'vmap': None},
}

TRIGGER_ACTION_KEYMAP = {
    'name': {'key': 'Name', 'vmap': None},
    'pause_symptoms': {'key': 'Pause operations for symptom problems', 'vmap': BOOL_KEYMAP},
    'pause_suppressed': {'key': 'Pause operations for suppressed problems', 'vmap': BOOL_KEYMAP},
    'notify_if_canceled': {'key': 'Notify about canceled escalations', 'vmap': BOOL_KEYMAP},
    'esc_period': {'key': 'Default operation step duration', 'vmap': None},
}

OPERATION_SENDMSG_KEYMAP = {
    'esc_period': {'key': 'Step duration', 'vmap': None},
    'esc_step_from': {'key': 'Steps from', 'vmap': None},
    'esc_step_to': {'key': 'Steps to', 'vmap': None},

}

ACTION_CONDITION_OPERATOR_KEYMAP = {
    '0': 'equals',
    '1': 'does not equal',
    '2': 'contains',
    '3': 'does not contain',
    '4': 'in',
    '5': 'is greater than equals',
    '6': 'is less than equals',
    '7': 'not in',
    '8': 'matches',
    '9': 'does not match',
    '10': 'Yes',
    '11': 'No'
}

ACTION_CONDITION_KEYMAP = {
    'formulaid': {'key': 'Label', 'vmap': None},
}

ACTION_EVAL_TYPE_KEYMAP = {
    '0': 'and/or',
    '1': 'and',
    '2': 'or',
    '3': 'custom expression'
}

OPERATION_CONDITION_KEYMAP = {
    'formulaid': {'key': 'Label', 'vmap': None},
    'operator': {'key': 'Operator', 'vmap': None},
    'value': {'key': 'Value', 'vmap': None},
}

HOST_INVENTORY_KEYMAP = {
    '4': 'alias',
    '11': 'asset_tag',
    '28': 'chassis',
    '23': 'contact',
    '32': 'contract_number',
    '47': 'date_hw_decomm',
    '46': 'date_hw_expiry',
    '45': 'date_hw_install',
    '44': 'date_hw_purchase',
    '34': 'deployment_status',
    '14': 'hardware',
    '15': 'hardware_full',
    '39': 'host_netmask',
    '38': 'host_networks',
    '40': 'host_router',
    '30': 'hw_arch',
    '33': 'installer_name',
    '24': 'location',
    '25': 'location_lat',
    '26': 'location_lon',
    '12': 'macaddress_a',
    '13': 'macaddress_b',
    '29': 'model',
    '3': 'name',
    '27': 'notes',
    '41': 'oob_ip',
    '42': 'oob_netmask',
    '43': 'oob_router',
    '5': 'os',
    '6': 'os_full',
    '7': 'os_short',
    '61': 'poc_1_cell',
    '58': 'poc_1_email',
    '57': 'poc_1_name',
    '63': 'poc_1_notes',
    '59': 'poc_1_phone_a',
    '60': 'poc_1_phone_b',
    '62': 'poc_1_screen',
    '68': 'poc_2_cell',
    '65': 'poc_2_email',
    '64': 'poc_2_name',
    '70': 'poc_2_notes',
    '66': 'poc_2_phone_a',
    '67': 'poc_2_phone_b',
    '69': 'poc_2_screen',
    '8': 'serialno_a',
    '9': 'serialno_b',
    '48': 'site_address_a',
    '49': 'site_address_b',
    '50': 'site_address_c',
    '51': 'site_city',
    '53': 'site_country',
    '56': 'site_notes',
    '55': 'site_rack',
    '52': 'site_state',
    '54': 'site_zip',
    '16': 'software',
    '18': 'software_app_a',
    '19': 'software_app_b',
    '20': 'software_app_c',
    '21': 'software_app_d',
    '22': 'software_app_e',
    '17': 'software_full',
    '10': 'tag',
    '1': 'type',
    '2': 'type_full',
    '35': 'url_a',
    '36': 'url_b',
    '37': 'url_c',
    '31': 'vendor',
    '4': 'alias',
    '11': 'asset_tag',
    '28': 'chassis',
    '23': 'contact',
    '32': 'contract_number',
    '47': 'date_hw_decomm',
    '46': 'date_hw_expiry',
    '45': 'date_hw_install',
    '44': 'date_hw_purchase',
    '34': 'deployment_status',
    '14': 'hardware',
    '15': 'hardware_full',
    '39': 'host_netmask',
    '38': 'host_networks',
    '40': 'host_router',
    '30': 'hw_arch',
    '33': 'installer_name',
    '24': 'location',
    '25': 'location_lat',
    '26': 'location_lon',
    '12': 'macaddress_a',
    '13': 'macaddress_b',
    '29': 'model',
    '3': 'name',
    '27': 'notes',
    '41': 'oob_ip',
    '42': 'oob_netmask',
    '43': 'oob_router',
    '5': 'os',
    '6': 'os_full',
    '7': 'os_short',
    '61': 'poc_1_cell',
    '58': 'poc_1_email',
    '57': 'poc_1_name',
    '63': 'poc_1_notes',
    '59': 'poc_1_phone_a',
    '60': 'poc_1_phone_b',
    '62': 'poc_1_screen',
    '68': 'poc_2_cell',
    '65': 'poc_2_email',
    '64': 'poc_2_name',
    '70': 'poc_2_notes',
    '66': 'poc_2_phone_a',
    '67': 'poc_2_phone_b',
    '69': 'poc_2_screen',
    '8': 'serialno_a',
    '9': 'serialno_b',
    '48': 'site_address_a',
    '49': 'site_address_b',
    '50': 'site_address_c',
    '51': 'site_city',
    '53': 'site_country',
    '56': 'site_notes',
    '55': 'site_rack',
    '52': 'site_state',
    '54': 'site_zip',
    '16': 'software',
    '18': 'software_app_a',
    '19': 'software_app_b',
    '20': 'software_app_c',
    '21': 'software_app_d',
    '22': 'software_app_e',
    '17': 'software_full',
    '10': 'tag',
    '1': 'type',
    '2': 'type_full',
    '35': 'url_a',
    '36': 'url_b',
    '37': 'url_c',
    '31': 'vendor',
}

HOST_IPMI_AUTHTYPE_KEYMAP = {
    '-1': 'default',
    '0': 'none',
    '1': 'password',
    '2': 'MD2',
    '3': 'MD5',
    '4': 'straight',
    '5': 'OEM',
    '6': 'RMCP+',
}
HOST_IPMI_PRIVILEGE_KEYMAP = {
    '1': 'callback',
    '2': 'user',
    '3': 'operator',
    '4': 'admin',
    '5': 'OEM',
}

HOST_KEYMAP = {
    'host': {'key': 'Host name', 'vmap': None},
    'name': {'key': 'Visible name', 'vmap': None},
    'status': {'key': 'Enable', 'vmap': BOOL_KEYMAP_REVERSE},
}
HOST_IPMI_KEYMAP = {
    'ipmi_authtype': {'key': 'Authentication algorithm', 'vmap': HOST_IPMI_AUTHTYPE_KEYMAP},
    'ipmi_privilege': {'key': 'Privilege level', 'vmap': HOST_IPMI_PRIVILEGE_KEYMAP},
    'ipmi_username': {'key': 'Username', 'vmap': None},
    'ipmi_password': {'key': 'Password', 'vmap': None},
}

HOST_ENCRYPTION_TO_KEYMAP = {
    '1': 'none',
    '2': 'PSK',
    '4': 'certificate'
}

HOST_ENCRYPTION_KEYMAP = {
    'tls_connect': {'key': 'Connections to host', 'vmap': HOST_ENCRYPTION_TO_KEYMAP},
}

HOST_INTERFACE_TYPE_KEYMAP = {
    '1': 'Agent',
    '2': 'SNMP',
    '3': 'IPMI',
    '4': 'JMX',
}

HOST_INTERFACE_USEIP_KEYMAP = {
    '0': 'DNS',
    '1': 'IP',
}

HOST_INTERFACE_KEYMAP = {
    'type': {'key': 'Type', 'vmap': HOST_INTERFACE_TYPE_KEYMAP},
    'ip': {'key': 'IP address', 'vmap': None},
    'dns': {'key': 'DNS name', 'vmap': None},
    'useip': {'key': 'Connect to host', 'vmap': HOST_INTERFACE_USEIP_KEYMAP},
    'port': {'key': 'Port', 'vmap': None},
}

SNMP_VERSION_KEYMAP = {
    '1': 'SNMPv1',
    '2': 'SNMPv2c',
    '3': 'SNMPv3',
}

HOST_INTERFACE_DETAILS_V1V2_KEYMAP = {
    'version': {'key': 'SNMP version', 'vmap': SNMP_VERSION_KEYMAP},
    'community': {'key': 'Community', 'vmap': None},
    'max_repetitions': {'key': 'Max repetition count', 'vmap': None},
    'bulk': {'key': 'Use combined requests', 'vmap': BOOL_KEYMAP},
}

HOST_INTERFACE_DETAILS_V3_SECURITY_LEVEL_KEYMAP = {
    '0': 'NoAuthNoPriv',
    '1': 'AuthNoPriv',
    '2': 'AuthPriv',
}

HOST_INTERFACE_DETAILS_V3_AUTH_PROTOCOL_KEYMAP = {
    '0': 'MD5',
    '1': 'SHA1',
    '2': 'SHA224',
    '3': 'SHA256',
    '4': 'SHA384',
    '5': 'SHA512',
}

HOST_INTERFACE_DETAILS_V3_PRIV_PROTOCOL_KEYMAP = {
    '0': 'DES',
    '1': 'AES128',
    '2': 'AES192',
    '3': 'AES256',
    '4': 'AES192C',
    '5': 'AES256C',
}

HOST_INTERFACE_DETAILS_V3_KEYMAP = {
    'version': {'key': 'SNMP version', 'vmap': SNMP_VERSION_KEYMAP},
    'max_repetitions': {'key': 'Max repetition count', 'vmap': None},
    'bulk': {'key': 'Use combined requests', 'vmap': BOOL_KEYMAP},
    'contextname': {'key': 'Context name', 'vmap': None},
    'securityname': {'key': 'Security name', 'vmap': None},
    'securitylevel': {'key': 'Security level', 'vmap': HOST_INTERFACE_DETAILS_V3_SECURITY_LEVEL_KEYMAP},
    'authprotocol': {'key': 'Authentication protocol', 'vmap': HOST_INTERFACE_DETAILS_V3_AUTH_PROTOCOL_KEYMAP},
    'privprotocol': {'key': 'Privacy protocol', 'vmap': HOST_INTERFACE_DETAILS_V3_PRIV_PROTOCOL_KEYMAP},
    'authpassphrase': {'key': 'Authentication passphrase', 'vmap': None},
    'privpassphrase': {'key': 'Privacy passphrase', 'vmap': None},
}

VALUEMAP_TYPE_KEYMAP = {
    '0': 'equals',
    '1': 'is greater than or equals',
    '2': 'is less than or equals',
    '3': 'in range',
    '4': 'regexp',
    '5': 'default'
}

TEMPLATE_KEYMAP = {
    'host': {'key': 'Host name', 'vmap': None},
    'name': {'key': 'Visible name', 'vmap': None},
}

ITEM_TYPE_KEYMAP = {
    '0': 'Zabbix agent',
    '2': 'Zabbix trapper',
    '3': 'Simple check',
    '5': 'Zabbix internal',
    '7': 'Zabbix agent (active)',
    '9': 'Web item',
    '10': 'External check',
    '11': 'Database monitor',
    '12': 'IPMI agent',
    '13': 'SSH agent',
    '14': 'TELNET agent',
    '15': 'Calculated',
    '16': 'JMX agent',
    '17': 'SNMP trap',
    '18': 'Dependent item',
    '19': 'HTTP agent',
    '20': 'SNMP agent',
    '21': 'Script',
    '22': 'Browser',
}

ITEM_VALUE_TYPE_KEYMAP = {
    '0': 'numeric float',
    '1': 'character',
    '2': 'log',
    '3': 'numeric unsigned',
    '4': 'text',
    '5': 'binary',
}

ITEM_PREPROCESSING_KEYMAP = {
    '1': 'Custom multiplier',
    '2': 'Right trim',
    '3': 'Left trim',
    '4': 'Trim',
    '5': 'Regular expression',
    '6': 'Boolean to decimal',
    '7': 'Octal to decimal',
    '8': 'Hexadecimal to decimal',
    '9': 'Simple change',
    '10': 'Change per second',
    '11': 'XML XPath',
    '12': 'JSONPath',
    '13': 'In range',
    '14': 'Matches regular expression',
    '15': 'Does not match regular expression',
    '16': 'Check for error in JSON',
    '17': 'Check for error in XML',
    '18': 'Check for error using regular expression',
    '19': 'Discard unchanged',
    '20': 'Discard unchanged with heartbeat',
    '21': 'JavaScript',
    '22': 'Prometheus pattern',
    '23': 'Prometheus to JSON',
    '24': 'CSV to JSON',
    '25': 'Replace',
    '26': 'Check unsupported',
    '27': 'XML to JSON',
    '28': 'SNMP walk value',
    '29': 'SNMP walk to JSON',
    '30': 'SNMP get value',
}

ITEM_PREPROCESSING_HANDLER_KEYMAP = {
    '0': 'Error message is set by Zabbix server',
    '1': 'Discard value',
    '2': 'Set custom value',
    '3': 'Set custom error message',
}

ITEM_KEYMAP = {
    'name': {'key': 'Name', 'vmap': None},
    'key_': {'key': 'Key', 'vmap': None},
    'type': {'key': 'Type', 'vmap': ITEM_TYPE_KEYMAP},
    'value_type': {'key': 'Type of information', 'vmap': ITEM_VALUE_TYPE_KEYMAP},
    'units': {'key': 'Units', 'vmap': None},
    'history': {'key': 'History', 'vmap': None},
    'trends': {'key': 'Trends', 'vmap': None},
    'valuemapid': {'key': 'Value mapping', 'vmap': None},
    'inventory_link': {'key': 'Populates host inventory field', 'vmap': None},
    'status': {'key': 'Enabled', 'vmap': BOOL_KEYMAP_REVERSE},
    'logtimefmt': {'key': 'Log time format', 'vmap': None},
}

PREPROCESSING_KEYMAP = {
    'type': {'key': 'Type', 'vmap': ITEM_PREPROCESSING_KEYMAP},
    'error_handler': {'key': 'Error handler', 'vmap': ITEM_PREPROCESSING_HANDLER_KEYMAP},
    'params': {'key': 'Parameters', 'vmap': None},
    'error_handler_params': {'key': 'Error handler parameters', 'vmap': None},
}

OPTIONAL_ITEM_KEYMAP = {
    'Zabbix agent': {
        'delay': {'key': 'Update interval', 'vmap': None},
        'timeout': {'key': 'Timeout', 'vmap': None},
    },
    'Zabbix trapper': {
        'trapper_hosts': {'key': 'Allowed hosts', 'vmap': None},
    },
    'Simple check': {
        'delay': {'key': 'Update interval', 'vmap': None},
        'timeout': {'key': 'Timeout', 'vmap': None},
        'username': {'key': 'Username', 'vmap': None},
        'password': {'key': 'Password', 'vmap': None},
    },
    'Zabbix internal': {
        'delay': {'key': 'Update interval', 'vmap': None},
    },
    'Zabbix agent (active)': {
        'delay': {'key': 'Update interval', 'vmap': None},
        'timeout': {'key': 'Timeout', 'vmap': None},
    },
    'SNMP agent': {
        'delay': {'key': 'Update interval', 'vmap': None},
        'snmp_oid': {'key': 'SNMP OID', 'vmap': None},
    },
    'SNMP trap': {
    },
    'Calculated': {
        'params': {'key': 'Formula', 'vmap': None},
        'delay': {'key': 'Update interval', 'vmap': None},
    },
    'Dependent item': {
        'master_itemid': {'key': 'Master item', 'vmap': None},
    }
}

TRIGGER_RECOVERY_MODE_KEYMAP = {
    '0': 'Expression',
    '1': 'Recovery expression',
    '2': 'None'
}

TRIGGER_TYPE_KEYMAP = {
    '0': 'Single',
    '1': 'Multiple',
}

TRIGGER_CORRELATION_MODE_KEYMAP = {
    '0': 'All problems',
    '1': 'All problems if tag values match',
}

TRIGGER_KEYMAP = {
    'description': {'key': 'Name', 'vmap': None},
    'event_name': {'key': 'Event name', 'vmap': None},
    'opdata': {'key': 'Operational data', 'vmap': None},
    'priority': {'key': 'Severity', 'vmap': TRIGGER_SEVERITY_KEYMAP},
    'expression': {'key': 'Expression', 'vmap': None},
    'recovery_mode': {'key': 'OK event generation', 'vmap': TRIGGER_RECOVERY_MODE_KEYMAP},
    'recovery_expression': {'key': 'Recovery expression', 'vmap': None},
    'type': {'key': 'PROBLEM event generation mode', 'vmap': TRIGGER_TYPE_KEYMAP},
    'correlation_mode': {'key': 'OK event closes', 'vmap': TRIGGER_CORRELATION_MODE_KEYMAP},
    'correlation_tag': {'key': 'Tag for matching', 'vmap': None},
    'manual_close': {'key': 'Allow manual close', 'vmap': BOOL_KEYMAP},
    'url_name': {'key': 'Menu entry name', 'vmap': None},
    'url': {'key': 'Menu entry URL', 'vmap': None},
    'status': {'key': 'Enabled', 'vmap': BOOL_KEYMAP_REVERSE},
}

GRAPH_TYPE_KEYMAP = {
    '0': 'Normal',
    '1': 'Stacked',
    '2': 'Pie',
    '3': 'Exploded',
}

GRAPH_AXIS_TYPE_KEYMAP = {
    '0': 'Calculated',
    '1': 'Fixed',
    '2': 'item'
}

GRAPH_KEYMAP = {
    'name': {'key': 'Name', 'vmap': None},
    'width': {'key': 'Width', 'vmap': None},
    'height': {'key': 'Height', 'vmap': None},
    'show_legend': {'key': 'Show legend', 'vmap': BOOL_KEYMAP},
    'show_work_period': {'key': 'Show working time', 'vmap': BOOL_KEYMAP},
    'show_triggers': {'key': 'Show triggers', 'vmap': BOOL_KEYMAP},
    'show_3d': {'key': 'Show 3D', 'vmap': BOOL_KEYMAP},
    'percent_left': {'key': 'Percentile line(left)', 'vmap': BOOL_KEYMAP},
    'percent_right': {'key': 'Percentile line(right)', 'vmap': BOOL_KEYMAP},
    'ymax_type': {'key': 'Y axis MAX value', 'vmap': GRAPH_AXIS_TYPE_KEYMAP},
    'ymax_itemid': {'key': 'Y axis MAX value item', 'vmap': None},
    'ymin_type': {'key': 'Y axis MIN value', 'vmap': GRAPH_AXIS_TYPE_KEYMAP},
    'ymin_itemid': {'key': 'Y axis MIN value item', 'vmap': None},
    'yaxismax': {'key': 'Y axis MAX', 'vmap': None},
    'yaxismin': {'key': 'Y axis MIN', 'vmap': None},
    'graphtype': {'key': 'Graph type', 'vmap': GRAPH_TYPE_KEYMAP},
}

GRAPH_ITEM_CALC_FNC_KEYMAP = {
    '1': 'min',
    '2': 'avg',
    '4': 'max',
    '7': 'all',
    '9': 'last',
}

GRAPH_ITEM_DRAWTYPE_KEYMAP = {
    '0': 'line',
    '1': 'filled region',
    '2': 'bold line',
    '3': 'dot',
    '4': 'dashed line',
    '5': 'gradient line'
}

GRAPH_ITEM_TYPE_KEYMAP = {
    '0': 'simple',
    '2': 'graph sum'
}

GRAPH_YAXISSIDE_KEYMAP = {
    '0': 'left',
    '1': 'right'
}

GLAPH_ITEM_KEYMAP = {
    'itemid': {'key': 'Item', 'vmap': None},
    'color': {'key': 'Color', 'vmap': None},
    'calc_fnc': {'key': 'Function', 'vmap': None},
    'drawtype': {'key': 'Draw type', 'vmap': GRAPH_ITEM_DRAWTYPE_KEYMAP},
    'yaxisside': {'key': 'Y axis side', 'vmap': GRAPH_YAXISSIDE_KEYMAP},
    'type': {'key': 'Type', 'vmap': GRAPH_ITEM_TYPE_KEYMAP},
}

LLD_LIFETIME_KEYMAP = {
    '0': 'After',
    '1': 'Never',
    '2': 'Immediately',
}

LLD_OVERRIDE_STOP_KEYMAP = {
    '0': 'Continue override',
    '1': 'Stop processing',
}

LLD_OVERRIDE_KEYMAP = {
    'stop': {'key': 'If filter matches', 'vmap': LLD_OVERRIDE_STOP_KEYMAP},
    'name': {'key': 'Name', 'vmap': None},
}

LLD_OPERATION_OBJECT_KEYMAP = {
    '0': 'Item prototype',
    '1': 'Trigger prototype',
    '2': 'Graph prototype',
    '3': 'Host prototype',
}

LLD_OPERATION_KEYMAP = {
    'operationobject': {'key': 'Object', 'vmap': LLD_OPERATION_OBJECT_KEYMAP},
    'operator': {'key': 'Operator', 'vmap': ACTION_CONDITION_OPERATOR_KEYMAP},
    'value': {'key': 'Value', 'vmap': None},
    'opstatus': {'key': 'Enabled', 'vmap': None},
    'opdiscover': {'key': 'Discovery', 'vmap': None},
    'opperiod': {'key': 'Update interval', 'vmap': None},
    'ophistory': {'key': 'History', 'vmap': None},
    'optrends': {'key': 'Trends', 'vmap': None},
    'optags': {'key': 'Tags', 'vmap': None},
}
