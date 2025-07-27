# file_mover.py

import os
import shutil
from colorama import Fore, Style
from config_handler import get_root_dir, get_target_dir, get_temp_dir


def copy_all_contents(dst_dir):
    src_dir = get_root_dir()
    if not os.path.exists(src_dir):
        print(Fore.RED + f"Source directory does not exist: {src_dir}" + Style.RESET_ALL)
        return

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
        print(Fore.YELLOW + f"Created destination directory: {dst_dir}" + Style.RESET_ALL)

    copied_files = 0
    for root, dirs, files in os.walk(src_dir):
        rel_path = os.path.relpath(root, src_dir)
        target_root = os.path.join(dst_dir, rel_path)

        os.makedirs(target_root, exist_ok=True)

        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_root, file)

            shutil.copy2(src_file, dst_file)
            print(Fore.CYAN + f"📄 Copied: {src_file} -> {dst_file}" + Style.RESET_ALL)
            copied_files += 1

    print(f"\n{Fore.GREEN}Done. Copied {copied_files} files to {dst_dir}.{Style.RESET_ALL}")

def move_all_contents(dst_dir):
    src_dir = get_root_dir()
    if not os.path.exists(src_dir):
        print(Fore.RED + f"Source directory does not exist: {src_dir}" + Style.RESET_ALL)
        return

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
        print(Fore.YELLOW + f"Created destination directory: {dst_dir}" + Style.RESET_ALL)

    moved_files = 0
    for root, dirs, files in os.walk(src_dir, topdown=False):
        rel_path = os.path.relpath(root, src_dir)
        target_root = os.path.join(dst_dir, rel_path)

        os.makedirs(target_root, exist_ok=True)

        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_root, file)

            shutil.move(src_file, dst_file)
            print(Fore.MAGENTA + f"🚚 Moved: {src_file} -> {dst_file}" + Style.RESET_ALL)
            moved_files += 1

    # Optionally remove empty folders in source after move
    for root, dirs, _ in os.walk(src_dir, topdown=False):
        for d in dirs:
            dir_path = os.path.join(root, d)
            if not os.listdir(dir_path):  # empty
                os.rmdir(dir_path)
                print(Fore.YELLOW + f"🧹 Removed empty folder: {dir_path}" + Style.RESET_ALL)

    print(f"\n{Fore.GREEN}Done. Moved {moved_files} files to {dst_dir}.{Style.RESET_ALL}")
