
# 📚 Manga PDF Converter

A comprehensive Python script that converts manga image folders into organised PDF files with multiple processing modes. Originally created as a personal project to organise my manga collection for digital reading across devices.

## 🆕 Recent Updates

- **✨ Added Hybrid Mode**: Intelligent processing that groups volume folders while keeping standalone chapters separate
- **📁 Organised Output Structure**: PDFs are now saved in a structured `PDF/[manga-name]/` directory
- **📖 Enhanced Chapter Processing**: Each folder can now be converted to its own PDF
- **🔍 Improved Volume Detection**: Better pattern matching for volume-based organisation
- **🛡️ Safe Filename Handling**: Automatic sanitisation of problematic characters in filenames
- **🎯 Command-line Interface**: Full argparse integration with help documentation

## ✨ Features

- **🎛️ Three Processing Modes**: Choose between volumes, chapters, or hybrid processing
- **📂 Automatic Output Organisation**: Creates organised output directories based on manga name
- **🔄 Recursive Image Search**: Finds images in nested folder structures
- **🖼️ Multiple Image Format Support**: PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP
- **⚡ Error Handling**: Continues processing even if individual images fail
- **💾 Memory Efficient**: Properly manages image memory to prevent crashes
- **🎨 Quality Preservation**: Maintains image quality during PDF conversion
- **📊 Progress Tracking**: Real-time feedback on processing status

## 🛠️ Installation

### Prerequisites

- **Python 3.6+** 🐍
- **Pillow (PIL)** library 📷

### 📦 Setup

1. **Clone this repository:**
```bash
git clone https://github.com/AlistairMacDiarmid/manga-pdf-converter.git
cd manga-pdf-converter
```

2. **Install required dependencies:**
```bash
pip install Pillow
```

3. **Verify installation:**
```bash
python3 manga_pdf_converter.py --help
```

## 🚀 Usage

### 📝 Basic Syntax

```bash
python3 manga_pdf_converter.py <path_to_manga_folder> [--mode MODE]
```

### 🎯 Processing Modes

#### 1. 📚 Volumes Mode (Default)
Perfect for manga organised with volume numbering systems.

```bash
python3 manga_pdf_converter.py /path/to/manga --mode volumes
# or simply:
python3 manga_pdf_converter.py /path/to/manga
```

**📁 Example folder structure:**
```
One Piece/
├── v1/
│   ├── 001.jpg
│   ├── 002.jpg
│   └── ...
├── v1.1/
├── v1.2/
├── v2/
└── v2.1/
```

**📄 Output:**
- `PDF/One Piece/v1.pdf` (contains v1, v1.1, v1.2)
- `PDF/One Piece/v2.pdf` (contains v2, v2.1)

**✨ Best for:**
- Official manga releases
- Scanlations organised by volume
- Series with clear volume divisions

#### 2. 📖 Chapters Mode
Ideal for chapter-by-chapter organisation.

```bash
python3 manga_pdf_converter.py /path/to/manga --mode chapters
```

**📁 Example folder structure:**
```
Attack on Titan/
├── Chapter 1 - To You, 2000 Years From Now/
│   ├── 01.png
│   ├── 02.png
│   └── ...
├── Chapter 2 - That Day/
├── Chapter 3 - Night of the Disbanding Ceremony/
└── Special Chapter - Ilse's Notebook/
```

**📄 Output:**
- `PDF/Attack on Titan/Chapter 1 - To You, 2000 Years From Now.pdf`
- `PDF/Attack on Titan/Chapter 2 - That Day.pdf`
- `PDF/Attack on Titan/Chapter 3 - Night of the Disbanding Ceremony.pdf`
- `PDF/Attack on Titan/Special Chapter - Ilse's Notebook.pdf`

**✨ Best for:**
- Weekly/monthly releases
- Web manga
- Individual chapter collections

#### 3. 🔄 Hybrid Mode
The smart choice for mixed organisation patterns.

```bash
python3 manga_pdf_converter.py /path/to/manga --mode hybrid
```

