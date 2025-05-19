from libs.gatherer.gatherer import Gatherer
from zabbix_utils import ZabbixAPI
from cachetools import LRUCache
import json


class ZabbixAPIGatherer(Gatherer):
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
            keyfile,
            root_password=root_password
        )

        self.__zabbix_api_url = zabbix_api_url
        self.__zabbix_api_user = zabbix_api_user
        self.__zabbix_api_password = zabbix_api_password
        self.__zapi = None

        self.__cache = LRUCache(maxsize=256)

        self.__login_zabbix_api()

    def __login_zabbix_api(self):
        if (
            self.__zabbix_api_url is None or
            self.__zabbix_api_user is None or
            self.__zabbix_api_password is None
        ):
            raise Exception('Zabbix API is not set')

        if self.__zapi is None:
            zapi = ZabbixAPI(self.__zabbix_api_url)
            zapi.login(
                user=self.__zabbix_api_user,
                password=self.__zabbix_api_password
            )
            self.__zapi = zapi

    def parse_api_result(self, result: dict, key_map: dict) -> dict:
        """
        Parse the API result to the key map

        Args:
            result (dict): The API result
            key_map (dict): The key map

        Returns:
            dict: The parsed result
        """
        parsed_result = {}

        for key, value in key_map.items():
            if not result.get(key):
                parsed_result[value['key']] = None
                continue

            if value['vmap'] is None:
                parsed_result[value['key']] = result.get(key)
            else:
                parsed_result[value['key']] = value['vmap'][result[key]]

        return parsed_result

    def search_fk_item(self, fk: str, fk_id: int, items: list) -> dict:
        """
        Search the item by the foreign key

        Args:
            fk (str): The foreign key
            fk_id (int): The foreign key id
            items (list): The items

        Returns:
            dict: The item
        """
        for item in items:
            if fk in item.keys() and item[fk] == fk_id:
                return item

        return None

    def cached_zapi_get(self, method: str, **kwargs):
        """
        Get the items by the method.
        Result data is cached.

        Args:
            method (str): The method
            **kwargs: The kwargs

        Returns:
            list: The items
        """
        key = (method, json.dumps(kwargs, sort_keys=True))
        if key not in self.__cache:
            func = getattr(self.__zapi, method).get
            self.__cache[key] = func(**kwargs)
        return self.__cache[key]

    def get_by_filter(self, filter: dict,  method: str, **kwargs):
        """
        Get the items by the filter.
        Result data is cached.

        Args:
            filter (dict): The filter
            method (str): The method

        Returns:
            list: The items
        """
        items = self.cached_zapi_get(method, **kwargs)
        results = []
        for filter_key in filter.keys():
            if not isinstance(filter[filter_key], list):
                filter[filter_key] = [filter[filter_key]]

        for item in items:
            if all(item.get(key) in value for key, value in filter.items()):
                results.append(item)

        return results

    def get_by_dual_layer_filter(
        self,
        l1_filter: dict,
        l2_filter: dict,
        method: str,
        **kwargs
    ):
        items = self.cached_zapi_get(method, filter=l1_filter, **kwargs)
        results = []
        for l2_filter_key in l2_filter.keys():
            if not isinstance(l2_filter[l2_filter_key], list):
                l2_filter[l2_filter_key] = [l2_filter[l2_filter_key]]

        for item in items:
            if all(item.get(key) in value for key, value in l2_filter.items()):
                results.append(item)

        return results

    @property
    def zapi(self):
        return self.__zapi
