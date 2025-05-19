from libs.gatherer.linux_oss_gatherer import LinuxOSSGatherer
from libs.excelize.excelizer import Excelizer
from libs.excelize.contents import ContentSheet, ContentCollection, ParentContent, ValueContent, MatrixContent, MatrixContentCollection


class LinuxOSSExcelizer(Excelizer):
    def __init__(self,
                 gatherer: LinuxOSSGatherer,
                 write_file: str,
                 client_name: str = "",
                 contractor_name: str = "",
                 project_name: str = "",
                 document_number: str = "",
                 system_name: str = "",
                 document_name: str = "",
                 document_title: str = "",
                 ):
        super().__init__(
            write_file, client_name,
            contractor_name, project_name, document_number,
            system_name, document_name, document_title,
        )
        self._gatherer = gatherer

    @property
    def gatherer(self):
        return self._gatherer

    def __build_httpd_content_block(self, conf, indent) -> ContentCollection:
        contents = []
        for _v in conf:
            if 'tag_name' in _v and 'tag_args' in _v and 'config' in _v:
                child = self.__build_httpd_content_block(
                    _v['config'], indent+1)
                contents.append(
                    ParentContent(
                        f"<{_v['tag_name']} {_v['tag_args']}>",
                        child, indent
                    )
                )
            else:
                contents.append(
                    ParentContent(
                        _v['key'], [
                            ValueContent(items=[_v['value']])
                        ], indent
                    )
                )

        return contents

    def build_httpd_content(self, index):
        httpd = self.gatherer.get_httpd()
        contents = []

        for _k, _v in httpd['conf'].items():
            conf_content = self.__build_httpd_content_block(_v, 0)
            contents.append(
                ContentCollection(
                    _k, conf_content, index
                ))
            index += 1

        for _k, _v in httpd['conf_module'].items():
            conf_module_content = self.__build_httpd_content_block(_v, 0)
            contents.append(
                ContentCollection(
                    _k, conf_module_content, index
                )
            )
            index += 1

        return contents

    def __build_postfix_main_content(self, conf, index):
        l1_items = []
        for _v in conf:
            l1_items.append(
                ParentContent(
                    _v['key'], [
                        ValueContent(items=[_v['value']])], 0
                )
            )

        return ContentCollection(
            'main.cf', l1_items, index
        )

    def __build_postfix_master_content(self, conf, index):
        services = []
        types = []
        privs = []
        unprivs = []
        chroots = []
        wakeups = []
        maxprocs = []
        commands = []
        options = []
        remarks = []

        for _v in conf:
            services.append(_v['service'])
            types.append(_v['type'])
            privs.append(_v['priv'])
            unprivs.append(_v['unpriv'])
            chroots.append(_v['chroot'])
            wakeups.append(_v['wakeup'])
            maxprocs.append(_v['maxproc'])
            commands.append(_v['command'])
            remarks.append('')
            if len(_v['option']) == 0:
                options.append('-')
            elif len(_v['option']) == 1:
                options.append(_v['option'][0])
            else:
                options.append(_v['option'][0])
                for _option in _v['option'][1:]:
                    services.append('')
                    types.append('')
                    privs.append('')
                    unprivs.append('')
                    chroots.append('')
                    wakeups.append('')
                    maxprocs.append('')
                    commands.append('')
                    options.append(_option)
                    remarks.append('')

        content = MatrixContentCollection(
            'master.cf', [
                MatrixContent('service', services),
                MatrixContent('type', types),
                MatrixContent('priv', privs),
                MatrixContent('unpriv', unprivs),
                MatrixContent('chroot', chroots),
                MatrixContent('wakeup', wakeups),
                MatrixContent('maxproc', maxprocs),
                MatrixContent('command', commands),
                MatrixContent('option', options, width=20),
                MatrixContent('備考', remarks, width=12)
            ], index
        )
        return content

    def __build_postfix_alias_content(self, conf, index):
        l1_items = []
        for _v in conf:
            l1_items.append(
                ParentContent(
                    _v['addr'], [
                        ValueContent(items=[_v['alias']])], 0
                )
            )

        return ContentCollection(
            'aliases', l1_items, index, key_title='アドレス', value_title='エイリアス'
        )

    def __build_postfix_access_content(self, conf, index):
        l1_items = []
        for _v in conf:
            l1_items.append(
                ParentContent(
                    _v['addr'], [
                        ValueContent(items=[_v['action']])], 0
                )
            )

        return ContentCollection(
            'access', l1_items, index, key_title='アドレス', value_title='アクセス権限'
        )

    def __build_postfix_transport_content(self, conf, index):
        l1_items = []
        for _v in conf:
            l1_items.append(
                ParentContent(
                    _v['addr'], [
                        ValueContent(items=[_v['transport']])], 0
                )
            )

        return ContentCollection(
            'transport', l1_items, index, key_title='アドレス', value_title='トランスポート'
        )

    def __build_postfix_virtual_content(self, conf, index):
        l1_items = []
        for _v in conf:
            l1_items.append(
                ParentContent(
                    _v['addr'], [
                        ValueContent(items=[_v['virtual']])], 0
                )
            )

        return ContentCollection(
            'virtual', l1_items, index, key_title='アドレス', value_title='仮想アドレス/エイリアス'
        )

    def build_postfix_content(self, index):
        postfix = self.gatherer.get_postfix()

        contents = []
        contents.append(
            self.__build_postfix_main_content(postfix['main.cf'], index)
        )
        contents.append(
            self.__build_postfix_master_content(postfix['master.cf'], index+1)
        )
        contents.append(
            self.__build_postfix_alias_content(postfix['aliases'], index+2)
        )
        contents.append(
            self.__build_postfix_access_content(postfix['access'], index+3)
        )
        contents.append(
            self.__build_postfix_transport_content(
                postfix['transport'], index+4)
        )
        contents.append(
            self.__build_postfix_virtual_content(postfix['virtual'], index+5)
        )

        return contents

    def __build_postgresql_conf_content(self, conf, index):
        l1_items = []
        for _v in conf:
            l1_items.append(
                ParentContent(
                    _v['key'], [
                        ValueContent(items=[_v['value']])], 0
                )
            )

        return ContentCollection(
            'postgresql.conf', l1_items, index
        )

    def __build_postgresql_hba_conf_content(self, conf, index):
        types = []
        databases = []
        users = []
        addresses = []
        methods = []
        remarks = []

        for _v in conf:
            types.append(_v['type'])
            databases.append(_v['database'])
            users.append(_v['user'])
            addresses.append(_v['address'])
            methods.append(_v['method'])
            remarks.append('')

        content = MatrixContentCollection(
            'pg_hba.conf', [
                MatrixContent('TYPE', types),
                MatrixContent('DATABASE', databases, width=14),
                MatrixContent('USER', users, width=14),
                MatrixContent('ADDRESS', addresses, width=16),
                MatrixContent('METHOD', methods, width=7),
                MatrixContent('備考', remarks, width=16)
            ], index
        )

        return content

    def build_postgresql_content(self, index):
        postgresql_conf = self.gatherer.get_postgresql()

        contents = []
        contents.append(
            self.__build_postgresql_conf_content(
                postgresql_conf['conf'], index)
        )
        contents.append(
            self.__build_postgresql_hba_conf_content(
                postgresql_conf['hba_conf'], index+1)
        )

        return contents

    def build_mysql_content(self, index):
        mysql_conf = self.gatherer.get_mysql()

        contents = []
        i = 0
        for _k, _v in mysql_conf.items():
            l1_items = []
            for section, conf in _v.items():
                l2_items = [
                    ParentContent(
                        c['key'], [
                            ValueContent(items=[c['value']])], 1
                    ) for c in conf
                ]
                l1_items.append(
                    ParentContent(section, l2_items, 0)
                )

            contents.append(
                ContentCollection(
                    _k, l1_items, index + i
                )
            )
            i += 1

        return contents

    def build_squid_content(self, index):
        squid_conf = self.gatherer.get_squid()

        squid_content = ContentCollection(
            'squid.conf', [
                ParentContent(
                    c['key'], [
                        ValueContent(items=[c['value']])
                    ], 0
                ) for c in squid_conf
            ], index
        )

        return [squid_content]

    def __build_named_conf_block(self, conf, indent):
        contents = []
        for _c in conf:
            _k = _c.get('key')
            _v = _c.get('value')
            _i = _c.get('items')

            if _v and isinstance(_v, str):
                contents.append(
                    ParentContent(
                        _k, [ValueContent(items=[_v])], indent
                    )
                )
            elif _v and isinstance(_v, list):
                contents.append(
                    ParentContent(
                        _k,
                        self.__build_named_conf_block(_v, indent+1),
                        indent
                    )
                )
            elif _i and isinstance(_i, str):
                contents.append(
                    ValueContent(items=[_i])
                )

        return contents

    def build_named_conf_content(self, index):
        named_conf = self.gatherer.get_named()

        contents = []
        for k, v in named_conf.items():
            contents.append(
                ContentCollection(
                    k, self.__build_named_conf_block(v, 0), index
                )
            )

        return contents

    def __build_named_zone_content_block(self, zones):
        contents = []
        for k, v in zones.items():
            l1_items = []
            for record in v:
                record_type = ""
                record_items = []
                for _k, _v in record.items():
                    if _k == 'type':
                        record_type = _v
                    else:
                        record_items.append(
                            ParentContent(
                                _k, [ValueContent(items=[_v])], 2
                            )
                        )

                l1_items.append(
                    ParentContent(
                        record_type, record_items, 1)
                )

            contents.append(
                ParentContent(
                    k, l1_items, 0
                )
            )

        return contents

    def build_named_zone_content(self, index):
        named_zone = self.gatherer.get_zonefiles()

        forward_contents = self.__build_named_zone_content_block(
            named_zone['forward'])
        reverse_contents = self.__build_named_zone_content_block(
            named_zone['reverse'])

        i = 0

        forward_content = ContentCollection(
            '正引きゾーン設定', forward_contents, index
        )
        reverse_content = ContentCollection(
            '逆引きゾーン設定', reverse_contents, index+1
        )

        return [forward_content, reverse_content]

    def build_nfs_content(self, index):
        nfs_conf = self.gatherer.get_nfs_server()

        l1_items = []
        for _k, _v in nfs_conf['idmap_conf'].items():
            l1_items.append(
                ParentContent(
                    _k, [
                        ParentContent(
                            c['key'], [ValueContent(items=[c['value']])], 1
                        ) for c in _v
                    ], 0
                )
            )

        idmap_content = ContentCollection(
            'idmapd.conf', l1_items, index
        )

        exports = []
        pathes = []
        options = []
        remarks = []
        for _v in nfs_conf['exports']:
            pathes.append(_v['path'])
            options.append(_v['options'])
            exports.append(_v['export'])
            remarks.append('')

        export_content = MatrixContentCollection(
            'exports', [
                MatrixContent('PATH', pathes, width=16),
                MatrixContent('EXPORT', exports, width=16),
                MatrixContent('OPTIONS', options, width=16),
                MatrixContent('備考', remarks, width=16)
            ], index+1
        )

        return [idmap_content, export_content]

    def build_samba_sheet(self, index):
        conf = self.gatherer.get_samba()

        l1_items = []
        for k, v in conf['conf'].items():
            l1_items.append(
                ParentContent(
                    k, [
                        ParentContent(
                            c['key'], [ValueContent(items=[c['value']])], 1)
                        for c in v
                    ], 0
                )
            )

        content = ContentCollection(
            'smb.conf', l1_items, index
        )

        return [content]

    def build_sssd_sheet(self, index):
        conf = self.gatherer.get_sssd()

        contents = []
        for k, v in conf.items():
            contents.append(
                ParentContent(
                    k, [
                        ParentContent(
                            _k, [ValueContent(items=[_v])], 1
                        ) for _k, _v in v.items()
                    ], 0
                )
            )

        return [ContentCollection(
            'sssd.conf', contents, index
        )]

    def build_main_sheet(self):
        self.add_sheet(
            ContentSheet(
                'HTTPD設定', self.build_httpd_content(1), 'HTTPD設定', 1
            )
        )

        self.add_sheet(
            ContentSheet(
                'Postfix設定', self.build_postfix_content(1), 'Postfix設定', 2
            )
        )

        self.add_sheet(
            ContentSheet(
                'PostgreSQL設定', self.build_postgresql_content(
                    1), 'PostgreSQL設定', 3
            )
        )

        self.add_sheet(
            ContentSheet(
                'MySQL設定', self.build_mysql_content(1), 'MySQL設定', 4
            )
        )

        self.add_sheet(
            ContentSheet(
                'Squid設定', self.build_squid_content(1), 'Squid設定', 5
            )
        )

        named_contents = []
        named_contents.extend(
            self.build_named_conf_content(2)
        )
        named_contents.extend(self.build_named_zone_content(1))
        self.add_sheet(
            ContentSheet(
                'Bind設定', named_contents, 'Bind設定', 6
            )
        )

        self.add_sheet(
            ContentSheet(
                'NFS設定', self.build_nfs_content(1), 'NFS設定', 7
            )
        )

        self.add_sheet(
            ContentSheet(
                'Samba設定', self.build_samba_sheet(1), 'Samba設定', 8
            )
        )

        self.add_sheet(
            ContentSheet(
                'SSSD設定', self.build_sssd_sheet(1), 'SSSD設定', 9
            )
        )