**📁 Example folder structure:**
```
Naruto/
├── Vol.1 Chapter 1 - Uzumaki Naruto/
├── Vol.1 Chapter 2 - Konohamaru/
├── Vol.1 Chapter 3 - Sasuke Uchiha/
├── Vol.2 Chapter 4 - Hatake Kakashi/
├── Vol.2 Chapter 5 - Failure/
├── Special Chapter 50 - Naruto's School Days/
├── Omake - Behind the Scenes/
└── Color Pages Collection/
```

**📄 Output:**
- `PDF/Naruto/Vol1.pdf` (contains all Vol.1 chapters)
- `PDF/Naruto/Vol2.pdf` (contains all Vol.2 chapters)
- `PDF/Naruto/Special_Chapter_50_-_Naruto's_School_Days.pdf`
- `PDF/Naruto/Omake_-_Behind_the_Scenes.pdf`
- `PDF/Naruto/Color_Pages_Collection.pdf`

**✨ Best for:**
- Mixed collection sources
- Series with volumes + extras
- Complex folder hierarchies

## 📊 Output Structure

The script creates a clean, organised output structure:

```
📁 Original Location/
├── 📁 Your Manga Folder/
│   ├── 📁 Chapter folders...
│   └── 🖼️ Image files...
└── 📁 PDF/
    └── 📁 Your Manga Folder/
        ├── 📄 Volume_1.pdf
        ├── 📄 Volume_2.pdf
        └── 📄 ...
```

**🎯 Benefits:**
- ✅ Original files remain untouched
- ✅ Clear separation between source and output
- ✅ Easy to find and organise PDFs
- ✅ Maintains manga series structure

## 🖼️ Supported Image Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| PNG | `.png` | ✅ Full support |
| JPEG | `.jpg`, `.jpeg` | ✅ Full support |
| BMP | `.bmp` | ✅ Full support |
| GIF | `.gif` | ✅ Animated → Static |
| TIFF | `.tiff` | ✅ Full support |
| WebP | `.webp` | ✅ Full support |

## 💡 Examples & Use Cases

### 🎨 Converting Different Manga Types

#### **🏴‍☠️ Long-running Series (One Piece style)**
```bash
# Large series with clear volume divisions
python3 manga_pdf_converter.py "/Users/reader/Manga/One Piece" --mode volumes
```

#### **⚔️ Seasonal Manga (Attack on Titan style)**
```bash
# Chapter-focused series
python3 manga_pdf_converter.py "/Users/reader/Manga/Attack on Titan" --mode chapters
```

#### **📚 Mixed Collection**
```bash
# When you have both volumes and standalone chapters
python3 manga_pdf_converter.py "/Users/reader/Manga/My Collection" --mode hybrid
```

### 🛠️ Advanced Usage

#### **📋 Command Help**
```bash
python3 manga_pdf_converter.py --help
```

#### **🔍 Testing with Sample Data**
```bash
# Test on a small folder first
python3 manga_pdf_converter.py "/path/to/test/manga" --mode chapters
```

## ⚙️ How It Works

### 🔄 Processing Pipeline

1. **📂 Folder Scanning**: 
   - Recursively scans the provided directory
   - Identifies all supported image files
   - Maintains alphabetical/numerical order

2. **🎯 Grouping Logic**: 
   - **Volumes**: Matches patterns like `v1`, `v2`, `vol1`, etc.
   - **Chapters**: Each folder = one PDF
   - **Hybrid**: Smart detection of volume patterns + standalone chapters

3. **🖼️ Image Processing**:
   - Opens images using PIL/Pillow
   - Converts to RGB format for PDF compatibility
   - Handles various image sizes and orientations

4. **📄 PDF Generation**:
   - Combines images into single PDF files
   - Preserves image quality and aspect ratios
   - Optimises file size without quality loss

5. **📁 Output Organisation**:
   - Creates structured directory hierarchy
   - Uses safe filename conventions
   - Maintains series organisation

### 🧠 Smart Features

- **🔍 Pattern Recognition**: Automatically detects volume numbering schemes
- **🛡️ Error Recovery**: Continues processing even with corrupted files
- **💾 Memory Management**: Efficiently handles large image collections
- **📊 Progress Feedback**: Real-time status updates during processing

