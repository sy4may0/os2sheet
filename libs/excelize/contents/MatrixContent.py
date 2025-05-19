from typing import Dict, Any, List, Optional
from libs.excelize.utils import column_increment, apply_border, apply_fill, apply_font
from libs.excelize.contents.Content import Content, StyleSet
from openpyxl.utils import column_index_from_string
from openpyxl.worksheet.worksheet import Worksheet


class MatrixStyleSet(StyleSet):
    def __init__(
        self, ref_row: int, config: Optional[Dict[str, Any]] = None,
        column: str = None,
        width: int = 5
    ):
        """
        Initialize the MatrixStyleSet.

        Args:
            ref_row (int): The reference row to start writing from.
            config (Optional[Dict[str, Any]]): The configuration for the style set.
            column (str, optional): The column to write to.
            width (int, optional): The width of the MatrixStyleSet.

        Raises:
            ValueError: If column is not provided.
        """
        super().__init__(ref_row, config)
        self.__column = column
        self.__width = width

    @property
    def column(self) -> str:
        """
        Get the column of the MatrixStyleSet.
        """
        return self.__column

    @property
    def width(self) -> int:
        """
        Get the width of the MatrixStyleSet.
        """
        return self.__width

    def border(
        self,
        worksheet: Worksheet,
    ):
        """
        Apply the border to the MatrixStyleSet.

        Args:
            worksheet (Worksheet): The worksheet to write to.
            row (int): The row to write to.
        """
        startcol = self.column
        endcol = column_increment(startcol, self.width-1)
        for _r in range(self.ref_row, self.ref_row + self.length - 1):
            apply_border(
                worksheet,
                startcol,
                endcol,
                _r,
                _r,
                color=self.config['colorset']['border_main'],
                style='dashed'
            )
        apply_border(
            worksheet,
            startcol,
            endcol,
            self.ref_row, self.ref_row,
            color=self.config['colorset']['border_sub']
        )
        apply_border(
            worksheet,
            startcol,
            endcol,
            self.ref_row,
            self.ref_row + self.length - 1,
            color=self.config['colorset']['border_sub']
        )

    def fill(
        self,
        worksheet: Worksheet,
    ):
        """
        Fill the MatrixStyleSet.

        Args:
            worksheet (Worksheet): The worksheet to write to.
            row (int): The row to write to.

        """
        startcol = self.column
        endcol = column_increment(startcol, self.width-1)
        apply_fill(
            worksheet,
            startcol,
            endcol,
            self.ref_row,
            self.ref_row + self.length - 1,
            color=self.config['colorset']['main']
        )
        apply_fill(
            worksheet,
            startcol,
            endcol,
            self.ref_row,
            self.ref_row,
            color=self.config['colorset']['sub2']
        )

    def font(
        self,
        worksheet: Worksheet,
    ):
        """
        Apply the font to the MatrixStyleSet.

        Args:
            worksheet (Worksheet): The worksheet to write to.
            row (int): The row to write to.

        """
        startcol = self.column
        endcol = column_increment(startcol, self.width-1)
        apply_font(
            worksheet,
            startcol,
            endcol,
            self.ref_row,
            self.ref_row + self.length - 1,
            font=self.config['fonts']['value']
        )
        apply_font(
            worksheet,
            startcol,
            endcol,
            self.ref_row, self.ref_row,
            font=self.config['fonts']['main']
        )

    def merge(
        self,
        worksheet: Worksheet,
    ):
        """
        Merge the MatrixStyleSet.

        Args:
            worksheet (Worksheet): The worksheet to write to.
            row (int): The row to write to.

        """
        startcol = self.column
        endcol = column_increment(startcol, self.width-1)
        for _r in range(self.ref_row, self.ref_row + self.length):
            worksheet.merge_cells(
                start_row=_r,
                start_column=column_index_from_string(startcol),
                end_row=_r,
                end_column=column_index_from_string(endcol)
            )


class MatrixContent(Content):
    def __init__(
        self,
        key: str,
        items: List[str],
        width: int = 5
    ) -> None:
        """
        Initialize the MatrixContent.

        Args:
            key (str): The key of the MatrixContent.
            items (List[str]): The items of the MatrixContent.
            column (str, optional): The column to write to.
            width (int, optional): The width of the MatrixContent.

        """
        super().__init__(key, items, type='matrix')
        self.__width = width

    @property
    def width(self) -> int:
        """
        Get the width of the MatrixContent.
        """
        return self.__width

    @property
    def length(self) -> int:
        """
        Get the length of the MatrixContent.
        """
        return len(self.items) + 1

    def write(
        self,
        worksheet: Worksheet,
        ref_row: int,
        column: str = None
    ) -> None:
        """
        Write the MatrixContent to the worksheet.

        Args:
            worksheet (Worksheet): The worksheet to write to.
            ref_row (int): The row to write to.
            column (str, optional): The column to write to.

        Raises:
            ValueError: If column is not provided.
        """
        row = ref_row
        if self.style and not isinstance(self.style, MatrixStyleSet):
            raise ValueError("Style is not a MatrixStyleSet")

        if not column and not self.column:
            raise ValueError("column is required")

        if not self.style:
            self.set_style(MatrixStyleSet(
                row, config=None,
                column=column,
                width=self.width
            ))

        self.style.set_ref_row(row)
        self.style.set_length(self.length)

        self.style.border(worksheet)
        self.style.fill(worksheet)

        worksheet[f"{column}{row}"] = self.key
        row += 1
        for item in self.items:
            worksheet[f"{column}{row}"] = item
            row += 1

        self.style.font(worksheet)
        self.style.merge(worksheet)

    def get_dict(self) -> Dict[str, Any]:
        """
        Get the dictionary representation of the MatrixContent.

        Returns:
            Dict[str, Any]: The dictionary representation of the MatrixContent.
        """
        return {
            'key': self.key,
            'items': self.items,
            'type': self.type
        }
