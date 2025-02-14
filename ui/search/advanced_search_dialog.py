from PySide2.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                              QCheckBox, QLabel, QDateEdit, QComboBox, QDialogButtonBox)
from PySide2.QtCore import QDate

class AdvancedSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Search")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Search text
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search text...")
        layout.addWidget(self.search_input)

        # Regex toggle
        self.regex_checkbox = QCheckBox("Use Regular Expression")
        layout.addWidget(self.regex_checkbox)

        # Date range
        date_layout = QHBoxLayout()
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        
        date_layout.addWidget(QLabel("From:"))
        date_layout.addWidget(self.date_from)
        date_layout.addWidget(QLabel("To:"))
        date_layout.addWidget(self.date_to)
        layout.addLayout(date_layout)

        # File type filter
        self.file_type = QComboBox()
        self.file_type.addItem("All Files")
        self.file_type.addItems([".ai", ".psd", ".pdf", ".png", ".jpg"])
        layout.addWidget(self.file_type)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout) 