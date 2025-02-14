from PySide2.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QSplitter, 
                              QInputDialog, QFileDialog, QMessageBox, QStatusBar, QApplication)
from PySide2.QtCore import Qt, QFileSystemWatcher, QTimer
from PySide2.QtGui import QIcon
from .panels.left_panel import LeftPanel
from .panels.right_panel import RightPanel
import os
from shutil import copytree, rmtree
from datetime import datetime
import json
from .utils.icon_loader import load_app_icon

class FileManagerUI(QMainWindow):
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.fileChanged.connect(self.on_file_changed)
        self.file_watcher.directoryChanged.connect(self.on_directory_changed)
        self.last_modified = None
        self.watched_file = None
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.is_committing = False
        self.commit_timer = QTimer()
        self.commit_timer.setSingleShot(True)
        self.commit_timer.timeout.connect(self.execute_pending_commit)
        self.pending_commit_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Snapshot")
        self.setWindowIcon(load_app_icon("ui/assets/app-icon.png"))
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Initialize panels
        self.left_panel = LeftPanel(self.file_manager, self)
        self.right_panel = RightPanel(self.file_manager, self)

        # Connect commit selection to preview
        self.left_panel.commit_list.currentItemChanged.connect(self.on_commit_selected)

        # Add panels to splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.right_panel)
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def on_commit_selected(self, current, previous):
        if not current:
            self.right_panel.preview.clear()
            return

        widget = self.left_panel.commit_list.itemWidget(current)
        if not widget:
            return
            
        commit_id = widget.get_commit_id()
        file_path = self.file_manager.get_version_path(commit_id)
        
        if file_path:
            # For PDFs, use thumbnail
            if file_path.lower().endswith('.pdf'):
                thumbnail_path = f"{self.file_manager.thumbnails_dir}/thumb_{commit_id}.png"
                self.right_panel.preview.set_preview(thumbnail_path)
            else:
                self.right_panel.preview.set_preview(file_path)

            # Update note if exists
            note = self.file_manager.get_commit_note(commit_id)
            self.right_panel.note_panel.set_note(note) 

    def save_project(self):
        """Export all commits to a single directory"""
        # First ask for project name
        project_name, ok = QInputDialog.getText(
            self,
            "Project Name",
            "Enter project name:",
            text=f"design_project_{datetime.now().strftime('%Y%m%d')}"
        )
        
        if not ok or not project_name:
            return
            
        # Then ask for save location
        save_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Save Location",
            os.path.expanduser("~/Desktop"),
            QFileDialog.ShowDirsOnly
        )
        
        if not save_dir:
            return

        try:
            # Create project directory with user's chosen name
            project_path = os.path.join(save_dir, project_name)
            
            # Check if directory already exists
            if os.path.exists(project_path):
                reply = QMessageBox.question(
                    self,
                    "Directory Exists",
                    f"A directory named '{project_name}' already exists.\nDo you want to replace it?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    rmtree(project_path)
                else:
                    return
            
            # Create the project directory
            os.makedirs(project_path)
            
            # Copy all commit files to the project directory
            history = self.file_manager.get_commit_history()
            for commit in history:
                source_file = commit['file']
                if os.path.exists(source_file):
                    # Create filename with commit ID and original name
                    filename = os.path.basename(source_file)
                    base, ext = os.path.splitext(filename)
                    new_filename = f"{base}_v{commit['id']}{ext}"
                    dest_file = os.path.join(project_path, new_filename)
                    
                    # Copy the file
                    os.system(f"cp '{source_file}' '{dest_file}'")
            
            # Save metadata for reference
            metadata = {
                'commits': [{
                    'id': commit['id'],
                    'timestamp': commit['timestamp'],
                    'message': commit['message'],
                    'note': commit.get('note', ''),
                    'filename': f"{os.path.splitext(os.path.basename(commit['file']))[0]}_v{commit['id']}{os.path.splitext(commit['file'])[1]}"
                } for commit in history]
            }
            
            with open(os.path.join(project_path, 'project_info.json'), 'w') as f:
                json.dump(metadata, f, indent=4)
            
            QMessageBox.information(
                self,
                "Success",
                f"Project saved successfully to:\n{project_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save project: {str(e)}"
            ) 

    def on_file_changed(self, path):
        """Handle file changes"""
        if not self.left_panel.auto_commit.isChecked() or self.is_committing:
            return

        try:
            if not os.path.exists(path):
                return

            current_mtime = os.path.getmtime(path)
            if self.last_modified is None or current_mtime > self.last_modified:
                self.last_modified = current_mtime
                self.schedule_commit(path)
                
            # Re-add the file to watcher
            if path not in self.file_watcher.files():
                self.file_watcher.addPath(path)
                
        except Exception as e:
            self.is_committing = False
            QMessageBox.warning(
                self,
                "Auto-commit Warning",
                f"Failed to auto-commit changes: {str(e)}"
            )

    def on_directory_changed(self, path):
        """Handle directory changes for Adobe files"""
        if not self.watched_file or not self.left_panel.auto_commit.isChecked() or self.is_committing:
            return

        if os.path.exists(self.watched_file):
            current_mtime = os.path.getmtime(self.watched_file)
            if self.last_modified is None or current_mtime > self.last_modified:
                self.last_modified = current_mtime
                self.schedule_commit(self.watched_file)

    def schedule_commit(self, path):
        """Schedule a commit with debouncing"""
        self.is_committing = True
        self.pending_commit_path = path
        self.commit_timer.start(1000)  # 1 second delay

    def execute_pending_commit(self):
        """Execute the pending commit"""
        if self.pending_commit_path:
            self.create_auto_commit(self.pending_commit_path)
            self.pending_commit_path = None

    def create_auto_commit(self, path):
        """Create an auto-commit for the file"""
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            filename = os.path.basename(path)
            message = f"Auto-commit: {filename} modified at {timestamp}"
            commit_id = self.file_manager.save(path, message)
            
            # Add only the new commit to the list
            commit = {
                'id': commit_id,
                'timestamp': timestamp,
                'message': message,
                'file': path,
                'note': '',
                'color': None
            }
            self.left_panel.commit_list.add_commit(commit)
            
            self.status_bar.showMessage(f"Auto-committed changes to: {filename}", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"Failed to auto-commit: {str(e)}", 3000)
            print(f"Failed to create auto-commit: {e}")
        finally:
            self.is_committing = False

    def watch_file(self, file_path):
        """Start watching a file for changes"""
        # Remove any existing watched files
        if self.watched_file:
            self.file_watcher.removePath(self.watched_file)
            
        # Add new file to watch
        self.watched_file = file_path
        self.file_watcher.addPath(file_path)
        
        # Also watch the directory for some file types (like AI files)
        dir_path = os.path.dirname(file_path)
        if dir_path not in self.file_watcher.directories():
            self.file_watcher.addPath(dir_path)

        # Update status bar
        self.status_bar.showMessage(f"Watching: {os.path.basename(file_path)}") 

    def closeEvent(self, event):
        """Handle window close event"""
        try:
            # Clean up file watcher
            if self.watched_file:
                try:
                    self.file_watcher.removePath(self.watched_file)
                except:
                    pass
            self.file_watcher.deleteLater()
            
            # Clean up panels safely
            try:
                if hasattr(self.left_panel, 'commit_list'):
                    self.left_panel.commit_list.clear()
                if hasattr(self.right_panel, 'note_panel'):
                    self.right_panel.note_panel.clear()
            except:
                pass
            
            # Clean up panels
            self.left_panel.deleteLater()
            self.right_panel.deleteLater()
            
            QApplication.processEvents()
        except:
            pass
        
        super().closeEvent(event) 