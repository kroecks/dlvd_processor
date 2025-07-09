# analyzer.py
import os
from utils import is_video_file, get_video_info, find_best_quality_video, calculate_quality_score
from sanitizer import sanitize_name
from colorama import Fore, Style

FFPROBE_FIELDS = {
    "r_frame_rate": "Frame Rate",
    "width": "Width",
    "height": "Height",
    "bit_rate": "Bitrate",
    "duration": "Duration",
}
EXTRA_FIELDS = ["Size (MB)"]

def compare_video_infos(video_infos):
    differences = {}
    keys = FFPROBE_FIELDS.values()
    for key in keys:
        values = [info.get(key) for info in video_infos]
        if len(set(values)) > 1:
            differences[key] = values
    return differences

def print_video_info_table(video_files, video_infos, differences):
    headers = ["Quality Score"] + list(FFPROBE_FIELDS.values()) + EXTRA_FIELDS + ["Filename"]
    rows = []
    best_index = find_best_quality_video(video_files, video_infos)

    def strip_ansi(text):
        import re
        return re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', str(text))

    for i, (path, info) in enumerate(zip(video_files, video_infos)):
        filename = os.path.basename(path)
        sanitized_name = sanitize_name(os.path.splitext(filename)[0]) + os.path.splitext(filename)[1]
        highlight = filename != sanitized_name

        display_name = filename
        if i == best_index:
            display_name = Fore.BLUE + filename + " (BEST)" + Style.RESET_ALL
        elif highlight:
            display_name = Fore.MAGENTA + filename + Style.RESET_ALL

        row = []
        if "error" not in info:
            score = round(calculate_quality_score(info), 1)
            if i == best_index:
                score = Fore.BLUE + str(score) + Style.RESET_ALL
            row.append(score)
        else:
            row.append("ERROR")

        for key in FFPROBE_FIELDS.values():
            val = info.get(key, "N/A")
            if key in differences:
                all_vals = [other_info.get(key, None) for other_info in video_infos]
                try:
                    float_vals = [float(v) if v not in [None, 'N/A'] else float('-inf') for v in all_vals]
                    best_val = max(float_vals)
                    this_val = float(val) if val not in [None, 'N/A'] else float('-inf')
                    val = Fore.GREEN + str(val) + Style.RESET_ALL if this_val == best_val else Fore.YELLOW + str(val) + Style.RESET_ALL
                except:
                    most_common = max(set(all_vals), key=all_vals.count)
                    val = Fore.GREEN + str(val) + Style.RESET_ALL if val == most_common else Fore.YELLOW + str(val) + Style.RESET_ALL
            row.append(val)

        row.append(info.get("Size (MB)", "N/A"))
        row.append(display_name)
        rows.append(row)

    col_widths = [max(len(strip_ansi(str(cell))) for cell in col) for col in zip(*rows, headers)]
    header_line = " | ".join(f"{h:<{col_widths[i]}}" for i, h in enumerate(headers))
    separator = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    print(header_line)
    print(separator)
    for row in rows:
        print(" | ".join(str(row[i]) + ' ' * (col_widths[i] - len(strip_ansi(str(row[i])))) for i in range(len(row))))

def count_videos(dir_path):
    video_files = []
    for root, _, files in os.walk(dir_path):
        for f in files:
            if is_video_file(f):
                video_files.append(os.path.join(root, f))
    return len(video_files)

