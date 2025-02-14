from PySide2.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide2.QtCore import Signal

class NotePanel(QFrame):
    note_hidden = Signal()  # Signal when note is hidden

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("QFrame { background-color: #f8f8f8; border: 1px solid #ddd; }")
        self.current_note = ""
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QHBoxLayout()
        title = QLabel("Note:")
        title.setStyleSheet("font-weight: bold;")
        close_button = QPushButton("×")
        close_button.setFixedSize(20, 20)
        close_button.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                color: #666;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #000;
            }
        """)
        close_button.clicked.connect(self.on_hide)
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_button)
        
        # Note content
        self.note_text = QLabel()
        self.note_text.setWordWrap(True)
        self.note_text.setStyleSheet("padding: 5px;")
        
        layout.addLayout(header)
        layout.addWidget(self.note_text)
        self.setLayout(layout)
        self.hide()

    def set_note(self, text):
        """Set note text and show/hide panel accordingly"""
        self.current_note = text or ""
        self.note_text.setText(self.current_note)
        
        if self.current_note:
            self.show()
            if hasattr(self.parent(), 'show_note_button'):
                self.parent().show_note_button.hide()
        else:
            self.hide()
            if hasattr(self.parent(), 'show_note_button'):
                self.parent().show_note_button.hide()

    def has_note(self):
        """Check if there's a note to show"""
        return bool(self.current_note)

    def on_hide(self):
        """Handle hide button click"""
        self.hide()
        self.note_hidden.emit()

    def clear(self):
        """Clear note panel contents"""
        self.note_text.clear()
        self.hide() 