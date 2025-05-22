from typing import Dict, Any, Optional, List
from libs.excelize.contents import StyleSet, Content, ValueContent
from libs.excelize.utils import column_increment, apply_border, apply_fill, apply_font
from openpyxl.worksheet.worksheet import Worksheet


class ParentStyleSet(StyleSet):
    """親コンテンツ用のスタイル設定クラス"""

    def __init__(
        self, ref_row: int,
        config: Optional[Dict[str, Any]] = None,
        length: int = 0,
        indent: int = 0,
    ):
        """
        Initialize the style set for the parent content.

        Args:
            ref_row (int): The row number of the reference cell.
            config (Optional[Dict[str, Any]]): The configuration for the style set.
            indent (int): The indent level of the parent content.

        Raises:
            ValueError: If the configuration is invalid.
        """
        super().__init__(ref_row, config, length)
        self.__indent = indent

    @property
    def indent(self) -> int:
        """
        Get the indent level of the parent content.

        Returns:
            int: The indent level of the parent content.
        """
        return self.__indent

    def set_indent(self, indent: int) -> None:
        """
        Set the indent level of the parent content.
        """
        self.__indent = indent

    def border(self, worksheet: Worksheet) -> None:
        """
        Apply the border to the parent content.
        Applies border to the entire content range including all child items.

        Args:
            worksheet (Worksheet): The worksheet to apply the border to.

        Raises:
            ValueError: If the worksheet is invalid or the range is invalid.
        """
        try:
            col_begin = column_increment(
                self.config['cols_content_range']['key_begin'],
                self.__indent
            )
            col_end = self.config['cols_content_range']['remark_end']

            apply_border(
                worksheet,
                col_begin,
                col_end,
                self.ref_row,
                self.ref_row + self.length - 1,
                color=self.config['colorset']['border_sub']
            )
        except (KeyError, ValueError) as e:
            raise ValueError(f"Failed to apply border: {str(e)}") from e

    def fill(self, worksheet: Worksheet) -> None:
        """
        Apply the fill to the parent content.
        Applies fill to the entire content range including all child items.

        Args:
            worksheet (Worksheet): The worksheet to apply the fill to.

        Raises:
            ValueError: If the worksheet is invalid or the range is invalid.
        """
        try:
            col_begin = column_increment(
                self.config['cols_content_range']['key_begin'],
                self.__indent
            )
            col_end = self.config['cols_content_range']['remark_end']
            apply_fill(
                worksheet,
                col_begin,
                col_end,
                self.ref_row,
                self.ref_row + self.length - 1,
                color=self.config['colorset']['sub1']
            )
        except (KeyError, ValueError) as e:
            raise ValueError(f"Failed to apply fill: {str(e)}") from e

    def font(self, worksheet: Worksheet) -> None:
        """
        Apply the font to the parent content.
        Applies font to key and remark columns.

        Args:
            worksheet (Worksheet): The worksheet to apply the font to.

        Raises:
            ValueError: If the worksheet is invalid or the range is invalid.
        """
        try:
            col_begin = column_increment(
                self.config['cols_content_range']['key_begin'],
                self.__indent
            )
            col_end = self.config['cols_content_range']['remark_end']
            for fix_range in [
                (col_begin, self.config['cols_content_range']['key_end']),
                (self.config['cols_content_range']['remark_begin'], col_end),
            ]:
                apply_font(
                    worksheet,
                    fix_range[0],
                    fix_range[1],
                    self.ref_row,
                    self.ref_row + self.length - 1,
                    font=self.config['fonts']['main']
                )
        except (KeyError, ValueError) as e:
            raise ValueError(f"Failed to apply font: {str(e)}") from e

    def merge(self, worksheet: Worksheet) -> None:
        """
        Not implemented.
        No need to merge the parent content.

        Args:
            worksheet (Worksheet): The worksheet to merge the parent content to.
        """
        pass


class ParentContent(Content):
    """親コンテンツを表すクラス"""

    def __init__(
        self,
        key: str,
        items: List[Content],
        indent: int = 0
    ):
        """
        Initialize a new ParentContent object.

        Args:
            key (str): The key of the content.
            items (List[Content]): The child items of the content.
            indent (int): The indent level of the content.

        Raises:
            ValueError: If the items list is invalid.
        """
        super().__init__(key, items, type='parent')
        self.__indent = indent

    @property
    def indent(self) -> int:
        """
        Get the indent level of the content.

        Returns:
            int: The indent level of the content.
        """
        return self.__indent

    @property
    def length(self) -> int:
        """
        Get the length of the content.
        The length is calculated based on the sum of all child items' lengths.

        Returns:
            int: The length of the content.
        """
        if len(self.items) == 0:
            return 1

        if len(self.items) == 1 and isinstance(self.items[0], ValueContent):
            return 1

        length_offset = 1
        if all(isinstance(item, ValueContent) for item in self.items):
            length_offset = 0

        return sum([item.length for item in self.items]) + length_offset

    def write(self, worksheet: Worksheet, ref_row: int) -> None:
        """
        Write the parent content to the worksheet.
        Writes the key, adds a default ValueContent if no items exist,
        and writes all child items.

        Args:
            worksheet (Worksheet): The worksheet to write the parent content to.
            ref_row (int): The row number of the reference cell.

        Raises:
            ValueError: If the worksheet is invalid or the row is invalid.
        """
        row = ref_row
        if self.style and not isinstance(self.style, ParentStyleSet):
            raise ValueError("Style is not a ParentStyleSet")

        try:
            if len(self.items) == 0:
                self.add_item(ValueContent("N/A"))

            if not self.style:
                self.set_style(ParentStyleSet(row))

            self.style.set_ref_row(row)
            self.style.set_length(self.length)
            self.style.set_indent(self.__indent)

            self.style.fill(worksheet)
            self.style.border(worksheet)

            col = column_increment(
                self.style.config['cols_content_range']['key_begin'],
                self.__indent
            )
            worksheet[f"{col}{row}"] = self.key
            row_offset = 0
            if not (len(self.items) == 1 and isinstance(self.items[0], ValueContent)):
                row_offset = 1
            if all(isinstance(item, ValueContent) for item in self.items):
                row_offset = 0

            row += row_offset

            for item in self.items:
                item.write(worksheet, row)
                row += item.length

            self.style.font(worksheet)
            self.style.merge(worksheet)

        except (KeyError, ValueError) as e:
            raise ValueError(
                f"Failed to write parent content: {str(e)}") from e
