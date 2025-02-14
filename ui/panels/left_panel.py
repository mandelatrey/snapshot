from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QCheckBox, QMessageBox
from ..widgets.commit_list import CommitList
from ..widgets.file_selector import FileSelector
from ..search.search_box import SearchBox
from datetime import datetime
from PySide2.QtWidgets import QApplication

class LeftPanel(QWidget):
    def __init__(self, file_manager, parent=None):
        super().__init__(parent)
        self.file_manager = file_manager
        self.parent_window = parent  # Store reference to main window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # File selector
        self.file_selector = FileSelector(self.file_manager)
        layout.addWidget(self.file_selector)

        # Auto-commit toggle
        self.auto_commit = QCheckBox("Auto-commit on file changes")
        self.auto_commit.setChecked(True)
        layout.addWidget(self.auto_commit)

        # Search box
        self.search_box = SearchBox()
        self.search_box.textChanged.connect(self.filter_commits)
        layout.addWidget(self.search_box)

        # Commit list
        self.commit_list = CommitList(self.file_manager)
        layout.addWidget(self.commit_list)

        # Buttons
        buttons_layout = self.create_buttons()
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def filter_commits(self, search_text):
        """Filter commits based on search text"""
        # Get all commits first
        history = self.file_manager.get_commit_history()
        
        # Store current selection
        current_item = self.commit_list.currentItem()
        current_id = None
        if current_item:
            widget = self.commit_list.itemWidget(current_item)
            if widget:
                current_id = widget.get_commit_id()
        
        # Clear current display
        self.commit_list.clear()
        
        # Sort commits by ID to maintain order
        history.sort(key=lambda x: x['id'])
        
        # Filter and add commits based on partial matches
        search_text = search_text.strip().lower()
        for commit in history:
            message = commit['message'].lower()
            note = commit.get('note', '').lower()
            
            # Check for partial matches in message or note
            if any(word in message or word in note 
                   for word in search_text.split() if word):
                self.commit_list.add_commit(commit)
        
        # Restore selection if possible
        if current_id is not None:
            for i in range(self.commit_list.count()):
                item = self.commit_list.item(i)
                widget = self.commit_list.itemWidget(item)
                if widget and widget.get_commit_id() == current_id:
                    self.commit_list.setCurrentItem(item)
                    break

    def create_buttons(self):
        """Create commit and project buttons"""
        buttons_layout = QHBoxLayout()
        
        # Left side buttons (commit)
        left_buttons = QHBoxLayout()
        commit_button = QPushButton("Commit")
        commit_button.clicked.connect(self.commit_file)
        left_buttons.addWidget(commit_button)
        buttons_layout.addLayout(left_buttons)
        
        # Right side buttons (project actions)
        right_buttons = QHBoxLayout()
        
        save_project_button = QPushButton("Save Project")
        save_project_button.clicked.connect(self.parent_window.save_project)
        save_project_button.setStyleSheet("""
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
        right_buttons.addWidget(save_project_button)
        
        delete_project_button = QPushButton("Delete Project")
        delete_project_button.clicked.connect(self.delete_project)
        delete_project_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        right_buttons.addWidget(delete_project_button)
        
        buttons_layout.addLayout(right_buttons)
        return buttons_layout

    def commit_file(self):
        """Commit the selected file"""
        file_path = self.file_selector.file_path_input.text().strip()
        if not file_path:
            return

        message = "Initial commit"  # Could be extended with input dialog
        commit_id = self.file_manager.save(file_path, message)
        
        # Add only the new commit
        commit = {
            'id': commit_id,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'message': message,
            'file': file_path,
            'note': '',
            'color': None
        }
        self.commit_list.add_commit(commit)

    def delete_project(self):
        """Delete all visible commits in the project"""
        visible_count = self.commit_list.count()
        if visible_count == 0:
            QMessageBox.information(
                self,
                "No Commits",
                "No commits to delete."
            )
            return
        
        message = "Are you sure you want to delete "
        message += f"these {visible_count} commits?\n" if visible_count > 1 else "this commit?\n"
        message += "This action cannot be undone."
        
        reply = QMessageBox.question(
            self,
            "Delete Commits",
            message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Get IDs of visible commits
                commit_ids = []
                for i in range(self.commit_list.count()):
                    item = self.commit_list.item(i)
                    widget = self.commit_list.itemWidget(item)
                    if widget:
                        commit_ids.append(widget.get_commit_id())
                
                # Delete visible commits
                for commit_id in commit_ids:
                    self.file_manager.delete_commit(commit_id)
                
                # Clear UI elements
                self.commit_list.clear()
                self.file_selector.file_path_input.clear()
                self.search_box.clear()
                QApplication.processEvents()
                
                # Reset file watching and UI state
                if self.parent_window:
                    if self.parent_window.watched_file:
                        try:
                            self.parent_window.file_watcher.removePath(self.parent_window.watched_file)
                        except:
                            pass
                    self.parent_window.watched_file = None
                    self.parent_window.last_modified = None
                    self.parent_window.is_committing = False
                    
                    # Clear right panel
                    self.parent_window.right_panel.update_source_file(None)
                    self.parent_window.right_panel.preview.clear()
                    self.parent_window.right_panel.note_panel.clear()
                    self.parent_window.right_panel.note_panel.hide()
                    self.parent_window.right_panel.show_note_button.hide()
                    
                    # Clear status bar
                    self.parent_window.status_bar.clearMessage()
                
                # Reload the commits list to show remaining commits
                self.commit_list.load_commits()
                QApplication.processEvents()
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Successfully deleted {visible_count} commit{'s' if visible_count > 1 else ''}."
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete commits: {str(e)}"
                ) 