# PyQt5 版打包成 EXE 說明

1. 請先安裝 pyinstaller：
   pip install pyinstaller

2. 在本資料夾執行下列指令：
   pyinstaller --noconsole --onefile tga_to_png_tool.py

3. 產生的 exe 會在 dist 資料夾內。

4. 若有其他資源（如圖片、設定檔），請用 --add-data 加入。

5. EXE 可直接在其他 Windows 電腦執行，無需額外 DLL。

如需自訂圖示：
   pyinstaller --noconsole --onefile --icon=youricon.ico tga_to_png_tool.py

如需自動化腳本或遇到打包錯誤，請告知！