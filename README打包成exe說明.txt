# 打包指令說明
# 1. 請先安裝 pyinstaller：
#    pip install pyinstaller
# 2. 在本資料夾執行下列指令：
#    pyinstaller --noconsole --onefile --add-data "tga_to_png_tool.py;." tga_to_png_tool.py
# 3. 產生的 exe 會在 dist 資料夾內
#
# 若有圖片或其他資源，請用 --add-data 加入
#
# 這份 readme 可刪除