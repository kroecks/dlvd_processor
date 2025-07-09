# utils.py
import os
import subprocess
import json
from colorama import Fore, Style

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv"}
FFPROBE_FIELDS = {
    "r_frame_rate": "Frame Rate",
    "width": "Width",
    "height": "Height",
    "bit_rate": "Bitrate",
    "duration": "Duration",
}

def is_video_file(filename):
    return any(filename.lower().endswith(ext) for ext in VIDEO_EXTENSIONS)

def get_video_info(filepath):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
             'stream=width,height,r_frame_rate,bit_rate,duration', '-of', 'json', filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        data = json.loads(result.stdout)
        stream = data.get("streams", [{}])[0]

        if "r_frame_rate" in stream:
            num, denom = stream["r_frame_rate"].split('/')
            stream["r_frame_rate"] = round(float(num) / float(denom), 2)

        info = {FFPROBE_FIELDS[k]: stream.get(k, None) for k in FFPROBE_FIELDS}
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        info["Size (MB)"] = round(size_mb, 2)
        info["name"] = filepath

        return info
    except Exception as e:
        return {"error": str(e)}

def calculate_quality_score(info):
    score = 0
    width = info.get("Width") or 0
    height = info.get("Height") or 0
    if width and height:
        score += ((width * height) / 1000000) * 100
    bitrate = info.get("Bitrate")
    if bitrate:
        try:
            score += (float(bitrate) / 1000000) * 10
        except: pass
    frame_rate = info.get("Frame Rate")
    if frame_rate:
        try:
            fps = float(frame_rate)
            score += fps * 0.5
            if fps > 30:
                score += (fps - 30) * 2
        except: pass
    size_mb = info.get("Size (MB)")
    if size_mb:
        try:
            score += min(float(size_mb) / 100, 20)
        except: pass
    return score

def find_best_quality_video(video_files, video_infos):
    if len(video_files) <= 1:
        print("No video files")
        return None
    best_index = 0
    best_score = 0
    for i, info in enumerate(video_infos):
        if "error" in info:
            continue
        score = calculate_quality_score(info)
        if score > best_score:
            best_score = score
            best_index = i
    return best_index
