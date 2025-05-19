from libs.excelize.contents import *
from openpyxl import Workbook

val01 = ValueContent(' ', ["test1"])
val02 = ValueContent(' ', ["test2"])
val03 = ValueContent(' ', ["test3"])

pc0 = ParentContent("test0", [val01, val02, val03], indent=0)

val11 = ValueContent(' ', ["test11"])
val12 = ValueContent(' ', ["test12"])
val13 = ValueContent(' ', ["test13"])

pc1 = ParentContent("test1", [val11, val12, val13], indent=1)

val21 = ValueContent(' ', ["test21"])
val22 = ValueContent(' ', ["test22"])
val23 = ValueContent(' ', ["test23"])

pc2 = ParentContent("test2", [val21, val22, val23, pc1], indent=0)
pc3 = ParentContent("test3", [], indent=0)
pc4 = ParentContent("test5", [ValueContent(' ', ["test51"])], indent=0)

cc1 = ContentCollection("test3", [pc0, pc2, pc3, pc4], index=1, parent_index=1)

mv1 = MatrixContent("test6", ["test61", "test62", "test63"], width=1)
mv2 = MatrixContent("test7", ["test71", "test72", "test73"], width=1)
mv3 = MatrixContent("test8", ["test81", "test82", "test83"], width=1)
mc1 = MatrixContentCollection(
    "test9", [mv1, mv2, mv3], index=1, parent_index=1)

cs1 = ContentSheet("test_contents", [cc1, mc1],
                   sheetname="test_contents", index=1)

cs1.fix_contents_index()

wb = Workbook()
ws = wb.active

cs1.write(ws, 1)

wb.save("test.xlsx")
