import os
import sys
from PyQt5 import uic

# 讓PyInstaller打包後能正確找到tkdnd拖曳資源
if getattr(sys, 'frozen', False):
    tkdnd_dir = os.path.join(sys._MEIPASS, 'tkdnd')
    if not os.path.exists(tkdnd_dir):
        tkdnd_dir = os.path.join(os.path.dirname(sys.executable), 'tkdnd')

from PyQt5.QtWidgets import (
    QApplication, QWidget, QMessageBox, QFileDialog, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QBrush, QPen, QPainterPath, QImage
from PIL import Image

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class DragDropWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(resource_path("tga_to_png_tool.ui"), self)
        # 手動設定佈局延伸比例 (索引 1 為中間區域，設為 1 表示延伸)
        self.mainLayout.setStretch(0, 0)
        self.mainLayout.setStretch(1, 1)
        self.mainLayout.setStretch(2, 0)
        self.setWindowTitle('視創用TGA/PNG轉檔工具')
        self.setWindowIcon(QIcon(resource_path("images/icon.ico")))
        # 設定圓角圖片按鈕
        self.set_rounded_icon(self.btn_tga_to_png, resource_path("images/01.png"), 48, 8)
        self.btn_tga_to_png.setFixedSize(56, 56)
        self.btn_tga_to_png.setText("")
        self.set_rounded_icon(self.btn_png_to_tga, resource_path("images/02.png"), 48, 8)
        self.btn_png_to_tga.setFixedSize(56, 56)
        self.btn_png_to_tga.setText("")
        # 綁定所有按鈕事件
        self.btn_tga_to_png.clicked.connect(self.set_tga_to_png_mode)
        self.btn_png_to_tga.clicked.connect(self.set_png_to_tga_mode)
        self.btn_add_file.clicked.connect(self.add_files)
        self.btn_remove_file.clicked.connect(self.remove_selected)
        self.btn_clear.clicked.connect(self.clear_table)
        self.btn_close.setText('關於')
        try:
            self.btn_close.clicked.disconnect()
        except Exception:
            pass
        self.btn_close.clicked.connect(self.show_about)
        self.btn_browse.clicked.connect(self.browse_folder)
        self.btn_convert.clicked.connect(self.convert_files)
        self.fileTable.itemSelectionChanged.connect(self.update_preview)
        # 設定表格欄位自動填滿寬度
        self.fileTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 拖曳功能（主視窗層級）
        self.setAcceptDrops(True)
        # 預設模式
        self.convert_mode = 'TGA2PNG'
        self.update_mode_ui()

    def set_rounded_icon(self, button, image_path, size=48, radius=8):
        pixmap = QPixmap(image_path).scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        rounded = QPixmap(size, size)
        rounded.fill(Qt.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, size, size, radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        button.setIcon(QIcon(rounded))
        button.setIconSize(QSize(size, size))

    def set_tga_to_png_mode(self):
        self.convert_mode = 'TGA2PNG'
        self.update_mode_ui()

    def set_png_to_tga_mode(self):
        self.convert_mode = 'PNG2TGA'
        self.update_mode_ui()

    def update_mode_ui(self):
        if self.convert_mode == 'TGA2PNG':
            self.btn_tga_to_png.setStyleSheet('border: 2px solid #2196F3; border-radius: 8px;')
            self.btn_png_to_tga.setStyleSheet('border: none;')
        else:
            self.btn_tga_to_png.setStyleSheet('border: none;')
            self.btn_png_to_tga.setStyleSheet('border: 2px solid #2196F3; border-radius: 8px;')
        self.btn_tga_to_png.setEnabled(True)
        self.btn_png_to_tga.setEnabled(True)

    def add_files(self):
        if self.convert_mode == 'TGA2PNG':
            files, _ = QFileDialog.getOpenFileNames(self, '選擇TGA檔案', '', 'TGA files (*.tga)')
        else:
            files, _ = QFileDialog.getOpenFileNames(self, '選擇PNG檔案', '', 'PNG files (*.png)')
        self.add_files_to_table(files)

    def add_files_to_table(self, files):
        for filepath in files:
            if not filepath:
                continue
            row = self.fileTable.rowCount()
            self.fileTable.insertRow(row)
            self.fileTable.setItem(row, 0, QTableWidgetItem(os.path.basename(filepath)))
            size = os.path.getsize(filepath)
            self.fileTable.setItem(row, 1, QTableWidgetItem(f'{size//1024} KB'))
            ext = os.path.splitext(filepath)[1][1:].upper()
            self.fileTable.setItem(row, 2, QTableWidgetItem(ext))
            self.fileTable.setRowHeight(row, 22)
            # 存檔案路徑在 QTableWidgetItem 的 data 屬性
            self.fileTable.item(row, 0).setData(Qt.UserRole, filepath)

    def remove_selected(self):
        selected = self.fileTable.selectionModel().selectedRows()
        for idx in sorted([s.row() for s in selected], reverse=True):
            self.fileTable.removeRow(idx)
        # 無需重新編號，因為已無序號欄

    def clear_table(self):
        self.fileTable.setRowCount(0)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '選擇資料夾')
        if folder:
            self.line_custom_path.setText(folder)
            self.radio_custom_folder.setChecked(True)

    def convert_files(self):
        if self.fileTable.rowCount() == 0:
            QMessageBox.warning(self, '提示', '請先添加檔案！')
            return
        # 決定輸出資料夾
        if self.radio_current_folder.isChecked():
            get_output_folder = lambda src: os.path.dirname(src)
        elif self.radio_custom_folder.isChecked():
            custom_path = self.line_custom_path.text().strip()
            if not custom_path or not os.path.isdir(custom_path):
                QMessageBox.warning(self, '錯誤', '請選擇有效的自訂輸出資料夾！')
                return
            get_output_folder = lambda src: custom_path
        else:
            QMessageBox.warning(self, '錯誤', '請選擇輸出資料夾！')
            return

        success, fail = 0, 0
        for row in range(self.fileTable.rowCount()):
            item = self.fileTable.item(row, 0)
            if not item:
                continue
            src_path = item.data(Qt.UserRole)
            if not src_path or not os.path.isfile(src_path):
                fail += 1
                continue
            out_dir = get_output_folder(src_path)
            base = os.path.splitext(os.path.basename(src_path))[0]
            try:
                if self.convert_mode == 'TGA2PNG':
                    out_path = os.path.join(out_dir, base + '.png')
                    with Image.open(src_path) as im:
                        im.save(out_path, 'PNG')
                else:
                    out_path = os.path.join(out_dir, base + '.tga')
                    with Image.open(src_path) as im:
                        # Pillow 7.0+ 支援TGA含alpha
                        im.save(out_path, 'TGA')
                success += 1
            except Exception as e:
                fail += 1
        QMessageBox.information(self, '轉檔完成', f'成功：{success} 個，失敗：{fail} 個。')

    def show_about(self):
        QMessageBox.information(self, '關於',
            '視創用TGA/PNG轉檔工具\n\n'
            '支援TGA與PNG批次互轉，拖曳/多選/自訂輸出路徑。\n'
            '作者：Cyrus\n'
            '版本：1.0\n'
            '最後更新：2025/12/22')

    def update_preview(self):
        row = self.fileTable.currentRow()
        if row >= 0:
            item = self.fileTable.item(row, 0)
            if item:
                path = item.data(Qt.UserRole)
                self.show_preview_image(path)
                return
        self.previewLabel.setText("預覽")
        self.previewLabel.setPixmap(QPixmap())

    def show_preview_image(self, path):
        if not path or not os.path.exists(path):
            self.previewLabel.setText("檔案不存在")
            return
        
        pixmap = QPixmap(path)
        if pixmap.isNull():
            try:
                with Image.open(path) as img:
                    if img.mode != "RGBA":
                        img = img.convert("RGBA")
                    data = img.tobytes("raw", "RGBA")
                    qimg = QImage(data, img.width, img.height, QImage.Format_RGBA8888)
                    pixmap = QPixmap.fromImage(qimg)
            except Exception:
                pass
        
        if not pixmap.isNull():
            rect = self.previewLabel.contentsRect()
            self.previewLabel.setPixmap(pixmap.scaled(rect.width(), rect.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.previewLabel.setText("無法預覽")

    # 拖曳進表格
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.isfile(path):
                if self.convert_mode == 'TGA2PNG' and path.lower().endswith('.tga'):
                    files.append(path)
                elif self.convert_mode == 'PNG2TGA' and path.lower().endswith('.png'):
                    files.append(path)
        self.add_files_to_table(files)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = DragDropWidget()
    w.show()
    sys.exit(app.exec_())
