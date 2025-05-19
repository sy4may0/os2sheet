from typing import List, Dict, Any, Optional
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Font
from abc import ABC, abstractmethod


DEFAULT_STYLE_CONFIG = {
    'colorset': {
        'main': 'FFFFFF',
        'sub1': 'fce4d6',
        'sub2': 'fcd7cf',
        'sub3': 'fcccc0',
        'text': '000000',
        'border_main': '808080',
        'border_sub': '833c0c'
    },
    'fonts_conf': {
        'main': {'name': 'Noto Sans JP', 'size': 10, 'bold': False},
        'title': {'name': 'Noto Sans JP', 'size': 11, 'bold': True},
        'value': {'name': 'BIZ UDゴシック', 'size': 9, 'bold': False}
    },
    'cols_content_range': {
        'key_begin': 'B',
        'key_end': 'Z',
        'value_begin': 'AA',
        'value_end': 'BE',
        'remark_begin': 'BF',
        'remark_end': 'BU'
    },
    'col_sheet_index': 'A',
    'col_content_index': 'B',
    'titles_content_header': {
        'key': '設定項目',
        'value': '値',
        'remark': '備考'
    }
}


class StyleSet(ABC):
    """スタイル設定を管理する抽象クラス"""

    def __init__(
        self, ref_row: int, config: Optional[Dict[str, Any]] = None,
        length: int = 1
    ):
        """
        Initialize a new StyleSet object.

        Args:
            ref_row (int): The reference row for style application.
            config (Optional[Dict[str, Any]]): The style configuration.
        """
        self.__ref_row = ref_row
        self.__length = length
        self.__config = config if config is not None else DEFAULT_STYLE_CONFIG
        self.__validate_config()

    def __validate_config(self) -> None:
        """
        Validate the style configuration.

        Raises:
            ValueError: If the configuration is invalid.
        """
        required_keys = {
            'colorset', 'fonts_conf', 'cols_content_range', 'col_sheet_index',
            'col_content_index', 'titles_content_header'
        }
        if not all(key in self.__config for key in required_keys):
            raise ValueError('Invalid style config: missing required keys')

        if not all(
            key in self.__config['fonts_conf']
            for key in ['main', 'title', 'value']
        ):
            raise ValueError('Invalid font config: missing required keys')

        self.__config['fonts'] = {
            'main': Font(**self.__config['fonts_conf']['main']),
            'title': Font(**self.__config['fonts_conf']['title']),
            'value': Font(**self.__config['fonts_conf']['value'])
        }

    def set_style_config(self, config: Dict[str, Any]) -> None:
        """
        Set the style configuration.

        Args:
            config (Dict[str, Any]): The new style configuration.
            config['fonts_conf'] must contain 'main', 'title', 'value' keys.
            config['colorset'] must contain 'main', 'sub1', 'sub2', 'sub3',
                'text', 'border_main', 'border_sub' keys.
            config['cols_content_range'] must contain 'key_begin', 'key_end',
                'value_begin', 'value_end', 'remark_begin', 'remark_end' keys.
            config['col_sheet_index'] must contain str.
            config['col_content_index'] must contain str.
            config['titles_content_header'] must contain 'key', 'value', 'remark' keys.


        Raises:
            ValueError: If the configuration is invalid.
        """
        self.__config = config
        self.__validate_config()

    def set_ref_row(self, ref_row: int) -> None:
        """
        Set the reference row.
        """
        self.__ref_row = ref_row

    def set_length(self, length: int) -> None:
        """
        Set the length.
        """
        self.__length = length

    @property
    def length(self) -> int:
        return self.__length

    @property
    def ref_row(self) -> int:
        """
        Get the reference row.

        Returns:
            int: The reference row.
        """
        return self.__ref_row

    @property
    def config(self) -> Dict[str, Any]:
        """
        Get the style configuration.

        Returns:
            Dict[str, Any]: The style configuration.
        """
        return self.__config

    @abstractmethod
    def border(self, worksheet: Worksheet) -> None:
        """
        Apply border to cells.
        This method should be implemented by subclasses to define specific border styles.

        Args:
            worksheet (Worksheet): The worksheet to apply the border to.
        """
        pass

    @abstractmethod
    def fill(self, worksheet: Worksheet) -> None:
        """
        Apply fill to cells.
        This method should be implemented by subclasses to define specific fill styles.

        Args:
            worksheet (Worksheet): The worksheet to apply the fill to.
        """
        pass

    @abstractmethod
    def font(self, worksheet: Worksheet) -> None:
        """
        Apply font to cells.
        This method should be implemented by subclasses to define specific font styles.

        Args:
            worksheet (Worksheet): The worksheet to apply the font to.
        """
        pass

    @abstractmethod
    def merge(self, worksheet: Worksheet) -> None:
        """
        Merge cells.
        This method should be implemented by subclasses to define specific merge patterns.

        Args:
            worksheet (Worksheet): The worksheet to merge cells in.
        """
        pass


class Content(ABC):
    """コンテンツの抽象基底クラス"""

    def __init__(
        self,
        key: str,
        items: Optional[List['Content']] = None,
        type: str = 'content',
    ) -> None:
        """
        Initialize a new Content object.

        Args:
            key (str): The key of the content.
            items (Optional[List['Content']]): The items of the content.
        """
        self.__key = key
        self.__items: List['Content'] = items if items is not None else []
        self.__style: Optional[StyleSet] = None
        self.__type = type

    @property
    def key(self) -> str:
        """
        Get the key of the content.

        Returns:
            str: The key of the content.
        """
        return self.__key

    @property
    def items(self) -> List['Content']:
        """
        Get the items of the content.

        Returns:
            List['Content']: The items of the content.
        """
        return self.__items

    @property
    def type(self) -> str:
        """
        Get the type of the content.
        """
        return self.__type

    @property
    @abstractmethod
    def length(self) -> int:
        """
        Get the length of the content.

        Returns:
            int: The length of the content.
        """
        pass

    @property
    def style(self) -> Optional[StyleSet]:
        """
        Get the style of the content.
        """
        return self.__style

    def add_item(self, item: 'Content') -> None:
        """
        Add an item to the content.

        Args:
            item ('Content'): The item to add.
        """
        self.__items.append(item)

    def set_style(self, style: StyleSet) -> None:
        """
        Set the style of the content.
        """
        self.__style = style

    @abstractmethod
    def write(
        self,
        worksheet: Worksheet,
        ref_row: int
    ) -> None:
        """
        Write the content to the worksheet.

        Args:
            worksheet (Worksheet): The worksheet to write to.
            style (StyleSet): The style set to use.
            ref_row (int): The reference row.
        """
        pass

    def __repr__(self) -> str:
        """
        Return a string representation of the content.

        Returns:
            str: The string representation.
        """
        return (
            f"{self.__class__.__name__}"
            f"(key={self.__key}, items={self.__items})"
        )

    def get_dict(self) -> Dict[str, Any]:
        """
        Get the dictionary representation of the content.
        Recursively converts all child items to their dictionary representation.

        Returns:
            Dict[str, Any]: The dictionary representation containing the key and
                a list of dictionary representations of child items.
        """
        return {
            'key': self.__key,
            'items': [item.get_dict() for item in self.__items],
            'type': self.__type
        }
