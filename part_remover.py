# part_remover.py
import os
from utils import is_part_file
from colorama import Fore, Style

def remote_parts(root_dir):
    removed_count = 0
    for root, _, files in os.walk(root_dir):
        part_files = [os.path.join(root, f) for f in files if is_part_file(f)]
        if len(part_files) < 1:
            continue

        for i, path in enumerate(part_files):
            os.remove(path)
            print(Fore.RED + f"🗑️ Deleted part: {path}" + Style.RESET_ALL)
            removed_count += 1

    print(f"\n{Fore.GREEN}Done. Removed {removed_count} duplicates.{Style.RESET_ALL}")
