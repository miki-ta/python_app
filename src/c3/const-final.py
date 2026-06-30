# Finalを使うための宣言
from typing import Final
# RED_COLORを定数として宣言
RED_COLOR: Final[str] = "#FF0000"
# ここで何かしらの処理
# 間違って RED_COLOR を変更しようとする
RED_COLOR = "#F03333"