from PySide2.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, 
                              QHBoxLayout, QFileDialog)
from PySide2.QtCore import Qt
from ..widgets.preview import PreviewWidget
from ..widgets.note_panel import NotePanel
import os

class RightPanel(QWidget):
    def __init__(self, file_manager, parent=None):
        super().__init__(parent)
        self.file_manager = file_manager
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Source file info panel
        self.source_info = QFrame()
        self.source_info.setFrameStyle(QFrame.StyledPanel)
        self.source_info.setStyleSheet("QFrame { background-color: #f8f8f8; border: 1px solid #ddd; }")
        source_layout = QVBoxLayout()
        
        # Header with label and watch button
        header_layout = QHBoxLayout()
        self.source_label = QLabel("Source File:")
        self.source_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(self.source_label)
        
        self.watch_button = QPushButton("Re-link file being watched")
        self.watch_button.setStyleSheet("""
            QPushButton {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 3px 8px;
                background-color: #e8e8e8;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #d8d8d8;
            }
        """)
        self.watch_button.clicked.connect(self.select_watch_file)
        header_layout.addWidget(self.watch_button)
        header_layout.addStretch()
        source_layout.addLayout(header_layout)
        
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setWordWrap(True)
        self.file_path_label.setStyleSheet("color: #666;")
        source_layout.addWidget(self.file_path_label)
        
        self.source_info.setLayout(source_layout)
        layout.addWidget(self.source_info)
        
        # Preview widget
        self.preview = PreviewWidget()
        layout.addWidget(self.preview)

        # Show Note button (initially hidden)
        self.show_note_button = QPushButton("📝 Show Note")
        self.show_note_button.setStyleSheet("""
            QPushButton {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                background-color: #f8f8f8;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """)
        self.show_note_button.clicked.connect(self.show_note)
        self.show_note_button.hide()
        layout.addWidget(self.show_note_button)

        # Note panel
        self.note_panel = NotePanel(self)
        self.note_panel.note_hidden.connect(self.on_note_hidden)
        layout.addWidget(self.note_panel)
        
        layout.addStretch()
        self.setLayout(layout)

    def select_watch_file(self):
        """Allow user to select a new file to watch"""
        options = QFileDialog.Options()
        file_filters = f"Design Files (*{' *'.join(self.file_manager.supported_formats)})"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File to Watch",
            os.path.dirname(self.file_path_label.text()) if self.file_path_label.text() != "No file selected" else "",
            file_filters,
            options=options
        )
        if file_path:
            main_window = self.window()
            if main_window:
                main_window.watch_file(file_path)
                self.update_source_file(file_path)

    def update_source_file(self, file_path):
        """Update the source file information"""
        if file_path:
            self.file_path_label.setText(file_path)
            self.source_info.show()
            self.watch_button.show()
        else:
            self.file_path_label.setText("No file selected")
            self.source_info.hide()
            self.watch_button.hide()

    def show_note(self):
        """Show note and hide button"""
        if self.note_panel.has_note():
            self.note_panel.show()
            self.show_note_button.hide()

    def on_note_hidden(self):
        """Show button when note is hidden"""
        if self.note_panel.has_note():
            self.show_note_button.show()
            self.note_panel.hide() 