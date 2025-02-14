from datetime import datetime
import re
from .advanced_search_dialog import AdvancedSearchDialog

class SearchHandler:
    def __init__(self, commit_list, file_manager):
        self.commit_list = commit_list
        self.file_manager = file_manager

    def filter_commits(self, search_text):
        search_text = search_text.lower()
        
        # Get currently selected commit ID before filtering
        current_commit_id = None
        current_item = self.commit_list.currentItem()
        if current_item:
            widget = self.commit_list.itemWidget(current_item)
            if widget:
                current_commit_id = widget.get_commit_id()

        # Clear and reload commits
        self.commit_list.clear()
        history = self.file_manager.get_commit_history()
        
        for commit in history:
            # Search in message and note
            message = commit['message'].lower()
            note = commit.get('note', '').lower()
            
            if search_text in message or search_text in note:
                self.commit_list.add_commit(commit)

    def show_advanced_search(self):
        dialog = AdvancedSearchDialog(self.commit_list.parent())
        if dialog.exec_():
            self.apply_advanced_search(dialog)

    def apply_advanced_search(self, dialog):
        search_text = dialog.search_input.text()
        use_regex = dialog.regex_checkbox.isChecked()
        date_from = dialog.date_from.date().toPython()
        date_to = dialog.date_to.date().toPython()
        file_type = dialog.file_type.currentText()

        # Clear and reload commits
        self.commit_list.clear()
        history = self.file_manager.get_commit_history()
        
        for commit in history:
            # Check date range
            commit_date = datetime.strptime(commit['timestamp'], '%Y-%m-%d %H:%M:%S').date()
            if not (date_from <= commit_date <= date_to):
                continue

            # Check file type
            if file_type != "All Files":
                file_path = commit['file']
                if not file_path.lower().endswith(file_type.lower()):
                    continue

            # Check text match
            message = commit['message']
            note = commit.get('note', '')
            
            if use_regex:
                try:
                    pattern = re.compile(search_text, re.IGNORECASE)
                    if not (pattern.search(message) or pattern.search(note)):
                        continue
                except re.error:
                    continue
            else:
                search_text = search_text.lower()
                if not (search_text in message.lower() or search_text in note.lower()):
                    continue

            # Add matching commit
            self.commit_list.add_commit(commit)

    # ... rest of search-related methods ... 