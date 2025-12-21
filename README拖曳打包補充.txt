# 打包tkinterdnd2拖曳功能到exe的步驟

1. 打包時需將tkinterdnd2的DLL與tcl檔案一併加入：

pyinstaller --noconsole --onefile \
  --add-data ".venv/Lib/site-packages/tkinterdnd2/tkdnd/win-x64/*;tkdnd/" \
  tga_to_png_tool.py

2. 打包後，dist資料夾下會有一個tkdnd資料夾，裡面有dll與tcl檔。

3. 若拖曳功能仍無法用，請將tkdnd資料夾複製到exe同目錄，或手動複製下列檔案到exe同資料夾：
- libtkdnd2.9.4.dll
- tkdnd.tcl
- pkgIndex.tcl

4. 若還是不行，請確認tkinterdnd2的TkinterDnD.py有正確尋找tkdnd路徑。

如需自動化腳本或詳細操作，請再告知！