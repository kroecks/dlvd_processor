# sanitizer.py
import os
import re

HASHTAG_PATTERN = re.compile(r'\s*#\S+')
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv"}

WHITELIST_PATTERN = re.compile(r'[^A-Za-z0-9 _\-\(\)]+')

def sanitize_name(filename):
    base, ext = os.path.splitext(filename)

    name = HASHTAG_PATTERN.sub('', base)

    # Replace disallowed characters with dashes
    name = WHITELIST_PATTERN.sub('-', name)

    # Collapse multiple dashes or underscores
    name = re.sub(r'[-_]{2,}', '-', name)

    # Trim leading/trailing dashes or underscores
    name = name.strip('-_')

    return name.strip() + ext

def rename_recursively(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
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

        for filename in filenames:
            old_path = os.path.join(dirpath, filename)
            name, ext = os.path.splitext(filename)
            clean_name = sanitize_name(name)
            new_filename = clean_name + ext
            new_path = os.path.join(dirpath, new_filename)
            if new_filename and new_filename != filename and not os.path.exists(new_path):
                try:
                    os.rename(old_path, new_path)
                    print(f"✅ Renamed file: {old_path} → {new_path}")
                except Exception as e:
                    print(f"❌ Error renaming file {old_path}: {e}")
