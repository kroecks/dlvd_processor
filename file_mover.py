# file_mover.py

import os
import shutil
from colorama import Fore, Style
from config_handler import get_root_dir, get_target_dir

# Define common video file extensions
VIDEO_EXTENSIONS = {
    '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v',
    '.mpg', '.mpeg', '.3gp', '.ogv', '.ts', '.mts', '.m2ts', '.vob'
}


def is_video_file(filename):
    """Check if file is a video file and not a .part file"""
    if filename.lower().endswith('.part'):
        return False

    _, ext = os.path.splitext(filename.lower())
    return ext in VIDEO_EXTENSIONS


def copy_all_contents(dst_dir):
    src_dir = get_root_dir()
    if not os.path.exists(src_dir):
        print(Fore.RED + f"Source directory does not exist: {src_dir}" + Style.RESET_ALL)
        return

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
        print(Fore.YELLOW + f"Created destination directory: {dst_dir}" + Style.RESET_ALL)

    copied_files = 0
    skipped_files = 0

    for root, dirs, files in os.walk(src_dir):
        rel_path = os.path.relpath(root, src_dir)
        target_root = os.path.join(dst_dir, rel_path)

        # Only create directory if we have video files to copy
        video_files = [f for f in files if is_video_file(f)]
        if video_files:
            os.makedirs(target_root, exist_ok=True)

        for file in files:
            if is_video_file(file):
                src_file = os.path.join(root, file)
                dst_file = os.path.join(target_root, file)

                shutil.copy2(src_file, dst_file)
                print(Fore.CYAN + f"📄 Copied: {src_file} -> {dst_file}" + Style.RESET_ALL)
                copied_files += 1
            else:
                skipped_files += 1
                if file.lower().endswith('.part'):
                    print(Fore.YELLOW + f"⏸️  Skipped .part file: {os.path.join(root, file)}" + Style.RESET_ALL)
                else:
                    print(Fore.GRAY + f"⏭️  Skipped non-video: {os.path.join(root, file)}" + Style.RESET_ALL)

    print(f"\n{Fore.GREEN}Done. Copied {copied_files} video files to {dst_dir}.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Skipped {skipped_files} non-video files.{Style.RESET_ALL}")


def move_all_contents(dst_dir):
    src_dir = get_root_dir()
    if not os.path.exists(src_dir):
        print(Fore.RED + f"Source directory does not exist: {src_dir}" + Style.RESET_ALL)
        return

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
        print(Fore.YELLOW + f"Created destination directory: {dst_dir}" + Style.RESET_ALL)

    moved_files = 0
    skipped_files = 0

    for root, dirs, files in os.walk(src_dir, topdown=False):
        rel_path = os.path.relpath(root, src_dir)
        target_root = os.path.join(dst_dir, rel_path)

        # Only create directory if we have video files to move
        video_files = [f for f in files if is_video_file(f)]
        if video_files:
            os.makedirs(target_root, exist_ok=True)

        for file in files:
            if is_video_file(file):
                src_file = os.path.join(root, file)
                dst_file = os.path.join(target_root, file)

                shutil.move(src_file, dst_file)
                print(Fore.MAGENTA + f"🚚 Moved: {src_file} -> {dst_file}" + Style.RESET_ALL)
                moved_files += 1
            else:
                skipped_files += 1
                if file.lower().endswith('.part'):
                    print(Fore.YELLOW + f"⏸️  Skipped .part file: {os.path.join(root, file)}" + Style.RESET_ALL)
                else:
                    print(Fore.GRAY + f"⏭️  Skipped non-video: {os.path.join(root, file)}" + Style.RESET_ALL)

    # Only remove empty folders in source after move (but leave folders with .part files)
    for root, dirs, remaining_files in os.walk(src_dir, topdown=False):
        for d in dirs:
            dir_path = os.path.join(root, d)
            if not os.listdir(dir_path):  # completely empty
                os.rmdir(dir_path)
                print(Fore.YELLOW + f"🧹 Removed empty folder: {dir_path}" + Style.RESET_ALL)

    print(f"\n{Fore.GREEN}Done. Moved {moved_files} video files to {dst_dir}.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Skipped {skipped_files} non-video files (including .part files).{Style.RESET_ALL}")