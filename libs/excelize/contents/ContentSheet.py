from typing import List, Optional, Dict, Any
from libs.excelize.utils import apply_font
from libs.excelize.contents.Content import Content, StyleSet
from libs.excelize.contents.ContentCollection import ContentCollection
from libs.excelize.contents.MatrixContentCollection import MatrixContentCollection
from openpyxl.worksheet.worksheet import Worksheet


class ContentSheetStyleSet(StyleSet):
    def __init__(
        self, ref_row: int, config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the style set.

        Args:
            ref_row: The row number to start writing.
            config: The configuration for the style set.
        """
        super().__init__(ref_row, config)

    def border(self, worksheet: Worksheet) -> None:
        pass

    def fill(self, worksheet: Worksheet) -> None:
        pass

    def font(self, worksheet: Worksheet) -> None:
        """
        Apply the font style to the worksheet.

        Args:
            worksheet: The worksheet to apply the style to.
        """
        apply_font(
            worksheet,
            self.config['col_sheet_index'],
            self.config['col_sheet_index'],
            self.ref_row, self.ref_row,
            font=self.config['fonts']['title']
        )

    def merge(self, worksheet: Worksheet) -> None:
        pass


class ContentSheet(Content):
    def __init__(
        self, key: str, items: List[Content],
        sheetname: str, index: int = 0
    ):
        """
        Initialize the content sheet.

        Args:
            key: The key of the content sheet.
            items: The items of the content sheet.
            sheetname: The name of the sheet.
            index: The index of the content sheet.  
        """
        super().__init__(key, items, type='sheet')
        self.__sheetname = sheetname
        self.__index = index

    @property
    def sheetname(self) -> str:
        """
        Get the name of the sheet.

        Returns:
            The name of the sheet.
        """
        return self.__sheetname

    @property
    def index(self) -> int:
        """
        Get the index of the content sheet.

        Returns:
            The index of the content sheet.
        """
        return self.__index

    @property
    def length(self) -> int:
        """
        Get the length of the content sheet.

        Returns:
            The length of the content sheet.
        """
        return sum([item.length for item in self.items]) + 1

    def set_index(self, index: int):
        """
        Set the index of the content sheet.

        Args:
            index: The index of the content sheet.
        """
        self.__index = index

    def set_sheetname(self, sheetname: str):
        """
        Set the name of the sheet.

        Args:
            sheetname: The name of the sheet.
        """
        self.__sheetname = sheetname

    def fix_contents_index(self):
        """
        Reassign the index of the contents.
        """
        index = 1
        for item in self.items:
            if not isinstance(item, (ContentCollection, MatrixContentCollection)):
                continue
            item.set_index(index)
            item.set_parent_index(self.index)
            index += 1

    def write(
        self,
        worksheet: Worksheet,
        ref_row: int
    ):
        """
        Write the content sheet to the worksheet.

        Args:
            worksheet: The worksheet to write the content sheet to.
            ref_row: The row number to start writing.
        """
        row = ref_row
        if self.style and not isinstance(self.style, ContentSheetStyleSet):
            raise ValueError("style must be ContentSheetStyleSet")

        if not self.style:
            self.set_style(ContentSheetStyleSet(
                row, config=None,
            ))

        worksheet[f'{self.style.config["col_sheet_index"]}{row}'] = \
            f"{self.index}. {self.key}"
        self.style.font(worksheet,)

        row += 1
        worksheet.insert_rows(row, self.length)
        for item in self.items:
            item.write(worksheet, row)
            row += item.length
        # 印刷時の空白ページ除去
        worksheet.delete_rows(row+1, self.length)
