# Snapshot - Design File Version Control System

Snapshot is a desktop application that helps designers manage versions of their design files. It provides an easy way to track changes, add notes, and maintain a history of your design iterations.

## Features

- Track changes in design files (PSD, AI, PDF, PNG, JPG, etc.)
- Auto-commit functionality for automatic version tracking
- Add notes to each version
- Color-code versions for better organization
- Search through version history
- Export versions
- Preview support for various file formats

## Installation

1. Clone the repository:
git clone https://github.com/yourusername/snapshot.git

2. Install dependencies:
pip install -r requirements.txt

3. Start the application:
python main.py

## Usage Guide

### Basic Operations

1. **Selecting a File**
   - Click "Select File" to choose your design file
   - The application will start watching this file for changes

2. **Auto-Commit**
   - Enable "Auto-commit on file changes" to automatically save versions
   - Each time you save your design file, a new version will be created

3. **Manual Commit**
   - Click the "Commit" button to manually save a version
   - Enter a message to describe your changes

### Managing Versions

1. **Viewing Versions**
   - All versions appear in the left panel
   - Click any version to preview it in the right panel

2. **Adding Notes**
   - Right-click a version and select "Add/Edit Note"
   - Add detailed notes about the changes

3. **Color Coding**
   - Right-click a version and select "Set Color"
   - Choose from preset colors or pick a custom color

4. **Searching**
   - Use the search bar to find specific versions
   - Type keywords from commit messages or notes
   - Click the "Search" button to execute the search

### Additional Features

1. **Exporting Versions**
   - Right-click a version and select "Export Version"
   - Choose a location to save the file

2. **Project Management**
   - "Save Project": Export all versions as a package
   - "Delete Project": Remove all versions (use with caution)

3. **File Watching**
   - The application monitors your selected file
   - Use "Re-link file being watched" if you move the file

## Tips

- Use descriptive commit messages for better organization
- Add notes to important versions
- Color-code versions based on their status or importance
- Regular commits help maintain a good version history
- Use search to quickly find specific versions

## Supported File Formats

- Adobe Photoshop (.psd)
- Adobe Illustrator (.ai)
- PDF (.pdf)
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- BMP (.bmp)
- SVG (.svg)

## Troubleshooting

1. **File Not Updating**
   - Click "Re-link file being watched"
   - Ensure auto-commit is enabled

2. **Preview Not Showing**
   - Check if the file format is supported
   - Ensure the file is not corrupted

3. **Search Not Working**
   - Clear the search box and try again
   - Check for typos in search terms

## Requirements

- Python 3.7 or higher
- PySide2
- Pillow (PIL)
- PyMuPDF (for PDF support)
- psd-tools (for PSD support)
- numpy

## System Requirements

- Operating System: Windows 10/11, macOS 10.14+, or Linux
- RAM: 4GB minimum (8GB recommended)
- Storage: 500MB free space
- Display: 1280x720 minimum resolution

## License

MIT License

Copyright (c) 2024 Snapshot

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

For support, please open an issue in the GitHub repository or contact the development team.
