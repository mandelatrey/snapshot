from PySide2.QtWidgets import QLabel
from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap

class PreviewWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 300)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid #ccc;")

    def set_preview(self, image_path):
        if not image_path:
            self.clear()
            return
            
        preview = QPixmap(image_path)
        if not preview.isNull():
            scaled_preview = preview.scaled(
                self.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.setPixmap(scaled_preview)
        else:
            self.setText("Preview not available")

    def clear(self):
        super().clear()
        self.setText("No preview available") 