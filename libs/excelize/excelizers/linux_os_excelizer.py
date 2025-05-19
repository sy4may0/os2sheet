from libs.gatherer.linux_os_gatherer import LinuxOSGatherer
from libs.excelize.excelizer import Excelizer
from libs.excelize.contents import ContentSheet, ContentCollection, ParentContent, ValueContent, MatrixContent, MatrixContentCollection


class LinuxOSExcelizer(Excelizer):
    def __init__(self,
                 gatherer: LinuxOSGatherer,
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
            system_name, document_name, document_title
        )
        self._gatherer = gatherer

    @property
    def gatherer(self):
        return self._gatherer

    def build_base_settings(self, index):
        items = []
        rhel_version = ValueContent(items=[self.gatherer.get_rhel_version()])
        hostname = ValueContent(items=[self.gatherer.get_hostname()])
        domainname = ValueContent(items=[self.gatherer.get_domainname()])
        default_target = ValueContent(
            items=[self.gatherer.get_default_target()])
        timezone = ValueContent(items=[self.gatherer.get_timezone()])
        locale = ValueContent(items=[self.gatherer.get_locale()])
        items = []
        items.append(ParentContent('OSバージョン', [rhel_version], 0))
        items.append(ParentContent('ホスト名', [hostname], 0))
        items.append(ParentContent('ドメイン名', [domainname], 0))
        items.append(ParentContent('systemdデフォルトターゲット', [default_target], 0))
        items.append(ParentContent('タイムゾーン', [timezone], 0))
        items.append(ParentContent('ロケール', [locale], 0))
        content = ContentCollection('Linux基本設定', items, index)

        return content

    def build_selinux_content(self, index):
        items = []
        for key, value in self.gatherer.get_selinux().items():
            data = ValueContent(items=[value])
            category = ParentContent(key, [data], 0)
            items.append(category)
        content = ContentCollection('SELinux設定', items, index)
        return content

    def build_nmcli_content(self, index):
        large_items = []
        for l1_key, l1_value in self.gatherer.get_nmcli_connections().items():
            medium_items = []
            for l2_key, l2_value in l1_value.items():
                data = ValueContent(items=[l2_value])
                category = ParentContent(l2_key, [data], 1)
                medium_items.append(category)
            large_items.append(ParentContent(l1_key, medium_items, 0))

        content = ContentCollection(
            'ネットワーク設定(NetworkManager)', large_items, index)
        return content

    def build_hadware_content(self, index):
        cpu_items = []
        cpu_data = self.gatherer.get_cpu()
        mem_data = self.gatherer.get_mem()
        cpu_items.append(ParentContent(
            'モデル', [ValueContent(items=[cpu_data['Model name']])], 1
        ))
        cpu_items.append(ParentContent(
            'ソケット数', [ValueContent(items=[cpu_data['Socket(s)']])], 1
        ))
        cpu_items.append(ParentContent(
            'コア数', [ValueContent(items=[cpu_data['Core(s) per socket']])], 1
        ))
        cpu_items.append(ParentContent(
            'スレッド数', [ValueContent(items=[cpu_data['Thread(s) per core']])], 1
        ))
        mem_items = [
            ParentContent('メモリ容量', [ValueContent(items=[mem_data])], 1)
        ]
        content = ContentCollection('ハードウェア情報', [
            ParentContent('CPU', cpu_items, 0),
            ParentContent('メモリ', mem_items, 0)
        ], index)

        return content

    def build_disk_content(self, index):
        disk_data = self.gatherer.get_localdisks()
        l0_items = []
        for l1_key, l1_value in disk_data.items():
            l1_items = []
            l1_items.append(ParentContent('ディスク名',
                            [ValueContent(items=[l1_value['name']])], 1
            ))
            l1_items.append(ParentContent('ディスク容量',
                            [ValueContent(items=[l1_value['size']])], 1
            ))
            for l2_value in l1_value['partition']:
                l2_items = []
                l2_items.append(ParentContent('パーティション名',
                                [ValueContent(items=[l2_value['name']])], 2
                ))
                l2_items.append(ParentContent('サイズ',
                                [ValueContent(items=[l2_value['size']])], 2
                ))
                l2_items.append(ParentContent('UUID',
                                [ValueContent(items=[l2_value['uuid']])], 2
                ))

                if not l2_value['volumes']:
                    l2_items.append(ParentContent('マウントポイント',
                                    [ValueContent(
                                        items=[l2_value['mountpoint']])], 2
                    ))
                    l1_items.append(ParentContent(
                        f"パーティション:{l2_value['name']}", l2_items, 1))
                    continue

                for l3_value in l2_value['volumes']:
                    l3_items = []
                    l3_items.append(ParentContent('ボリューム名',
                                                  [ValueContent(
                                                      items=[l3_value['name']])], 3
                                                  ))
                    l3_items.append(ParentContent('タイプ',
                                                  [ValueContent(
                                                      items=[l3_value['type']])], 3
                                                  ))
                    l3_items.append(ParentContent('サイズ',
                                                  [ValueContent(
                                                      items=[l3_value['size']])], 3
                                                  ))
                    l3_items.append(ParentContent('マウントポイント',
                                                  [ValueContent(
                                                      items=[l3_value['mountpoint']])], 3
                                                  ))
                    l3_items.append(ParentContent('uuid',
                                                  [ValueContent(
                                                      items=[l3_value['uuid']])], 3
                                                  ))

                    l2_items.append(ParentContent(
                        f"論理ボリューム:{l3_value['name']}", l3_items, 2))

                l1_items.append(ParentContent(
                    f"パーティション:{l2_value['name']}", l2_items, 1))

            l0_items.append(ParentContent(
                f"ディスク:{l1_value['name']}", l1_items, 0
            ))
        content = ContentCollection('ローカルディスク', l0_items, index)
        return content

    def build_fstab_content(self, index):
        fstab_data = self.gatherer.get_fstab()
        devices = []
        mountpoints = []
        filesystems = []
        options = []
        dumps = []
        fscks = []
        remarks = []
        for l1_value in fstab_data:
            devices.append(l1_value['device'])
            mountpoints.append(l1_value['mountpoint'])
            filesystems.append(l1_value['filesystem'])
            options.append(l1_value['options'])
            dumps.append(l1_value['dump'])
            fscks.append(l1_value['fsck'])
            remarks.append("")

        content = MatrixContentCollection(
            'fstab設定', [
                MatrixContent('デバイス', devices, width=18),
                MatrixContent('マウントポイント', mountpoints, width=8),
                MatrixContent('ファイルシステム', filesystems, width=6),
                MatrixContent('オプション', options, width=14),
                MatrixContent('ダンプ', dumps, width=5),
                MatrixContent('fsck', fscks, width=5),
                MatrixContent('備考', remarks, width=16)
            ], index
        )
        return content

    def build_group_content(self, index):
        groups = self.gatherer.get_groups()

        names = []
        gids = []
        remarks = []
        for group in groups:
            names.append(group['name'])
            gids.append(group['gid'])
            remarks.append("")

        content = MatrixContentCollection(
            'グループ', [
                MatrixContent('グループ名', names, width=18),
                MatrixContent('GID', gids, width=8),
                MatrixContent('備考', remarks, width=16)
            ], index
        )

        return content

    def build_user_content(self, index):
        users = self.gatherer.get_users()

        names = []
        uids = []
        groups = []
        gids = []
        subgroups = []
        homes = []
        shells = []
        descrs = []
        remarks = []
        for user in users:
            names.append(user['name'])
            uids.append(user['uid'])
            groups.append(user['group']['name'])
            gids.append(user['group']['gid'])
            subgroups.append(', '.join([g['name'] for g in user['groups']]))
            homes.append(user['home_directory'])
            shells.append(user['shell'])
            descrs.append(user['description'])
            remarks.append("")

        content = MatrixContentCollection(
            'ユーザー', [
                MatrixContent('ユーザー名', names, width=8),
                MatrixContent('UID', uids, width=3),
                MatrixContent('グループ', groups, width=8),
                MatrixContent('GID', gids, width=3),
                MatrixContent('サブグループ', subgroups, width=10),
                MatrixContent('ホーム', homes, width=8),
                MatrixContent('シェル', shells, width=6),
                MatrixContent('説明', descrs, width=10),
                MatrixContent('備考', remarks, width=10)
            ], index
        )

        return content

    def build_install_package_content(self, index):
        rpm_packages = self.gatherer.get_rpm_packages()
        l1_items = []
        for l1_key, l1_value in rpm_packages.items():
            l2_items = []
            for l2_value in l1_value:
                l2_items.append(
                    ValueContent(
                        items=[
                            f"{l2_value['name']} ({l2_value['version']})"
                        ]
                    )
                )
            l1_items.append(
                ParentContent(
                    l1_key, l2_items, 0
                )
            )
        content = ContentCollection(
            'インストールパッケージ', l1_items, index,
            key_title='インストールソース', value_title='パッケージ (バージョン)'
        )

        return content

    def build_systemd_units_content(self, index):
        systemd_units = self.gatherer.get_systemd_units()
        l1_items = []
        for unit in systemd_units:
            l1_items.append(
                ParentContent(unit['name'], [
                    ValueContent(items=[unit['state']])
                ], 0)
            )

        content = ContentCollection(
            'systemdユニット', l1_items, index
        )

        return content

    def build_rsyslog_content(self, index):
        rsyslog = self.gatherer.get_rsyslog()
        l1_items = []
        for key, value in rsyslog.items():
            l2_items = []
            for v in value:
                l2_items.append(ValueContent(items=[v]))
            l1_items.append(
                ParentContent(key, l2_items, 0))

        content = ContentCollection(
            'rsyslog設定', l1_items, index
        )

        return content

    def build_sshd_content(self, index):
        sshd = self.gatherer.get_sshd()
        l1_items = []
        for key, value in sshd.items():
            l2_items = []
            for v in value:
                l2_items.append(ParentContent(
                    v['key'], [
                        ValueContent(items=[v['value']])
                    ], 1
                ))
            l1_items.append(
                ParentContent(key, l2_items, 0)
            )

        content = ContentCollection(
            'sshd設定', l1_items, index
        )

        return content

    def build_logrotate_content(self, index):
        logrotate = self.gatherer.get_logrotate()

        l1_items = []
        for key, value in logrotate.items():
            l2_items = []
            l2_items.append(
                ParentContent(
                    '対象ファイル', [
                        ValueContent(items=[_tf]) for _tf in value['target']
                    ], 1
                )
            )
            l2_items.append(
                ParentContent(
                    '設定', [
                        ValueContent(items=[_cf]) for _cf in value['config']
                    ], 1
                )
            )
            l1_items.append(
                ParentContent(key, l2_items, 0)
            )

        content = ContentCollection(
            'logrotate設定', l1_items, index
        )

        return content

    def build_cron_content(self, index):
        cron = self.gatherer.get_cron()

        l1_items = []
        for key, value in cron.items():
            env_items = []
            schedule_items = []
            for _e in value['environment']:
                env_items.append(
                    ParentContent(_e['env'], [
                        ValueContent(items=[_e['value']])
                    ], 2)
                )
            for _s in value['job']:
                schedule_items.append(
                    ParentContent(_s['schedule'], [
                        ValueContent(items=[_s['command']])
                    ], 2)
                )
            l2_items = [
                ParentContent('環境変数', env_items, 1),
                ParentContent('スケジュール', schedule_items, 1)
            ]
            l1_items.append(
                ParentContent(key, l2_items, 0)
            )

        content = ContentCollection(
            'cron設定', l1_items, index
        )

        return content

    def build_chrony_content(self, index):
        chrony = self.gatherer.get_chrony()

        l1_items = []
        for _cf in chrony:
            l1_items.append(
                ParentContent(_cf['key'], [
                    ValueContent(items=[_cf['value']])
                ])
            )
        content = ContentCollection(
            'chrony設定', l1_items, index
        )

        return content

    def build_dnf_content(self, index):
        dnf = self.gatherer.get_dnf()

        l1_items = []
        for key, value in dnf.items():
            l2_items = []
            for _v in value:
                l2_items.append(
                    ParentContent(
                        _v['key'], [
                            ValueContent(items=[_v['value']])
                        ], 1
                    )
                )
            l1_items.append(
                ParentContent(key, l2_items, 0)
            )

        content = ContentCollection(
            'dnf設定', l1_items, index
        )

        return content

    def build_dnf_repo_content(self, index):
        dnf_repo = self.gatherer.get_dnf_repo()

        l1_items = []
        for key, value in dnf_repo.items():
            l2_items = []
            for key, value in value.items():
                l3_items = [
                    ParentContent(
                        _v['key'], [ValueContent(items=[_v['value']])], 2
                    ) for _v in value
                ]

                l2_items.append(
                    ParentContent(
                        key, l3_items, 1
                    )
                )
            l1_items.append(
                ParentContent(key, l2_items, 0)
            )

        content = ContentCollection(
            'dnfリポジトリ設定', l1_items, index
        )

        return content

    def build_sudoers_content(self, index):
        sudoers = self.gatherer.get_sudoers()

        l1_items = []
        for key, value in sudoers.items():
            l1_items.append(
                ParentContent(
                    key, [
                        ValueContent(items=[v]) for v in value
                    ]
                )
            )

        content = ContentCollection(
            'sudoers設定', l1_items, index
        )

        return content

    def build_firewalld_content(self, index):
        firewalld = self.gatherer.get_firewalld()

        l1_items = []
        for key, value in firewalld.items():
            interface_contents = ParentContent('インターフェース', [
                ValueContent(items=[_v]) for _v in value['interfaces']
            ], 1)
            services_contents = ParentContent('サービス', [
                ValueContent(items=[_v]) for _v in value['services']
            ], 1)

            l1_items.append(
                ParentContent(f"ゾーン: {key}", [
                    interface_contents,
                    services_contents
                ], 0)
            )

        content = ContentCollection('firewalld設定', l1_items, index)

        return content

    def build_firewalld_rich_rule_content(self, index):
        firewalld = self.gatherer.get_firewalld()

        zone_list = []
        rule_list = []
        remark_list = []
        for zone, value in firewalld.items():
            for rule in value['rich_rules']:
                zone_list.append(zone)
                rule_list.append(rule)
                remark_list.append('')

        zone_contents = MatrixContent('ゾーン', zone_list, width=8)
        rule_contents = MatrixContent('ルール', rule_list, width=48)
        remark_contents = MatrixContent('備考', remark_list, width=16)

        content = MatrixContentCollection(
            'firewalldリッチルール一覧', [
                zone_contents,
                rule_contents,
                remark_contents
            ], index)

        return content

    def build_sysconfig_grub_content(self, index):
        sysconfig_grub = self.gatherer.get_sysconfig_grub()

        l1_items = []
        for _v in sysconfig_grub:
            l1_items.append(
                ParentContent(
                    _v['key'], [
                        ValueContent(items=[_v['value']])
                    ], 1
                )
            )

        parent = ParentContent('/etc/sysconfig/grub', l1_items, 0)

        content = ContentCollection(
            'grub設定', [parent], index
        )

        return content

    def build_sysctl_content(self, index):
        sysctl = self.gatherer.get_sysctl()

        l1_items = []
        for key, value in sysctl.items():
            l2_items = [
                ParentContent(
                    conf['key'], [ValueContent(items=[conf['value']])], 1)
                for conf in value
            ]
            l1_items.append(
                ParentContent(key, l2_items, 0)
            )

        content = ContentCollection(
            'sysctl設定', l1_items, index
        )

        return content

    def build_pam_content(self, index):
        pam = self.gatherer.get_pam()

        authselect_profile = ParentContent(
            'authselectプロファイル', [
                ValueContent(items=[pam['profile']])
            ], 0
        )

        authselect_features = ParentContent(
            'authselect機能', [
                ValueContent(items=[feature]) for feature in pam['features']
            ], 0
        )

        authselect_content = ContentCollection(
            'authselect設定', [
                authselect_profile,
                authselect_features
            ], index
        )

        contents = [authselect_content]

        i = 0
        for path, v in pam['prof_pam_conf'].items():
            col = MatrixContentCollection(
                path, [
                    MatrixContent('タイプ', v['module_types'], width=5),
                    MatrixContent('コントロール', v['controls'], width=16),
                    MatrixContent('モジュール', v['modules'], width=8),
                    MatrixContent('引数', v['arguments'], width=20),
                    MatrixContent('条件', v['conditions'], width=18),
                    MatrixContent('備考', v['remarks'], width=14)
                ], index + i
            )
            contents.append(col)
            i += 1

        return contents

    def build_main_sheet(self):
        general_contents = []
        general_contents.append(self.build_base_settings(1))
        general_contents.append(self.build_selinux_content(2))
        general_contents.append(self.build_hadware_content(3))
        general_contents.append(self.build_nmcli_content(4))
        general_contents.append(self.build_disk_content(5))
        general_contents.append(self.build_fstab_content(6))
        general_contents.append(self.build_sysconfig_grub_content(7))
        general_contents.append(self.build_sysctl_content(8))

        self.add_sheet(
            ContentSheet('Linux基本設定', general_contents, 'Linux基本設定')
        )

        self.add_sheet(
            ContentSheet('ユーザー・グループ',
                         [
                             self.build_group_content(1),
                             self.build_user_content(2),
                             self.build_sudoers_content(3)
                         ],
                         'ユーザー・グループ')
        )

        self.add_sheet(
            ContentSheet('インストールパッケージ',
                         [self.build_install_package_content(1)],
                         'インストールパッケージ')
        )

        self.add_sheet(
            ContentSheet('systemdユニット',
                         [self.build_systemd_units_content(1)],
                         'systemdユニット')
        )

        optional_contents = [
            self.build_rsyslog_content(1),
            self.build_sshd_content(2),
            self.build_logrotate_content(3),
            self.build_cron_content(4),
            self.build_chrony_content(5),
        ]
        self.add_sheet(
            ContentSheet('基本OSS設定', optional_contents, '基本OSS設定')
        )

        dnf_contents = [
            self.build_dnf_content(1),
            self.build_dnf_repo_content(2)
        ]
        self.add_sheet(
            ContentSheet(
                'DNFパッケージマネージャー設定',
                dnf_contents, 'DNFパッケージマネージャー設定')
        )

        firewalld_contents = [
            self.build_firewalld_content(1),
            self.build_firewalld_rich_rule_content(2)
        ]
        self.add_sheet(
            ContentSheet(
                'firewalld設定', firewalld_contents,
                'firewalld設定'
            )
        )

        self.add_sheet(
            ContentSheet(
                'PAM設定', self.build_pam_content(1),
                'PAM設定'
            )
        )
