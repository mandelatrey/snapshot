import os
import json
from datetime import datetime
from PIL import Image
import io
import sys
from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QIcon
from ui.main_window import FileManagerUI
from ui.utils.icon_loader import load_app_icon
try:
    from psd_tools import PSDImage
except ImportError:
    PSDImage = None
try:
    import fitz  # PyMuPDF for PDF handling
except ImportError:
    fitz = None
import shutil

class FileManager:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.thumbnails_dir = os.path.join(repo_path, "thumbnails")
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)
        if not os.path.exists(self.thumbnails_dir):
            os.makedirs(self.thumbnails_dir)
        self.metadata_file = os.path.join(repo_path, "metadata.json")
        self.metadata = self.load_metadata()
        self.supported_formats = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".psd", ".ai", ".svg", ".pdf"]

    def load_metadata(self):
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        return {"saves": [], "branches": {"main": []}}

    def save_metadata(self):
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=4)

    def generate_thumbnail(self, file_path, save_id):
        """Generate and save a thumbnail for the file"""
        thumbnail_path = os.path.join(self.thumbnails_dir, f"thumb_{save_id}.png")
        
        try:
            if file_path.lower().endswith('.pdf') and fitz:
                # Handle PDF files
                pdf_document = fitz.open(file_path)
                # Get first page
                page = pdf_document[0]
                # Convert to image with reasonable resolution
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                # Convert to PIL Image
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                pdf_document.close()
            elif file_path.lower().endswith('.psd') and PSDImage:
                # Handle PSD files
                psd = PSDImage.open(file_path)
                # Try different methods to get the image
                try:
                    image = psd.composite()
                except AttributeError:
                    try:
                        image = psd.compose()
                    except AttributeError:
                        image = psd.as_PIL()
            else:
                # Handle other image formats
                image = Image.open(file_path)
            
            # Convert to RGB if necessary
            if image and image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Generate thumbnail
            image.thumbnail((200, 200), Image.LANCZOS)
            image.save(thumbnail_path, "PNG")
            return thumbnail_path
        except Exception as e:
            print(f"Failed to generate thumbnail: {e}")
            return None

    def save(self, file_path, message, branch="main"):
        # Validate file format
        if not any(file_path.lower().endswith(fmt) for fmt in self.supported_formats):
            raise ValueError(f"Unsupported file format. Please use one of: {', '.join(self.supported_formats)}")
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_id = len(self.metadata["saves"])
        version_dir = os.path.join(self.repo_path, f"v{save_id}")
        os.makedirs(version_dir, exist_ok=True)

        # Copy the file using shutil instead of os.system
        version_file = os.path.join(version_dir, os.path.basename(file_path))
        try:
            shutil.copy2(file_path, version_file)
        except Exception as e:
            raise IOError(f"Failed to copy file: {str(e)}")

        # Generate thumbnail
        thumbnail_path = self.generate_thumbnail(version_file, save_id)

        # Create save data
        save_data = {
            "id": save_id,
            "timestamp": timestamp,
            "message": message,
            "branch": branch,
            "file": version_file,
            "thumbnail": thumbnail_path,
            "note": "",
            "color": None
        }
        
        # Update metadata
        self.metadata["saves"].append(save_data)
        
        # Ensure branch exists
        if branch not in self.metadata["branches"]:
            self.metadata["branches"][branch] = []
        self.metadata["branches"][branch].append(save_id)
        
        self.save_metadata()
        return save_id

    def get_commit_history(self, branch="main"):
        """Get commit history for a branch"""
        # Get all commits that belong to this branch
        branch_commits = []
        for save in self.metadata["saves"]:
            if save["branch"] == branch:
                branch_commits.append(save)
        return branch_commits

    def get_version_path(self, save_id):
        """Get the file path for a specific version"""
        for save in self.metadata["saves"]:
            if save["id"] == save_id:
                return save["file"]
        return None

    def delete_commit(self, save_id):
        """Delete a commit and its associated files"""
        # Find the commit
        commit_to_delete = None
        for save in self.metadata["saves"]:
            if save["id"] == save_id:
                commit_to_delete = save
                break
                
        if not commit_to_delete:
            return

        try:
            # Delete the version directory
            version_dir = os.path.dirname(commit_to_delete["file"])
            if os.path.exists(version_dir):
                shutil.rmtree(version_dir)

            # Delete thumbnail if it exists
            if commit_to_delete.get("thumbnail") and os.path.exists(commit_to_delete["thumbnail"]):
                os.remove(commit_to_delete["thumbnail"])

            # Remove from branches
            branch = commit_to_delete["branch"]
            if branch in self.metadata["branches"]:
                self.metadata["branches"][branch] = [
                    cid for cid in self.metadata["branches"][branch] 
                    if cid != save_id
                ]

            # Remove from saves list
            self.metadata["saves"] = [
                save for save in self.metadata["saves"] 
                if save["id"] != save_id
            ]

            # Save updated metadata
            self.save_metadata()
            return True
        except Exception as e:
            print(f"Error deleting commit: {e}")
            return False

    def get_commit_message(self, save_id):
        """Get commit message for a specific save"""
        for save in self.metadata["saves"]:
            if save["id"] == save_id:
                return save.get("message", "")
        return ""

    def get_commit_note(self, save_id):
        """Get commit note for a specific save"""
        for save in self.metadata["saves"]:
            if save["id"] == save_id:
                return save.get("note", "")
        return ""

    def update_commit(self, save_id, message=None, color=None, note=None):
        """Update commit metadata"""
        for save in self.metadata["saves"]:
            if save["id"] == save_id:
                if message is not None:
                    save["message"] = message
                if color is not None:
                    save["color"] = color
                if note is not None:
                    save["note"] = note
                self.save_metadata()
                break

    def __del__(self):
        """Cleanup when FileManager is deleted"""
        try:
            # Close any open file handles
            for attr_name in dir(self):
                attr = getattr(self, attr_name)
                if hasattr(attr, 'close'):
                    try:
                        attr.close()
                    except:
                        pass
        except:
            pass

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Snapshot")
    app.setWindowIcon(load_app_icon("ui/assets/app-icon.png"))
    
    repo_path = os.path.expanduser("~/design_file_manager")
    fm = FileManager(repo_path)
    window = FileManagerUI(fm)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()