from .gatherer import Gatherer
from libs.defines import CONF_HTTPD, CONF_HTTPD_D, CONF_HTTPD_MODULES, CONF_HTTPD_ROOT
from libs.defines import CONF_POSTFIX_MAIN, CONF_POSTFIX_MASTER, CONF_POSTFIX_ACCESS, CONF_POSTFIX_ALIASES, CONF_POSTFIX_TRANSPORT, CONF_POSTFIX_VIRTUAL
from libs.defines import CONF_POSTGRESQL_CONF, CONF_PG_HBA_CONF
from libs.defines import CONF_MYSQL, CONF_MYSQL_D
from libs.defines import CONF_SQUID
from libs.defines import CONF_NAMED, ROOTDIR_NAMED_CHROOT
from libs.defines import CONF_NFS_IDMAP, CONF_NFS_EXPORT
from libs.defines import CONF_SMB
from libs.defines import CONF_SSSD
import dns
from dns import zone
import re
import configparser


class LinuxOSSGatherer(Gatherer):
    def __init__(
        self,
        host: str,
        user: str,
        port: int = 22,
        password: str = None,
        root_password: str = None,
        keyfile: str = None,
    ):
        """
        Initialize the LinuxOSSGatherer class.

        Args:
            host (str): The hostname of the target system.
            user (str): The username for SSH access to the target system.
            port (int): The port number for SSH access to the target system.
            password (str): The password for SSH access to the target system.
            root_password (str): The root password for SSH access to the target system.
            keyfile (str): The path to the SSH private key file for SSH access to the target system.
        """
        super().__init__(
            host, user, port, password,
            keyfile, root_password=root_password)

        self.httpd = None
        self.postfix = None
        self.postgresql = None
        self.mysql = None
        self.squid = None
        self.named = None
        self.named_zonefiles = None
        self.nfs_server = None
        self.samba = None
        self.sssd = None

    def __read_httpd_block(self, lines, i) -> tuple[dict, int]:
        """
        Read an HTTPD block from the given lines.

        Args:
            lines (list[str]): The lines of the HTTPD configuration file.
            i (int): The index of the line to start reading from.

        Returns:
            A tuple containing:
            - A dictionary representing the HTTPD block.
            - The number of lines read.
        """
        result = {
            'tag_name': '',
            'tag_args': '',
            'config': []
        }
        length = 0

        tag_match = re.match(r'^<(\w+)\s*(.*?)>$', lines[i].strip())
        result['tag_name'] = tag_match.group(1)
        result['tag_args'] = tag_match.group(2)

        length += 1
        i += 1

        while i < len(lines):
            if re.match('^<.+>$', lines[i].strip()):
                _r, _l = self.__read_httpd_block(lines, i)
                result['config'].append(_r)
                length += _l
                i += _l

            else:
                part = lines[i].split()
                result['config'].append({
                    'key': part[0],
                    'value': ' '.join(part[1:])
                })
                length += 1
                i += 1

            if re.match(f"</{result['tag_name']}>", lines[i].strip()):
                length += 1
                break

        return result, length

    def __read_httpd_conf(self, conf_path) -> list[dict]:
        conf_text = self.runner.exec(f'cat {conf_path}')
        lines = self.remove_comment(conf_text)
        result = []

        i = 0
        while i < len(lines):
            if re.match('^<.+>$', lines[i].strip()):
                _block_result, length = self.__read_httpd_block(lines, i)
                result.append(_block_result)
                i += length
            else:
                part = lines[i].split()
                result.append({
                    'key': part[0],
                    'value': ' '.join(part[1:])
                })
                i += 1

        return result

    def get_httpd(self) -> dict[str, list[dict]]:
        """
        Retrieve the contents of the httpd configuration files.

        Returns:
            A dictionary with the path of each httpd configuration file as the key and a list of dictionaries as the value.
            Each dictionary in the list represents a configuration option in the file.
        """
        if self.httpd:
            return self.httpd

        result = {
            'conf': {},
            'conf_module': {},
        }

        conf_targets = [CONF_HTTPD]
        module_targets = []
        httpd_conf_d = self.runner.exec(
            f'find {CONF_HTTPD_D} | egrep -v "{CONF_HTTPD_D}$"')
        httpd_conf_mod_d = self.runner.exec(
            f'find {CONF_HTTPD_MODULES} | egrep -v "{CONF_HTTPD_MODULES}$"')

        for _f in httpd_conf_d.splitlines():
            if _f.endswith('.conf'):
                conf_targets.append(_f)

        for _f in httpd_conf_mod_d.splitlines():
            if _f.endswith('.conf'):
                module_targets.append(_f)

        for conf_path in conf_targets:
            result['conf'][conf_path.removeprefix(
                CONF_HTTPD_ROOT)] = self.__read_httpd_conf(conf_path)

        for conf_path in module_targets:
            result['conf_module'][conf_path.removeprefix(
                CONF_HTTPD_ROOT)] = self.__read_httpd_conf(conf_path)

        self.httpd = result
        return self.httpd

    def __read_main_cf(self, conf_text) -> list[dict]:
        """
        Read the contents of the main.cf file.

        Args:
            conf_text (str): The contents of the main.cf file.

        Returns:
            A list of dictionaries representing the configuration options in the file.
        """
        lines = self.remove_comment(conf_text)

        result = []
        multiline_tmp = None
        multiline_values = []
        for line in lines:
            part = line.strip().split('=')
            if (not re.match('^\s+', line) and
               (len(part) < 2 or not part[1])):
                multiline_tmp = part[0].strip()
                continue

            if re.match('^\s+', line) and multiline_tmp:
                multiline_values.append(line.strip())
                continue

            if len(part) >= 2 and multiline_tmp and multiline_values:
                result.append({
                    'key': multiline_tmp,
                    'value': '\n'.join(multiline_values)
                })
                multiline_tmp = None
                multiline_values = []

            result.append({
                'key': part[0].strip(),
                'value': '='.join(part[1:]).strip()
            })

        return result

    def __read_master_cf(self, conf_text) -> list[dict]:
        """
        Read the contents of the master.cf file.

        Args:
            conf_text (str): The contents of the master.cf file.

        Returns:
            A list of dictionaries representing the configuration options in the file.
        """
        lines = self.remove_comment(conf_text)
        result = []
        for line in lines:
            part = line.split()
            if re.match('^\s+', line) and result:
                result[-1]['option'].append(line.strip())

            if len(part) >= 8:
                result.append({
                    "service": part[0],
                    "type": part[1],
                    "priv": part[2],
                    "unpriv": part[3],
                    "chroot": part[4],
                    "wakeup": part[5],
                    "maxproc": part[6],
                    "command": part[7],
                    "option": []
                })

        return result

    def __read_aliases(self, conf_text) -> list[dict]:
        """
        Read the contents of the aliases file.

        Args:
            conf_text (str): The contents of the aliases file.

        Returns:
            A list of dictionaries representing the configuration options in the file.
        """
        lines = self.remove_comment(conf_text)

        result = []
        for line in lines:
            part = line.split()
            result.append({
                'addr': part[0],
                'alias': ' '.join(part[1:])
            })

        return result

    def __read_access(self, conf_text) -> list[dict]:
        """
        Read the contents of the access file.

        Args:
            conf_text (str): The contents of the access file.
        """
        lines = self.remove_comment(conf_text)

        result = []
        for line in lines:
            part = line.split()
            result.append({
                'addr': part[0],
                'action': ' '.join(part[1:])
            })

        return result

    def __read_transport(self, conf_text) -> list[dict]:
        """
        Read the contents of the transport file.

        Args:
            conf_text (str): The contents of the transport file.
        """
        lines = self.remove_comment(conf_text)

        result = []
        for line in lines:
            part = line.split()
            result.append({
                'addr': part[0],
                'transport': ' '.join(part[1:])
            })

        return result

    def __read_virtual(self, conf_text) -> list[dict]:
        """
        Read the contents of the virtual file.

        Args:
            conf_text (str): The contents of the virtual file.
        """
        lines = self.remove_comment(conf_text)

        result = []
        for line in lines:
            part = line.split()
            result.append({
                'addr': part[0],
                'virtual': ' '.join(part[1:])
            })

        return result

    def get_postfix(self) -> dict[str, list[dict]]:
        """
        Retrieve the contents of the postfix configuration files.

        Returns:
            A dictionary with the path of each postfix configuration file as the key and a list of dictionaries as the value.
            Each dictionary in the list represents a configuration option in the file.
            The keys are the configuration file names and the values are lists of dictionaries.
        """
        if self.postfix:
            return self.postfix

        result = {
            'main.cf': None,
            'master.cf': None,
            'aliases': None,
            'access': None
        }

        main_cf = self.runner.exec(f'cat {CONF_POSTFIX_MAIN}')
        result['main.cf'] = self.__read_main_cf(main_cf)

        master_cf = self.runner.exec(f'cat {CONF_POSTFIX_MASTER}')
        result['master.cf'] = self.__read_master_cf(master_cf)

        aliases = self.runner.exec(f'cat {CONF_POSTFIX_ALIASES}')
        result['aliases'] = self.__read_aliases(aliases)

        access = self.runner.exec(f'cat {CONF_POSTFIX_ACCESS}')
        result['access'] = self.__read_access(access)

        transport = self.runner.exec(f'cat {CONF_POSTFIX_TRANSPORT}')
        result['transport'] = self.__read_transport(transport)

        virtual = self.runner.exec(f'cat {CONF_POSTFIX_VIRTUAL}')
        result['virtual'] = self.__read_virtual(virtual)

        self.postfix = result
        return self.postfix

    def __read_postgresql_hba_conf(self, conf_text) -> list[dict]:
        """
        Read the contents of the postgresql hba configuration file.

        Args:
            conf_text (str): The contents of the postgresql hba configuration file.
        """
        lines = self.remove_comment(conf_text)

        result = []
        for line in lines:
            part = line.split()
            result.append({
                'type': part[0],
                'database': part[1],
                'user': part[2],
                'address': None,
                'method': None
            })

            if not re.match('^[a-z0-9-]+$', part[3].strip()):
                result[-1]['address'] = part[3]
                result[-1]['method'] = part[4]
            else:
                result[-1]['address'] = ''
                result[-1]['method'] = part[3]

        return result

    def get_postgresql(self) -> dict[str, list[dict]]:
        """
        Retrieve the contents of the postgresql configuration files.

        Returns:
            A dictionary with the path of each postgresql configuration file as the key and a list of dictionaries as the value.
            Each dictionary in the list represents a configuration option in the file.
        """
        if self.postgresql:
            return self.postgresql

        result = {
            'conf': None,
            'hba_conf': None
        }

        conf = self.runner.exec(f'cat {CONF_POSTGRESQL_CONF}')
        result['conf'] = self.parse_ini_style_nosection(conf)

        hba_conf = self.runner.exec(f'cat {CONF_PG_HBA_CONF}')
        result['hba_conf'] = self.__read_postgresql_hba_conf(hba_conf)

        self.postgresql = result
        return self.postgresql

    def get_mysql(self) -> dict[str, list[dict]]:
        """
        Retrieve the contents of the mysql configuration files.

        Returns:
            A dictionary with the path of each mysql configuration file as the key and a list of dictionaries as the value.
            Each dictionary in the list represents a configuration option in the file.
        """
        if self.mysql:
            return self.mysql

        result = {}

        target_files = [CONF_MYSQL]
        mysql_conf_d = self.runner.exec(
            f'find {CONF_MYSQL_D} | egrep -v "{CONF_MYSQL_D}$"'
        )
        for _f in mysql_conf_d.splitlines():
            target_files.append(_f)

        for target_file in target_files:
            conf_text = self.runner.exec(f'cat {target_file}')
            conf_dict = self.parse_ini_style(conf_text)

            result[target_file] = conf_dict

        self.mysql = result
        return self.mysql

    def get_squid(self) -> dict[str, list[dict]]:
        """
        Retrieve the contents of the squid configuration files.

        Returns:
            A dictionary with the path of each squid configuration file as the key and a list of dictionaries as the value.
            Each dictionary in the list represents a configuration option in the file.
        """
        if self.squid:
            return self.squid

        result = {}

        conf = self.runner.exec(f'cat {CONF_SQUID}')
        result = self.parse_unix_style(conf)

        self.squid = result
        return self.squid

    def __read_named_conf_block(self, lines, i) -> tuple[list[dict], int]:
        """
        Read a named configuration block from the given lines.

        Args:
            lines (list[str]): The lines of the named configuration file.
            i (int): The index of the line to start reading from.

        Returns:
            A tuple containing:
            - A list of dictionaries representing the configuration options in the block.
            - The number of lines read.
        """
        result = []
        length = 0
        while i < len(lines):
            if lines[i].startswith('}'):
                i += 1
                length += 1
                break

            if not lines[i].endswith(';') and lines[i+1].startswith('{'):
                opt_key = lines[i]
                i += 2
                length += 2
                b_result, b_length = self.__read_named_conf_block(lines, i)
                result.append({
                    'key': opt_key,
                    'value': b_result
                })
                i += b_length
                length += b_length
                continue

            if re.match('.+\s+.+;$', lines[i]):
                part = lines[i].split()
                result.append({
                    'key': part[0],
                    'value': ' '.join(part[1:])
                })
                i += 1
                length += 1
                continue

            if re.match('.+;$', lines[i]):
                result.append({
                    'items': lines[i]
                })
                i += 1
                length += 1
                continue

        return result, length

    def __read_named_conf(self, conf_text) -> list[dict]:
        """
        Read the contents of the named configuration file.

        Args:
            conf_text (str): The contents of the named configuration file.
        """
        lines = [s.strip() for s in
                 self.remove_cstyle_comment(conf_text)]

        result, _ = self.__read_named_conf_block(lines, 0)

        return result

    def get_named(self) -> dict[str, list[dict]]:
        """
        Retrieve the contents of the named configuration files.

        Returns:
            A dictionary with the path of each named configuration file as the key and a list of dictionaries as the value.
            Each dictionary in the list represents a configuration option in the file.
        """
        if self.named:
            return self.named

        result = {}

        conf = self.runner.exec(f'cat {CONF_NAMED}')
        result[CONF_NAMED] = self.__read_named_conf(
            conf.replace('{', '\n{\n').replace(';', ';\n')
        )

        self.named = result
        return self.named

    def __find_zone_files(self) -> list[str]:
        """
        Find the zone files in the named configuration directory.

        Returns:
            A list of the zone files in the named configuration directory.
        """
        conf = self.runner.exec(f'cat {CONF_NAMED}')
        lines = self.remove_comment(
            conf.replace('{', '\n{\n').replace(';', ';\n')
        )

        zonefiles = []
        in_zone = False
        for line in lines:
            match = re.match('directory\s+"(.+)"', line.strip())
            if match:
                directory = match.group(1)

            if line.startswith('zone'):
                in_zone = True
                continue

            if line.startswith('}'):
                in_zone = False
                continue

            if in_zone:
                match = re.match('^file\s+"(.+)"', line.strip())
                if match:
                    zonefiles.append(f"{directory}/{match.group(1)}")

        return zonefiles

    def __read_zonefiles(self, chroot: bool) -> tuple[list[dict], list[dict]]:
        """
        Read the contents of the zone files.

        Args:
            chroot (bool): Whether to read the zone files in the chroot directory.

        Returns:
            A tuple containing:
            - A list of dictionaries representing the zone files.
            - A list of dictionaries representing the reverse zone files.
        """
        if chroot:
            prefix = ROOTDIR_NAMED_CHROOT
        else:
            prefix = ''
        zonefiles = self.__find_zone_files()
        zones = []
        zones_reverse = []
        for _f in zonefiles:
            zone_text = self.runner.exec(f'cat {prefix}{_f}')
            if not zone_text:
                continue
            if re.match(r'^([0-9]+\.)+in-addr\.arpa.*', _f.split('/')[-1]):
                zones_reverse.append({'file': _f, 'text': zone_text})
            else:
                zones.append({'file': _f, 'text': zone_text})

        return zones, zones_reverse

    def read_zonfile_text(self, text: str) -> list[dict]:
        """
        Read the contents of a zone file.

        Args:
            text (str): The contents of the zone file.

        Returns:
            A list of dictionaries representing the records in the zone file.
        """
        _zone = zone.from_text(
            text, check_origin=False,
            origin='dummy@dummy.org'
        )
        records = []

        for name, node in _zone.nodes.items():
            for rdataset in node.rdatasets:
                rtype = dns.rdatatype.to_text(rdataset.rdtype)
                for rdata in rdataset:
                    record = {
                        'name': '@',
                        "ttl": rdataset.ttl,
                        'type': rtype,
                    }

                    if rdataset.rdtype == dns.rdatatype.A:
                        record['name'] = name.to_text()
                        record['address'] = rdata.address
                    elif rdataset.rdtype == dns.rdatatype.PTR:
                        record['name'] = name.to_text()
                        record['ptr'] = rdata.target.to_text()
                    elif rdataset.rdtype == dns.rdatatype.MX:
                        record['name'] = name.to_text()
                        record['priority'] = rdata.preference
                        record['host'] = rdata.exchange.to_text()
                    elif rdataset.rdtype == dns.rdatatype.NS:
                        record['name'] = name.to_text()
                        record['ns'] = rdata.target.to_text()
                    elif rdataset.rdtype == dns.rdatatype.CNAME:
                        record['name'] = name.to_text()
                        record['cname'] = rdata.target.to_text()
                    elif rdataset.rdtype == dns.rdatatype.AAAA:
                        record['name'] = name.to_text()
                        record['address'] = rdata.address
                    elif rdataset.rdtype == dns.rdatatype.TXT:
                        record['name'] = name.to_text()
                        record['text'] = rdata.text
                    elif rdataset.rdtype == dns.rdatatype.SOA:
                        record['name'] = name.to_text()
                        record['mname'] = rdata.mname.to_text()
                        record['rname'] = rdata.rname.to_text()
                        record['serial'] = rdata.serial
                        record['refresh'] = rdata.refresh
                        record['retry'] = rdata.retry
                        record['expire'] = rdata.expire
                        record['minimum'] = rdata.minimum
                    else:
                        record['name'] = name.to_text()
                        record['raw'] = rdata.to_text()

                    records.append(record)

        return records

    def get_zonefiles(self, chroot=True) -> dict[str, list[dict]]:
        """
        Retrieve the contents of the zone files.

        Returns:
            A dictionary with the path of each zone file as the key and a list of dictionaries as the value.
            Each dictionary in the list represents a record in the zone file.
        """
        if self.named_zonefiles:
            return self.named_zonefiles

        zone_texts, zone_reverse_texts = self.__read_zonefiles(chroot)

        result = {}
        result_reverse = {}
        for zone_text in zone_texts:
            result[zone_text['file']] = self.read_zonfile_text(
                zone_text['text'])
        for zone_text in zone_reverse_texts:
            result_reverse[zone_text['file']
                           ] = self.read_zonfile_text(zone_text['text'])

        self.named_zonefiles = {
            'forward': result,
            'reverse': result_reverse
        }

        return self.named_zonefiles

    def __read_exports(self, conf_text) -> list[dict]:
        """
        Read the contents of the exports file.

        Args:
            conf_text (str): The contents of the exports file.

        Returns:
            A list of dictionaries representing the exports in the file.
        """
        lines = self.remove_comment(conf_text)

        result = []
        for line in lines:
            match = re.match(r'\s*(\S+)\s+(.+)\((.*)\)', line)
            if not match:
                continue

            result.append({
                'path': match.group(1),
                'export': match.group(2),
                'options': match.group(3)
            })

        return result

    def get_nfs_server(self) -> dict[str, list[dict]]:
        """
        Retrieve the contents of the nfs server configuration files.

        Returns:
            A dictionary with the path of each nfs server configuration file as the key and a list of dictionaries as the value.
            Each dictionary in the list represents a configuration option in the file.
        """
        if self.nfs_server:
            return self.nfs_server

        result = {}
        idmap_conf = self.runner.exec(f'cat {CONF_NFS_IDMAP}')
        exports = self.runner.exec(f'cat {CONF_NFS_EXPORT}')

        result['idmap_conf'] = self.parse_ini_style(idmap_conf)
        result['exports'] = self.__read_exports(exports)

        self.nfs_server = result
        return self.nfs_server

    def get_samba(self) -> dict[str, list[dict]]:
        """
        Retrieve the contents of the samba configuration files.

        Returns:
            A dictionary with the path of each samba configuration file as the key and a list of dictionaries as the value.
            Each dictionary in the list represents a configuration option in the file.
        """
        if self.samba:
            return self.samba

        result = {}
        smb_conf = self.runner.exec(f'cat {CONF_SMB}')

        result['conf'] = self.parse_ini_style(smb_conf)

        self.samba = result
        return self.samba

    def get_sssd(self) -> dict[str, list[dict]]:
        """
        Retrieve the contents of the sssd configuration files.

        Returns:
            A dictionary with the path of each sssd configuration file as the key and a list of dictionaries as the value.
            Each dictionary in the list represents a configuration option in the file.
        """
        if self.sssd:
            return self.sssd

        sssd_conf = self.runner.exec(f'cat {CONF_SSSD}')
        parser = configparser.ConfigParser()
        parser.read_string(sssd_conf)
        conf_dict = {
            section: dict(parser.items(section))
            for section in parser.sections()
        }

        self.sssd = conf_dict
        return self.sssd
