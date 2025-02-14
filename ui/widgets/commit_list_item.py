from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide2.QtCore import Qt

class CommitListItem(QWidget):
    def __init__(self, commit_id, timestamp, message, note="", color=None, parent=None):
        super().__init__(parent)
        self.commit_id = commit_id
        self.timestamp = timestamp
        self.message = message
        self.note = note
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(5, 5, 5, 5)

        # Main commit info with HTML support for highlighting
        self.commit_label = QLabel()
        self.update_display()
        self.commit_label.setTextFormat(Qt.RichText)
        if color:
            self.set_color(color)
        layout.addWidget(self.commit_label)

    def update_display(self):
        """Update the display text"""
        display_text = f"{self.commit_id} - {self.timestamp} - {self.message}"
        if self.note:
            display_text += " 📝"  # Add note indicator
        self.commit_label.setText(display_text)

    def update_message(self, new_message):
        """Update the commit message"""
        self.message = new_message
        self.update_display()

    def update_note(self, new_note):
        """Update the commit note"""
        self.note = new_note
        self.update_display()

    def set_color(self, color):
        """Update the widget's color"""
        if color:
            self.setStyleSheet(f"background-color: {color};")
        else:
            self.setStyleSheet("")  # Reset to default

    def get_commit_id(self):
        return self.commit_id

    def __del__(self):
        """Cleanup when object is deleted"""
        try:
            if not self.isDestroyed():
                self.setParent(None)
                self.deleteLater()
        except (RuntimeError, AttributeError):
            pass 