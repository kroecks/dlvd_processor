# sanitizer.py
import os
import re

HASHTAG_PATTERN = re.compile(r'\s*#\S+')
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv"}
WHITELIST_PATTERN = re.compile(r'[^A-Za-z0-9 _\-\(\)\.]+')


def detect_video_type(filepath):
    """Detect if a file is MP4 or MKV by reading its magic bytes."""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(12)

            # MP4 signature: starts with ftyp at bytes 4-8
            if len(header) >= 12 and header[4:8] == b'ftyp':
                return '.mp4'

            # MKV signature: starts with EBML header (0x1A45DFA3)
            if len(header) >= 4 and header[0:4] == b'\x1A\x45\xDF\xA3':
                return '.mkv'

            # AVI signature: starts with RIFF
            if len(header) >= 4 and header[0:4] == b'RIFF':
                return '.avi'

    except Exception as e:
        print(f"⚠️  Could not detect file type for {filepath}: {e}")

    return None


def sanitize_name(filename):
    """Sanitize filename while preserving extension."""
    base, ext = os.path.splitext(filename)

    # Remove hashtags
    name = HASHTAG_PATTERN.sub('', base)

    # Replace disallowed characters with dashes
    name = WHITELIST_PATTERN.sub('-', name)

    # Collapse multiple dashes or underscores
    name = re.sub(r'[-_]{2,}', '-', name)

    # Trim leading/trailing dashes or underscores
    name = name.strip('-_')

    return name.strip() + ext


def rename_recursively(root_dir):
    """Recursively rename files and directories with sanitized names."""
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # Rename directories
        for dirname in dirnames:
            old_path = os.path.join(dirpath, dirname)
            new_name = sanitize_name(dirname)
            new_path = os.path.join(dirpath, new_name)

            if new_name and new_name != dirname and not os.path.exists(new_path):
                try:
                    os.rename(old_path, new_path)
                    print(f"✅ Renamed folder: {old_path} → {new_path}")
                except Exception as e:
                    print(f"❌ Error renaming folder {old_path}: {e}")

        # Rename files
        for filename in filenames:
            old_path = os.path.join(dirpath, filename)

            # Sanitize the full filename (with extension)
            new_filename = sanitize_name(filename)

            # Check if file is missing extension
            name, ext = os.path.splitext(new_filename)
            if not ext:
                # Try to detect the video type
                detected_ext = detect_video_type(old_path)
                if detected_ext:
                    new_filename = name + detected_ext
                    print(f"🔍 Detected {detected_ext} for: {filename}")
                else:
                    print(f"⚠️  No extension detected for: {filename} - skipping")
                    continue

            new_path = os.path.join(dirpath, new_filename)

            if new_filename and new_filename != filename and not os.path.exists(new_path):
                try:
                    os.rename(old_path, new_path)
                    print(f"✅ Renamed file: {old_path} → {new_path}")
                except Exception as e:
                    print(f"❌ Error renaming file {old_path}: {e}")
