from PySide2.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QLabel
from PySide2.QtCore import Signal

class FileSelector(QWidget):
    fileSelected = Signal(str)

    def __init__(self, file_manager, parent=None):
        super().__init__(parent)
        self.file_manager = file_manager
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        
        # File label
        self.file_label = QLabel("Selected File:")
        layout.addWidget(self.file_label)

        # File path input
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("Select a file...")
        self.file_path_input.setReadOnly(True)  # Make it read-only
        layout.addWidget(self.file_path_input)

        # Select button
        select_button = QPushButton("Select File")
        select_button.clicked.connect(self.select_file)
        layout.addWidget(select_button)

        self.setLayout(layout)

    def select_file(self):
        options = QFileDialog.Options()
        file_filters = f"Design Files (*{' *'.join(self.file_manager.supported_formats)})"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", file_filters, options=options
        )
        if file_path:
            self.file_path_input.setText(file_path)
            self.fileSelected.emit(file_path)
            # Get main window and update components
            main_window = self.window()
            if main_window:
                main_window.watch_file(file_path)
                main_window.right_panel.update_source_file(file_path) 