# 📦 DLVd Processor

A command-line utility for managing and cleaning up video downloads—especially from batch downloaders like JDownloader. It can:

* 🔍 Analyze folders of video files for quality comparison
* 🧹 Sanitize filenames and folder names
* 📁 Identify incomplete `.part` downloads
* 🔁 Detect and remove duplicate video files (both within and across folders)

---

## 📁 Folder Structure

```
dlvd_processor/
├── analyzer.py           # Analyzes video metadata, highlights duplicates
├── sanitizer.py          # Cleans up invalid filenames and folders
├── remover.py            # Removes lower-quality duplicates (TBD)
├── utils.py              # Shared helper functions
├── cli.py                # CLI interface logic
├── config.json           # (Generated) Stores your chosen ROOT_DIR
├── main.py               # Entry point to run from CLI
```

---

## ⚙️ Installation

1. Install [FFmpeg](https://ffmpeg.org/download.html) and ensure `ffprobe` is in your system PATH.
2. Install Python dependencies:

```bash
pip install colorama
```

---

## 🚀 Usage

### Command-line flags

```bash
python main.py -anl   # Analyze packages
python main.py -san   # Sanitize package names
python main.py -dup   # Remove duplicates
python main.py -all   # Run all operations
```

### Interactive Mode

Run without flags to use the menu:

```bash
python main.py
```

You'll see:

```
Choose an operation:
1 - Analyze packages
2 - Sanitize packages
3 - Remove Duplicates
4 - Perform All
```

---

## 🧐 Features

### Analyze

* Compares video files in a folder and highlights differences in metadata (resolution, bitrate, frame rate, etc.)
* Identifies the highest-quality version
* Flags any `.part` files (incomplete downloads)
* Detects duplicates **across folders** (based on duration/resolution similarity)
* Highlights filenames that would change if sanitized

### Sanitize

* Removes invalid characters (`<>:"/\\|?*!`)
* Strips hashtags like `#example` from file and folder names
* Trims extra whitespace

### Remove Duplicates

* (Planned/partially implemented) Removes inferior duplicates automatically, keeping the best version

---

## 📝 Configuration

The first time you run the script, you'll be prompted for the root directory (e.g., your JDownloader folder). This will be saved to a local `config.json` for reuse.

To change it later, delete `config.json` or set it manually.

---

## 🧪 Example Output

```
 Directory: D:/Downloads/SomeVideoSet
 Video files: 3, .part files: 1
   - Incomplete file: funny_cat_video.mp4.part

Video Properties (Best Quality marked in BLUE):

Quality Score | Width | Height | Bitrate | Duration | Size (MB) | Filename
--------------+-------+--------+---------+----------+-----------+-----------------------------
 324.1        | 1920  | 1080   | 5000000 | 123.45   | 50.2      | cat_video_hd.mp4 (BEST)
 290.5        | 1280  | 720    | 3000000 | 123.40   | 32.1      | cat_video_sd.mp4
```

---

## 📌 Requirements

* Python 3.8+
* FFmpeg (`ffprobe` must be accessible from the command line)

---

## 🙋‍♂️ Contributions

Open to contributions! Feel free to PR improvements like:

* Better duplicate detection
* GUI or web dashboard
* Logging and export support

---

## 📄 License

MIT License
