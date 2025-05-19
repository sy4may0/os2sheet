from libs.excelize.contents import StyleSet, Content
from libs.excelize.utils import apply_fill, apply_border, apply_font
from openpyxl.worksheet.worksheet import Worksheet
from typing import Dict, Any, Optional, List
from openpyxl.utils import column_index_from_string


class ValueStyleSet(StyleSet):
    """値コンテンツ用のスタイル設定クラス"""

    def __init__(self, ref_row: int, config: Optional[Dict[str, Any]] = None):
        """
        ValueStyleSet is a style set for ValueContent.

        Args:
            ref_row (int): The row number of the reference cell.
            config (Optional[Dict[str, Any]]): The configuration of the style set.

        Raises:
            ValueError: If the configuration is invalid.
        """
        super().__init__(ref_row, config)
        self.set_ref_row(ref_row - 1)

    def border(self, worksheet: Worksheet) -> None:
        """
        Apply border to the value content.
        Applies borders to value and remark columns.

        Args:
            worksheet (Worksheet): The worksheet object.

        Raises:
            ValueError: If the worksheet is invalid or the range is invalid.
        """
        try:
            for fix_range in [
                (self.config['cols_content_range']['value_begin'],
                 self.config['cols_content_range']['value_end']),
                (self.config['cols_content_range']['remark_begin'],
                 self.config['cols_content_range']['remark_end'])
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
        Apply fill to the value content.
        Applies fill to value and remark columns.

        Args:
            worksheet (Worksheet): The worksheet object.

        Raises:
            ValueError: If the worksheet is invalid or the range is invalid.
        """
        try:
            for fix_range in [
                (self.config['cols_content_range']['value_begin'],
                 self.config['cols_content_range']['value_end']),
                (self.config['cols_content_range']['remark_begin'],
                 self.config['cols_content_range']['remark_end'])
            ]:
                apply_fill(
                    worksheet,
                    fix_range[0],
                    fix_range[1],
                    self.ref_row,
                    self.ref_row,
                    color=self.config['colorset']['main']
                )
        except (KeyError, ValueError) as e:
            raise ValueError(f"Failed to apply fill: {str(e)}") from e

    def font(self, worksheet: Worksheet) -> None:
        """
        Apply font to the value content.
        Applies font to value and remark columns.

        Args:
            worksheet (Worksheet): The worksheet object.

        Raises:
            ValueError: If the worksheet is invalid or the range is invalid.
        """
        try:
            for fix_range in [
                (self.config['cols_content_range']['value_begin'],
                 self.config['cols_content_range']['value_end']),
                (self.config['cols_content_range']['remark_begin'],
                 self.config['cols_content_range']['remark_end'])
            ]:
                apply_font(
                    worksheet,
                    fix_range[0],
                    fix_range[1],
                    self.ref_row,
                    self.ref_row,
                    font=self.config['fonts']['value']
                )
        except (KeyError, ValueError) as e:
            raise ValueError(f"Failed to apply font: {str(e)}") from e

    def merge(self, worksheet: Worksheet) -> None:
        """
        Merge cells in the value content.
        Merges cells in value and remark columns.

        Args:
            worksheet (Worksheet): The worksheet object.

        Raises:
            ValueError: If the worksheet is invalid or the range is invalid.
        """
        try:
            for fix_range in [
                (self.config['cols_content_range']['value_begin'],
                 self.config['cols_content_range']['value_end']),
                (self.config['cols_content_range']['remark_begin'],
                 self.config['cols_content_range']['remark_end'])
            ]:
                worksheet.merge_cells(
                    start_row=self.ref_row,
                    start_column=column_index_from_string(fix_range[0]),
                    end_row=self.ref_row,
                    end_column=column_index_from_string(fix_range[1])
                )
        except (KeyError, ValueError) as e:
            raise ValueError(f"Failed to merge cells: {str(e)}") from e


class ValueContent(Content):
    """値コンテンツを表すクラス"""

    def __init__(
        self,
        key: str = '-',
        items: Optional[List[str]] = None,
    ):
        """
        ValueContent is a content for value.

        Args:
            key (str): Unused argument.
            items (Optional[List[str]]): The items of the content.

        Raises:
            ValueError: If the items list is invalid.
        """
        super().__init__('value', items, type='value')

    @property
    def length(self) -> int:
        """
        The length of the value content.

        Returns:
            int: The length of the value content (always 1).
        """
        return 1

    def add_item(self, item: str) -> None:
        if self.items:
            raise ValueError("ValueContent does not support adding items")
        super().add_item(item)

    def write(self, worksheet: Worksheet, ref_row: int) -> None:
        """
        Write the value content to the worksheet.

        Args:
            worksheet (Worksheet): The worksheet object.
            ref_row (int): The row number of the worksheet.

        Raises:
            ValueError: If the worksheet is invalid or the row is invalid.
        """
        row = ref_row
        if self.style and not isinstance(self.style, ValueStyleSet):
            raise ValueError("Style is not a ValueStyleSet")

        try:
            if not self.items or not self.items[0]:
                self.add_item("N/A")

            if not self.style:
                self.set_style(ValueStyleSet(row))

            self.style.set_ref_row(row)
            self.style.set_length(self.length)

            self.style.fill(worksheet)
            self.style.border(worksheet)
            worksheet[f"{self.style.config['cols_content_range']['value_begin']}{row}"] = str(
                self.items[0])
            self.style.font(worksheet)
            self.style.merge(worksheet)

        except (KeyError, ValueError) as e:
            raise ValueError(f"Failed to write value content: {str(e)}") from e

    def __repr__(self) -> str:
        """
        Return the string representation of the value content.

        Returns:
            str: The string representation of the value content.
        """
        return f"ValueContent(key={self.key}, items={self.items})"

    def get_dict(self) -> Dict[str, Any]:
        """
        Return the dictionary representation of the value content.

        Returns:
            Dict[str, Any]: The dictionary representation of the value content.
        """
        return {
            'key': self.key,
            'item': self.items[0] if self.items else None,
            'type': self.type
        }
