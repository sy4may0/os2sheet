from libs.excelize.contents.Content import StyleSet
from libs.excelize.contents.Collection import Collection
from typing import Dict, Any, Optional, List
from libs.excelize.contents.MatrixContent import MatrixContent
from openpyxl.worksheet.worksheet import Worksheet
from libs.excelize.utils import column_increment, apply_font


class MatrixCollectionStyleSet(StyleSet):
    def __init__(
        self, ref_row: int,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the MatrixCollectionStyleSet.

        Args:
            ref_row (int): The reference row to start writing from.
            config (Optional[Dict[str, Any]]): The configuration for the style set.
        """
        super().__init__(ref_row, config)

    @property
    def index(self) -> int:
        """
        Get the index of the MatrixCollectionStyleSet.
        """
        return self.__index

    @property
    def parent_index(self) -> int:
        """
        Get the parent index of the MatrixCollectionStyleSet.
        """
        return self.__parent_index

    def set_index(self, index: int) -> None:
        """
        Set the index of the MatrixCollectionStyleSet.
        """
        self.__index = index

    def set_parent_index(self, index: int) -> None:
        """
        Set the parent index of the MatrixCollectionStyleSet.
        """
        self.__parent_index = index

    def border(self, worksheet: Worksheet) -> None:
        pass

    def fill(self, worksheet: Worksheet) -> None:
        pass

    def font(self, worksheet: Worksheet) -> None:
        """
        Apply the font to the MatrixCollectionStyleSet.
        """
        apply_font(
            worksheet,
            self.config['col_content_index'],
            self.config['col_content_index'],
            self.ref_row,
            self.ref_row,
            font=self.config['fonts']['title']
        )

    def merge(self, worksheet: Worksheet) -> None:
        pass


class MatrixContentCollection(Collection):
    def __init__(
        self, ref_row: int,
        items: Optional[List[MatrixContent]] = None,
        index: int = 0,
        parent_index: int = 0,
    ):
        """
        Initialize the MatrixContentCollection.

        Args:
            ref_row (int): The reference row to start writing from.
            config (Optional[Dict[str, Any]]): The configuration for the MatrixContentCollection.
            index (int, optional): The index of the MatrixContentCollection.
            parent_index: (int, optional): The parent index of the MatrixContentCollection.
        """
        super().__init__(ref_row, items, index, parent_index)

    @property
    def length(self) -> int:
        """
        Get the length of the MatrixContentCollection.
        """
        return self.items[0].length + 2

    def check_length(self):
        """
        Check the length of the MatrixContentCollection.
        """
        length_list = [item.length for item in self.items]
        if length_list and max(length_list) != min(length_list):
            raise ValueError(
                "Items in MatrixContentCollection must "
                "have the same length MatrixContent"
            )

    def add_item(self, item: MatrixContent) -> None:
        """
        Add an item to the MatrixContentCollection.

        Args:
            item (MatrixContent): The item to add to the MatrixContentCollection.
        """
        super().add_item(item)
        self.check_length()

    def write(self, worksheet: Worksheet, ref_row: int) -> None:
        """
        Write the MatrixContentCollection to the worksheet.

        Args:
            worksheet (Worksheet): The worksheet to write to.
            ref_row (int): The reference row to start writing from.
        """
        row = ref_row
        if self.style and not isinstance(self.style, MatrixCollectionStyleSet):
            raise ValueError("Style is not a MatrixCollectionStyleSet")

        if not self.style:
            self.set_style(MatrixCollectionStyleSet(
                row, config=None,
            ))

        worksheet[f'{self.style.config["col_content_index"]}{row}'] = \
            f"{self.parent_index}.{self.index}. {self.key}"

        row += 1
        col = self.style.config['col_content_index']
        for item in self.items:
            item.write(worksheet, row, col)
            col = column_increment(col, item.width)
        self.style.font(worksheet)