def analyze_directory(dir_path):
    video_files = []
    part_files = []
    needing_sanitize = []
    for root, _, files in os.walk(dir_path):
        for f in files:
            if is_video_file(f):
                video_files.append(os.path.join(root, f))
            elif f.endswith('.part'):
                part_files.append(os.path.join(root, f))

            filename = os.path.basename(f)
            sanitized = sanitize_name(os.path.splitext(filename)[0]) + os.path.splitext(filename)[1]
            highlight = filename != sanitized
            if highlight:
                needing_sanitize.append(filename)

    video_count = len(video_files)
    part_count = len(part_files)
    rename_count = len(needing_sanitize)
    if video_count > 1 or part_count > 0 or rename_count > 0:
        header = Fore.YELLOW + f"\n Directory: {dir_path}" + Style.RESET_ALL
        if part_count > 0:
            header = Fore.YELLOW + "INCOMPLETE DOWNLOAD! " + header + Style.RESET_ALL

        print(header)
        print(f" Video files: {video_count}, .part files: {part_count}")
        for part_file in part_files:
            print(Fore.YELLOW + f"   - Incomplete file: {os.path.basename(part_file)}" + Style.RESET_ALL)

        if video_count > 1:
            video_infos = [get_video_info(f) for f in video_files]
            diffs = compare_video_infos(video_infos)
            print("Video Properties (Best Quality marked in BLUE):\n")
            print_video_info_table(video_files, video_infos, diffs)

        if rename_count > 0:
            print(f"Names Needing Sanitization:")
            for to_sanitize in needing_sanitize:
                print(Fore.RED + f"{to_sanitize}" + Style.RESET_ALL)
                print(Fore.GREEN + f"{sanitize_name(to_sanitize)}" + Style.RESET_ALL)

    return video_files, part_files

def count_files(root):
    total_video_files = 0

    print("\nCounting Video Files...\n...")

    for entry in os.listdir(root):
        full_path = os.path.join(root, entry)
        if os.path.isdir(full_path):
            videos = count_videos(full_path)
            total_video_files += videos

    print("\n" + "=" * 50)
    print("Summary:")
    print(f" Total video files:              {total_video_files}")

def scan_root_directory(root):
    total_video_files = 0
    total_folders_with_duplicates = 0
    total_incomplete_folders = 0
    all_video_files = []
    all_video_infos = []

    for entry in os.listdir(root):
        full_path = os.path.join(root, entry)
        if os.path.isdir(full_path):
            videos, parts = analyze_directory(full_path)
            total_video_files += len(videos)
            if len(videos) > 1:
                total_folders_with_duplicates += 1
            if len(parts) > 0:
                total_incomplete_folders += 1

            for vf in videos:
                vi = get_video_info(vf)
                if "error" not in vi:
                    all_video_files.append(vf)
                    all_video_infos.append(vi)

    # Global duplicate detection
    print("\nChecking for similar videos across folders...")
    duplicates_found = 0
    threshold_seconds = 2
    threshold_resolution = 32
    visited = set()

    for i in range(len(all_video_infos)):
        for j in range(i + 1, len(all_video_infos)):
            info_a = all_video_infos[i]
            info_b = all_video_infos[j]
            if i in visited or j in visited:
                continue
            try:
                duration_diff = abs(float(info_a["Duration"]) - float(info_b["Duration"]))
                width_diff = abs(int(info_a["Width"]) - int(info_b["Width"]))
                height_diff = abs(int(info_a["Height"]) - int(info_b["Height"]))
                if duration_diff < threshold_seconds and width_diff < threshold_resolution and height_diff < threshold_resolution:
                    print(Fore.CYAN + f"Possible duplicate across folders:\n  {all_video_files[i]}\n  {all_video_files[j]}" + Style.RESET_ALL)
                    print(Fore.YELLOW + f'Duration:{info_a["Duration"]}=={info_b["Duration"]} Width={info_a["Width"]}=={info_b["Width"]} Height={info_a["Height"]}=={info_b["Height"]}' + Style.RESET_ALL)
                    duplicates_found += 1
                    visited.add(i)
                    visited.add(j)
            except:
                continue

    print("\n" + "="*50)
    print("Summary:")
    print(f" Total video files:              {total_video_files}")
    print(f" Folders with duplicates:        {total_folders_with_duplicates}")
    print(f" Folders with incomplete files:  {total_incomplete_folders}")
    print(f" Similar videos across folders:  {duplicates_found}")
    print("="*50)
