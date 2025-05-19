from libs.excelize.contents import StyleSet, Content
from libs.excelize.contents.Collection import Collection
from libs.excelize.utils import apply_border, apply_fill, apply_font
from typing import Dict, Any, Optional, List
from openpyxl.worksheet.worksheet import Worksheet


class CollectionStyleSet(StyleSet):
    """コレクションコンテンツ用のスタイル設定クラス"""

    def __init__(
        self, ref_row: int, config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a new CollectionStyleSet object.

        Args:
            ref_row (int): The row number of the reference cell.
            config (Optional[Dict[str, Any]]): The configuration of the style set.
            length (int): The length of the collection content.

        Raises:
            ValueError: If the configuration is invalid.
        """
        super().__init__(ref_row, config)

    def border(self, worksheet: Worksheet) -> None:
        """
        Apply border to the collection.
        Applies border to the header and content areas.

        Args:
            worksheet (Worksheet): The worksheet to apply the border to.

        Raises:
            ValueError: If the worksheet is invalid or the range is invalid.
        """
        try:
            col_begin = self.config['cols_content_range']['key_begin']
            col_end = self.config['cols_content_range']['remark_end']
            apply_border(
                worksheet,
                col_begin,
                col_end,
                self.ref_row,
                self.ref_row + self.length - 3,
                color=self.config['colorset']['border_sub']
            )
            for fix_range in [
                (self.config['cols_content_range']['key_begin'],
                 self.config['cols_content_range']['key_end']),
                (self.config['cols_content_range']['value_begin'],
                 self.config['cols_content_range']['value_end']),
                (self.config['cols_content_range']['remark_begin'],
                 self.config['cols_content_range']['remark_end']),
            ]:
                apply_border(
                    worksheet,
                    fix_range[0],
                    fix_range[1],
                    self.ref_row,
                    self.ref_row,
                    color=self.config['colorset']['border_sub']
                )
        except (KeyError, ValueError) as e:
            raise ValueError(f"Failed to apply border: {str(e)}") from e

    def fill(self, worksheet: Worksheet) -> None:
        """
        Apply fill to the collection.
        Applies fill to the header and content areas with different colors.

        Args:
            worksheet (Worksheet): The worksheet to apply the fill to.

        Raises:
            ValueError: If the worksheet is invalid or the range is invalid.
        """
        col_begin = self.config['cols_content_range']['key_begin']
        col_end = self.config['cols_content_range']['remark_end']
        apply_fill(
            worksheet,
            col_begin,
            col_end,
            self.ref_row + 1,
            self.ref_row + self.length - 3,
            color=self.config['colorset']['main']
        )

        apply_fill(
            worksheet,
            col_begin,
            col_end,
            self.ref_row,
            self.ref_row,
            color=self.config['colorset']['sub2']
        )

    def font(self, worksheet: Worksheet) -> None:
        """
        Apply font to the collection.
        Applies different fonts to the title and header areas.

        Args:
            worksheet (Worksheet): The worksheet to apply the font to.

        Raises:
            ValueError: If the worksheet is invalid or the range is invalid.
        """
        try:
            col_begin = self.config['cols_content_range']['key_begin']
            col_end = self.config['cols_content_range']['remark_end']
            apply_font(
                worksheet,
                self.config['col_content_index'],
                self.config['col_content_index'],
                self.ref_row - 1,
                self.ref_row - 1,
                font=self.config['fonts']['title']
            )
            apply_font(
                worksheet,
                col_begin,
                col_end,
                self.ref_row,
                self.ref_row,
                font=self.config['fonts']['main']
            )
        except (KeyError, ValueError) as e:
            raise ValueError(f"Failed to apply font: {str(e)}") from e

    def merge(self, worksheet: Worksheet) -> None:
        """
        Not implemented.
        No need to merge cells in the collection content.

        Args:
            worksheet (Worksheet): The worksheet to merge cells in.
        """
        pass


class ContentCollection(Collection):
    """コレクションコンテンツを表すクラス"""

    def __init__(
        self,
        key: str,
        items: List[Content],
        index: int = 0,
        parent_index: int = 0,
        key_title: str = None,
        value_title: str = None,
        remark_title: str = None,
    ):
        """
        Initialize a new ContentCollection object.

        Args:
            key (str): The key of the content.
            items (List[Content]): The child items of the content.
            index (int): The index of the collection.
            parent_index (int): The index of the parent collection.
            key_title (str): The title for the key column.
            value_title (str): The title for the value column.
            remark_title (str): The title for the remark column.

        Raises:
            ValueError: If the configuration is invalid.
        """
        super().__init__(key, items, index, parent_index, type='content_collection')
        self.__key_title = key_title
        self.__value_title = value_title
        self.__remark_title = remark_title

    @property
    def key_title(self) -> str:
        """
        Get the title for the key column.

        Returns:
            str: The title for the key column.
        """
        return self.__key_title

    @property
    def value_title(self) -> str:
        """
        Get the title for the value column.

        Returns:
            str: The title for the value column.
        """
        return self.__value_title

    @property
    def remark_title(self) -> str:
        """
        Get the title for the remark column.

        Returns:
            str: The title for the remark column.
        """
        return self.__remark_title

    @property
    def length(self) -> int:
        """
        Get the length of the collection content.
        The length is calculated based on the sum of all child items' lengths plus header rows.

        Returns:
            int: The length of the collection content.
        """
        return sum([item.length for item in self.items]) + 3

    def write(self, worksheet: Worksheet, ref_row: int) -> None:
        """
        Write the collection content to the worksheet.
        Writes the title, header, and all child items.

        Args:
            worksheet (Worksheet): The worksheet to write the collection content to.
            ref_row (int): The row number of the reference cell.

        Raises:
            ValueError: If the worksheet is invalid or the row is invalid.
        """
        row = ref_row
        if self.style and not isinstance(self.style, CollectionStyleSet):
            raise ValueError("Style is not a CollectionStyleSet")

        if not self.items:
            return

        if not self.style:
            self.set_style(CollectionStyleSet(row))

        if not self.__key_title:
            self.__key_title = self.style.config['titles_content_header']['key']
        if not self.__value_title:
            self.__value_title = self.style.config['titles_content_header']['value']
        if not self.__remark_title:
            self.__remark_title = self.style.config['titles_content_header']['remark']

        worksheet[f'{self.style.config["col_content_index"]}{row}'] = \
            f"{self.parent_index}.{self.index}. {self.key}"
        row += 1

        self.style.set_ref_row(row)
        self.style.set_length(self.length)

        self.style.fill(worksheet)
        self.style.border(worksheet)

        worksheet[f"{self.style.config['cols_content_range']['key_begin']}{row}"] = \
            self.__key_title
        worksheet[f"{self.style.config['cols_content_range']['value_begin']}{row}"] = \
            self.__value_title
        worksheet[f"{self.style.config['cols_content_range']['remark_begin']}{row}"] = \
            self.__remark_title

        row += 1

        for item in self.items:
            item.write(worksheet, row)
            row += item.length

        self.style.font(worksheet)
        self.style.merge(worksheet)
