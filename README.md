# Manga PDF Converter

A Python script that automatically converts manga/comic book images organised in volume folders into individual PDF files. Perfect for creating digital manga volumes from scanned pages or downloaded chapters.

---


## 🚀 Features

- **Automatic Volume Detection**: Scans for folders starting with "v" followed by numbers (v1, v2, v10, etc.)
- **Recursive Image Search**: Finds all images in subfolders within each volume
- **Multiple Format Support**: Handles PNG, JPG, JPEG, BMP, GIF, TIFF, and WEBP files
- **Robust Error Handling**: Continues processing even if individual images fail to load
- **Memory Efficient**: Properly closes images after processing to prevent memory leaks
- **macOS Compatible**: Designed to work within macOS file handle limitations
- **Sorted Output**: Maintains proper page order in the final PDF

## 📋 Requirements

- Python 3.6 or higher
- Pillow (PIL) library

## 🔧 Installation

1. Clone this repository:
```bash
git clone https://github.com/AlistairMacDiarmid/manga-pdf-converter.git
cd manga-pdf-converter
```

2. Install required dependencies:
```bash
pip install Pillow
```

Or using pip3:
```bash
pip3 install Pillow
```

## 📁 Expected Folder Structure

The script expects your manga to be organised in folders that start with "v" followed by numbers:

```
manga_collection/
├── v1_chapter_01/
│   ├── page_001.jpg
│   ├── page_002.jpg
│   └── page_003.jpg
├── v1_chapter_02/
│   ├── page_001.jpg
│   └── page_002.jpg
├── v2_chapter_01/
│   ├── page_001.jpg
│   ├── page_002.jpg
│   └── page_003.jpg
└── v2_chapter_02/
    ├── page_001.jpg
    └── page_002.jpg
```

## 🖥️ Usage

### Basic Usage

```bash
python3 manga_pdf_converter.py /path/to/your/manga/folder
```

### Example

```bash
python3 manga_pdf_converter.py ~/Downloads/OnePiece
```

This will create PDF files in the current directory:
- `v1.pdf` - Contains all pages from v1_chapter_01, v1_chapter_02, etc.
- `v2.pdf` - Contains all pages from v2_chapter_01, v2_chapter_02, etc.

### Output

The script provides clear feedback during processing:

```
Processing v1 (2 retraces)
✅ Saved v1.pdf (45 pages)

Processing v2 (3 retraces)
✅ Saved v2.pdf (67 pages)
```

## 🎯 How It Works

1. **Volume Detection**: Scans the root directory for folders matching the pattern `v[number]`
2. **Grouping**: Groups related folders by volume number (e.g., v1_ch1, v1_ch2 → volume v1)
3. **Image Collection**: Recursively searches each volume's folders for supported image files
4. **PDF Creation**: Converts all images for each volume into a single PDF file
5. **Cleanup**: Properly closes all images to free memory

## 🛠️ Design Considerations

### macOS File Handle Limitations

This script was specifically designed to work within macOS limitations on the number of files that can be open simultaneously. The code:

- Opens images one at a time rather than all at once
- Immediately closes each image after copying it to memory
- Uses `.copy()` to create independent image objects before closing the original
- Processes images sequentially to avoid hitting file descriptor limits

This approach ensures compatibility with macOS systems whilst maintaining good performance.

## 🛠️ Customisation

### Adding New Image Formats

To support additional image formats, modify the `supported` tuple in the `get_image_files_recursive` function:

```python
supported = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp', '.svg')
```

### Changing Folder Pattern

To match different folder naming patterns, modify the regex in `get_all_retrace_folders`:

```python
# For folders like "Volume_1", "Volume_2"
retrace_pattern = re.compile(r'^(Volume_\d+)', re.IGNORECASE)

# For folders like "Vol1", "Vol2"
retrace_pattern = re.compile(r'^(Vol\d+)', re.IGNORECASE)
```

## 🐛 Troubleshooting

### Common Issues

**"No images to convert" warning**
- Check that your folders contain supported image formats
- Verify folder names start with "v" followed by numbers
- Ensure images aren't corrupted

**"Failed to open first image" error**
- The first image in the sequence may be corrupted
- Try moving or removing the problematic image

**Memory issues with large volumes**
- The script processes images efficiently, but very large volumes (1000+ pages) may require more RAM
- Consider splitting large volumes into smaller parts

### Debugging

Add the `-v` flag for verbose output (requires modifying the script):

```python
# Add this near the top of main()
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Licence

This project is released into the public domain. Feel free to use, modify, and distribute as needed.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 🔄 Changelog

### v1.0.0
- Initial release
- Basic volume detection and PDF conversion
- Support for common image formats
- Error handling and memory management

## 📧 Support

If you encounter any issues or have questions, please:
1. Check the troubleshooting section above
2. Search existing [GitHub issues](https://github.com/AlistairMacDiarmid/manga-pdf-converter/issues)
3. Create a new issue with detailed information about your problem

## ⭐ Acknowledgements

- Built with [Pillow](https://pillow.readthedocs.io/) for image processing
- Inspired by the need to organise digital manga collections

---

**Note**: This tool is intended for personal use with legally obtained manga/comic content. Please respect copyright laws and only use with content you own or have permission to convert.