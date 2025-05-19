from libs.excelize.contents.Content import Content
from typing import List, Optional


class Collection(Content):
    def __init__(
        self,
        key: str,
        items: Optional[List[Content]] = None,
        index: int = 0,
        parent_index: int = 0,
        type: str = 'collection',
    ):
        super().__init__(key, items, type=type)
        self.__index = index
        self.__parent_index = parent_index

    @property
    def index(self) -> int:
        return self.__index

    @property
    def parent_index(self) -> int:
        return self.__parent_index

    def set_index(self, index: int) -> None:
        self.__index = index

    def set_parent_index(self, index: int) -> None:
        self.__parent_index = index
