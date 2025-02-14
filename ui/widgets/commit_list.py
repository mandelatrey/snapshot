from PySide2.QtWidgets import (QListWidget, QListWidgetItem, QMenu, 
                              QInputDialog, QColorDialog, QMessageBox,
                              QFileDialog, QLineEdit, QDialog, QVBoxLayout, QTextEdit,
                              QDialogButtonBox, QApplication)
from PySide2.QtCore import Qt
from .commit_list_item import CommitListItem
import os
import shutil

class CommitList(QListWidget):
    def __init__(self, file_manager, parent=None):
        super().__init__(parent)
        self.file_manager = file_manager
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setSpacing(2)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.load_commits()

    def load_commits(self):
        """Load all commits into the list"""
        history = self.file_manager.get_commit_history()
        self.clear()
        
        # Sort commits by ID to maintain order
        history.sort(key=lambda x: x['id'])
        
        for commit in history:
            self.add_commit(commit)
        
        # Process events to ensure UI is updated
        QApplication.processEvents()

    def add_commit(self, commit):
        """Add a commit to the list if it doesn't already exist"""
        # Check if commit already exists
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget and widget.get_commit_id() == commit['id']:
                return  # Skip if already exists
            
        # Add new commit
        item = QListWidgetItem(self)
        widget = CommitListItem(
            commit['id'],
            commit['timestamp'],
            commit['message'],
            commit.get('note', ''),
            commit.get('color')
        )
        item.setSizeHint(widget.sizeHint())
        self.setItemWidget(item, widget)

    def show_context_menu(self, position):
        item = self.itemAt(position)
        if not item:
            return

        widget = self.itemWidget(item)
        if not widget:
            return

        commit_id = widget.get_commit_id()
        menu = QMenu()

        # Edit message action
        edit_message = menu.addAction("Edit Message")
        edit_message.triggered.connect(lambda: self.edit_commit_message(commit_id))

        # Add/Edit note action
        edit_note = menu.addAction("Add/Edit Note")
        edit_note.triggered.connect(lambda: self.edit_commit_note(commit_id))

        # Color options submenu
        color_menu = menu.addMenu("Set Color")
        colors = {
            "None": None,
            "Red": "#ffcdd2",
            "Green": "#c8e6c9",
            "Blue": "#bbdefb",
            "Yellow": "#fff9c4",
            "Purple": "#e1bee7"
        }
        
        for color_name, color_value in colors.items():
            action = color_menu.addAction(color_name)
            action.triggered.connect(
                lambda checked=False, cv=color_value: self.set_commit_color(commit_id, cv)
            )

        # Export action
        menu.addSeparator()
        export_action = menu.addAction("Export Version")
        export_action.triggered.connect(lambda: self.export_commit(commit_id))

        # Delete action
        menu.addSeparator()
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self.delete_commit(commit_id))

        menu.exec_(self.mapToGlobal(position))

    def edit_commit_message(self, commit_id):
        current_message = self.file_manager.get_commit_message(commit_id)
        new_message, ok = QInputDialog.getText(
            self,
            "Edit Commit Message",
            "Enter new message:",
            text=current_message
        )
        if ok and new_message:
            self.file_manager.update_commit(commit_id, message=new_message)
            # Update the existing item's message
            for i in range(self.count()):
                item = self.item(i)
                widget = self.itemWidget(item)
                if widget and widget.get_commit_id() == commit_id:
                    widget.update_message(new_message)
                    break

    def edit_commit_note(self, commit_id):
        current_note = self.file_manager.get_commit_note(commit_id)
        dialog = NoteDialog(current_note, self)
        if dialog.exec_() == QDialog.Accepted:
            new_note = dialog.get_note()
            self.file_manager.update_commit(commit_id, note=new_note)
            # Update the existing item's note
            for i in range(self.count()):
                item = self.item(i)
                widget = self.itemWidget(item)
                if widget and widget.get_commit_id() == commit_id:
                    widget.update_note(new_note)
                    break

    def set_commit_color(self, commit_id, color):
        """Set color for a specific commit"""
        if color == "Custom":
            color = QColorDialog.getColor()
            if not color.isValid():
                return
            color = color.name()

        # Update the commit in the file manager
        self.file_manager.update_commit(commit_id, color=color)

        # Find and update the specific item
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget and widget.get_commit_id() == commit_id:
                # Update the existing widget's color
                widget.set_color(color)
                break

    def export_commit(self, commit_id):
        """Export a specific version of the file"""
        file_path = self.file_manager.get_version_path(commit_id)
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(
                self,
                "Export Error",
                "Could not find the file for this version."
            )
            return

        # Get original filename and suggest new name with version
        original_name = os.path.basename(file_path)
        base, ext = os.path.splitext(original_name)
        suggested_name = f"{base}_v{commit_id}{ext}"

        # Ask user for save location
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Version",
            os.path.join(os.path.expanduser("~/Desktop"), suggested_name),
            f"*{ext}"
        )

        if save_path:
            try:
                shutil.copy2(file_path, save_path)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Version exported successfully to:\n{save_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Failed to export version: {str(e)}"
                )

    def delete_commit(self, commit_id):
        """Delete a specific commit"""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this commit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = self.file_manager.delete_commit(commit_id)
            if success:
                # Find and remove the item from the list
                for i in range(self.count()):
                    item = self.item(i)
                    widget = self.itemWidget(item)
                    if widget and widget.get_commit_id() == commit_id:
                        # Remove the item
                        item = self.takeItem(i)
                        if widget:
                            widget.setParent(None)
                            widget.deleteLater()
                        del item
                        break
                
                # If this was the last commit, clear everything
                if self.count() == 0:
                    if hasattr(self.parent(), 'parent_window'):
                        main_window = self.parent().parent_window
                        if main_window:
                            # Clear preview and note panel
                            main_window.right_panel.preview.clear()
                            main_window.right_panel.note_panel.clear()
                            main_window.right_panel.note_panel.hide()
                            main_window.right_panel.show_note_button.hide()
            else:
                QMessageBox.warning(
                    self,
                    "Delete Failed",
                    "Failed to delete the commit. Please try again."
                )

    def clear(self):
        """Override clear to properly clean up widgets"""
        try:
            if not self.isValid():  # Check if widget is still valid
                return
            
            # Take and delete items one by one
            while self.count() > 0:
                try:
                    item = self.takeItem(0)
                    if item:
                        widget = self.itemWidget(item)
                        if widget and not widget.isDestroyed():
                            widget.setParent(None)
                            widget.deleteLater()
                        del item
                except RuntimeError:
                    break  # Break if objects are already deleted
                
            super().clear()
            QApplication.processEvents()
        except RuntimeError:
            pass  # Ignore if widget is already deleted

    def __del__(self):
        """Cleanup when object is deleted"""
        try:
            if self.isValid():  # Check if widget is still valid
                self.clear()
                self.setParent(None)
        except (RuntimeError, AttributeError):
            pass

    def isValid(self):
        """Check if the widget is still valid"""
        try:
            return not self.isDestroyed() and self.count() >= 0
        except (RuntimeError, AttributeError):
            return False

class NoteDialog(QDialog):
    def __init__(self, current_note="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Note")
        self.init_ui(current_note)

    def init_ui(self, current_note):
        layout = QVBoxLayout()
        
        # Text editor
        self.text_edit = QTextEdit()
        self.text_edit.setText(current_note)
        self.text_edit.setMinimumSize(300, 200)
        layout.addWidget(self.text_edit)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

    def get_note(self):
        return self.text_edit.toPlainText() 