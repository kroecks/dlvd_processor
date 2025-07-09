# deduplicator.py
import os
from utils import is_video_file, get_video_info, find_best_quality_video
from colorama import Fore, Style

def remove_duplicates(root_dir):
    removed_count = 0
    for root, _, files in os.walk(root_dir):
        video_files = [os.path.join(root, f) for f in files if is_video_file(f)]
        if len(video_files) <= 1:
            continue

        infos = [get_video_info(f) for f in video_files]
        best_index = find_best_quality_video(video_files, infos)
        if best_index is None:
            continue

        for i, path in enumerate(video_files):
            if i != best_index:
                try:
                    os.remove(path)
                    print(Fore.RED + f"🗑️ Deleted lower quality: {path}" + Style.RESET_ALL)
                    removed_count += 1
                except Exception as e:
                    print(Fore.YELLOW + f"⚠️ Error deleting {path}: {e}" + Style.RESET_ALL)

    print(f"\n{Fore.GREEN}Done. Removed {removed_count} duplicates.{Style.RESET_ALL}")
