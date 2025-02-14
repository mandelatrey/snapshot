from PySide2.QtGui import QIcon, QPixmap, QImage
from PIL import Image
import io

def load_app_icon(path):
    """Load and process application icon to avoid PNG profile warnings"""
    try:
        # Open with PIL and convert to RGB
        with Image.open(path) as img:
            img = img.convert('RGB')
            
            # Save to bytes buffer without color profile
            buffer = io.BytesIO()
            img.save(buffer, format='PNG', icc_profile=None)
            buffer.seek(0)
            
            # Convert to QImage and then to QIcon
            qimg = QImage.fromData(buffer.getvalue())
            pixmap = QPixmap.fromImage(qimg)
            return QIcon(pixmap)
    except Exception:
        # Fallback to direct loading if something goes wrong
        return QIcon(path) 