## 🚨 Error Handling & Troubleshooting

### ⚠️ Common Issues & Solutions

#### **"No volume folders found"**
```
❌ Problem: Script can't find volume-numbered folders
✅ Solution: 
   • Check folder naming (should be v1, v2, etc.)
   • Try --mode chapters or --mode hybrid
   • Verify folder structure matches expected patterns
```

#### **"Failed to open image"**
```
❌ Problem: Corrupted or unreadable image files
✅ Solution:
   • Script automatically skips corrupted files
   • Check image file integrity
   • Ensure files have correct extensions
```

#### **Memory errors with large collections**
```
❌ Problem: System runs out of memory
✅ Solution:
   • Process smaller batches
   • Close other applications
   • Increase system virtual memory
   • Process one series at a time
```

#### **PDFs not generating**
```
❌ Problem: No output files created
✅ Solution:
   • Check folder permissions
   • Verify image files exist in subfolders
   • Ensure sufficient disk space
   • Check console output for specific errors
```

### 🔧 Performance Tips

#### **🚀 Speed Optimisation**
- Use SSD storage for faster I/O
- Process series individually rather than in bulk
- Close unnecessary applications during processing
- Use smaller test folders to verify settings first

#### **💾 Memory Management**
- Monitor system memory usage
- Process large series in smaller batches
- Restart script between very large collections
- Consider splitting massive series into parts

#### **📁 Organisation Tips**
- Use consistent folder naming conventions
- Group similar series together
- Keep original files as backup
- Regularly clean up old PDF outputs

## 🎯 Best Practices

### 📋 Before Processing
- [ ] **Backup original files** - Always keep originals safe
- [ ] **Test on small sample** - Verify settings work correctly
- [ ] **Check folder structure** - Ensure it matches expected patterns
- [ ] **Free up disk space** - PDFs can be large files
- [ ] **Close other applications** - Maximise available memory

### ⚡ During Processing
- [ ] **Monitor progress** - Watch console output for errors
- [ ] **Don't interrupt** - Let the process complete fully
- [ ] **Check system resources** - Ensure adequate memory/CPU
- [ ] **Be patient** - Large collections take time

### ✅ After Processing
- [ ] **Verify PDF quality** - Open a few files to check
- [ ] **Check completeness** - Ensure all expected PDFs were created
- [ ] **Organise output** - Move PDFs to your reading device/app
- [ ] **Clean up if needed** - Remove any incomplete or error files

---

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

### v1.0.1
- Added Hybrid Mode for mixed folder structures  
- Improved volume folder detection with enhanced regex patterns  
- Organised PDFs into `PDF/[manga-name]/` directories  
- Added safe filename sanitisation to avoid invalid characters  
- Implemented full command-line interface with argparse and help documentation  
- Enhanced error handling and progress reporting

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

## 🎨 About This Project

This started as a personal solution to a very specific problem: I had thousands of manga images scattered across different folder structures, and I wanted to read them comfortably on my tablet. What began as a simple script to combine images into PDFs evolved into a comprehensive tool that handles the various ways manga collections are organised.

### 🌟 Why This Tool Exists
- **📱 Digital Reading**: Perfect PDFs for tablets and e-readers  
- **📚 Organisation**: Clean, consistent file structure  
- **💾 Space Efficiency**: Compressed, organised storage  
- **🔄 Flexibility**: Handles different organisation schemes  
- **⚡ Automation**: No more manual PDF creation

### 🤝 Community
If you find this useful for your own manga organisation, that's awesome! Feel free to:  
- 🐛 Report issues you encounter  
- 💡 Suggest improvements or new features  
- 🌟 Share how you're using it  
- 🔧 Contribute enhancements

The goal is to make manga collection management as painless as possible for everyone who loves digital reading!

---

**Happy reading! 📖✨**

**Note**: This tool is intended for personal use with legally obtained manga/comic content. Please respect copyright laws and only use with content you own or have permission to convert.