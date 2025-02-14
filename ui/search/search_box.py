from PySide2.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton
from PySide2.QtCore import Signal, Qt

class SearchBox(QWidget):
    textChanged = Signal(str)  # Signal for when search text changes

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search commits...")
        self.search_input.returnPressed.connect(self.trigger_search)  # Add Enter key support
        layout.addWidget(self.search_input)

        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.trigger_search)
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(self.search_button)

        self.setLayout(layout)

    def trigger_search(self):
        """Trigger search with current input text"""
        self.textChanged.emit(self.search_input.text().strip())

    def on_text_changed(self, text):
        """Emit signal when search text changes"""
        self.textChanged.emit(text.strip())

    def clear(self):
        """Clear the search box"""
        self.search_input.clear() 