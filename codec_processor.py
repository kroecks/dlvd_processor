#!/usr/bin/env python3
"""
Video Codec Analyzer and Re-encoder
Scans directories for videos, analyzes codecs, and re-encodes for better compression
Optimized for Raspberry Pi usage
"""

import os
import json
import subprocess
import argparse
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

from config_handler import get_root_dir

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Video file extensions to scan
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.3gp', '.mpg', '.mpeg'}

# Codec priority (more efficient codecs have higher scores)
CODEC_EFFICIENCY = {
    'h265': 100,  # Most efficient
    'hevc': 100,  # Same as h265
    'h264': 80,  # Good efficiency
    'avc': 80,  # Same as h264
    'vp9': 85,  # Good efficiency
    'av1': 95,  # Very efficient but slower to encode
    'mpeg4': 40,  # Less efficient
    'xvid': 35,  # Less efficient
    'divx': 35,  # Less efficient
    'wmv': 30,  # Less efficient
    'mpeg2': 25,  # Less efficient
    'mpeg1': 20,  # Least efficient
}


class VideoAnalyzer:
    def __init__(self, target_codec='h264', quality_preset='medium'):
        self.target_codec = target_codec
        self.quality_preset = quality_preset
        self.processed_files = []
        self.total_original_size = 0
        self.estimated_new_size = 0
        self.is_windows = platform.system() == 'Windows'
        self.available_encoders = self.detect_available_encoders()

    def detect_available_encoders(self) -> Dict[str, str]:
        """Detect available video encoders in ffmpeg"""
        encoder_map = {
            'h264': ['libx264', 'h264'],
            'h265': ['libx265', 'hevc_nvenc', 'h265_nvenc', 'libx265', 'hevc'],  # Added NVENC for Windows
            'vp9': ['libvpx-vp9', 'vp9'],
            'av1': ['libaom-av1', 'librav1e', 'libsvtav1', 'av1_nvenc'],  # Added NVENC AV1
            'mpeg4': ['libxvid', 'mpeg4']
        }

        available = {}

        try:
            # Get list of available encoders
            cmd = ['ffmpeg', '-encoders']
            if self.is_windows:
                # On Windows, might need to handle different executable names
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                except FileNotFoundError:
                    # Try common Windows ffmpeg locations
                    for ffmpeg_exe in ['ffmpeg.exe', r'C:\ffmpeg\bin\ffmpeg.exe']:
                        try:
                            cmd[0] = ffmpeg_exe
                            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                            break
                        except FileNotFoundError:
                            continue
                    else:
                        raise FileNotFoundError("ffmpeg not found")
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                encoder_output = result.stdout.lower()

                for codec, encoders in encoder_map.items():
                    for encoder in encoders:
                        if encoder in encoder_output:
                            available[codec] = encoder
                            logger.info(f"Found {codec} encoder: {encoder}")
                            break

                    if codec not in available:
                        logger.warning(f"No {codec} encoder found")

        except Exception as e:
            logger.error(f"Could not detect encoders: {e}")
            # Fallback to common encoders
            available = {'h264': 'libx264', 'mpeg4': 'mpeg4'}

        return available

    def get_video_info(self, filepath: Path) -> Optional[Dict]:
        """Get video information using ffprobe"""
        try:
            cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json',
                   '-show_format', '-show_streams', str(filepath)]

            # Handle Windows executable names
            if self.is_windows:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                except FileNotFoundError:
                    # Try common Windows ffprobe locations
                    for ffprobe_exe in ['ffprobe.exe', r'C:\ffmpeg\bin\ffprobe.exe']:
                        try:
                            cmd[0] = ffprobe_exe
                            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                            break
                        except FileNotFoundError:
                            continue
                    else:
                        raise FileNotFoundError("ffprobe not found")
            else:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.warning(f"Could not analyze {filepath}: {result.stderr}")
                return None

        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"Error analyzing {filepath}: {e}")
            return None

    def validate_target_codec(self) -> bool:
        """Validate that target codec is available"""
        if self.target_codec not in self.available_encoders:
            logger.error(f"Target codec '{self.target_codec}' not available!")
            logger.info("Available encoders:")
            for codec, encoder in self.available_encoders.items():
                logger.info(f"  {codec}: {encoder}")
            return False
        return True
        """Get video information using ffprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', str(filepath)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.warning(f"Could not analyze {filepath}: {result.stderr}")
                return None

        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"Error analyzing {filepath}: {e}")
            return None

    def get_video_codec(self, video_info: Dict) -> Optional[str]:
        """Extract video codec from ffprobe output"""
        try:
            for stream in video_info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    codec = stream.get('codec_name', '').lower()
                    return codec
        except Exception as e:
            logger.warning(f"Error extracting codec: {e}")
        return None

    def should_reencode(self, current_codec: str) -> bool:
        """Determine if video should be re-encoded based on codec efficiency"""
        if not current_codec:
            return False

        current_efficiency = CODEC_EFFICIENCY.get(current_codec, 0)
        target_efficiency = CODEC_EFFICIENCY.get(self.target_codec, 0)

        # Re-encode if current codec is less efficient
        return current_efficiency < target_efficiency

    def estimate_size_reduction(self, original_size: int, current_codec: str) -> int:
        """Estimate new file size after re-encoding"""
        if not current_codec:
            return original_size

        current_efficiency = CODEC_EFFICIENCY.get(current_codec, 50)
        target_efficiency = CODEC_EFFICIENCY.get(self.target_codec, 50)

        # Rough estimation: better codec = smaller file
        if target_efficiency > current_efficiency:
            # Estimate 20-40% reduction for significant codec improvements
            reduction_factor = min(0.4, (target_efficiency - current_efficiency) / 100)
            return int(original_size * (1 - reduction_factor))

        return original_size

    def scan_directory(self, directory: Path, recursive: bool = True) -> List[Dict]:
        """Scan directory for video files and analyze them"""
        video_files = []

        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        for filepath in directory.glob(pattern):
            if filepath.is_file() and filepath.suffix.lower() in VIDEO_EXTENSIONS:
                logger.info(f"Analyzing: {filepath}")

                video_info = self.get_video_info(filepath)
                if not video_info:
                    continue

                codec = self.get_video_codec(video_info)
                file_size = filepath.stat().st_size

                file_data = {
                    'path': filepath,
                    'size': file_size,
                    'codec': codec,
                    'should_reencode': self.should_reencode(codec),
                    'estimated_new_size': self.estimate_size_reduction(file_size, codec) if codec else file_size
                }

                video_files.append(file_data)
                logger.info(f"  Codec: {codec}, Size: {self.format_size(file_size)}, "
                            f"Re-encode: {file_data['should_reencode']}")

        return video_files

    def reencode_video(self, input_path: Path, output_path: Path) -> bool:
        """Re-encode video with target codec"""
        try:
            # Get the actual encoder name
            encoder = self.available_encoders.get(self.target_codec)
            if not encoder:
                logger.error(f"Encoder for {self.target_codec} not available")
                return False

            # Base command
            cmd = ['ffmpeg', '-i', str(input_path)]

            # Add hardware acceleration hints for different platforms
            if self.is_windows and 'nvenc' in encoder:
                # NVIDIA hardware acceleration on Windows
                cmd.extend(['-hwaccel', 'cuda'])
            elif not self.is_windows and encoder == 'h264_v4l2m2m':
                # Raspberry Pi hardware acceleration
                cmd.extend(['-hwaccel', 'v4l2m2m'])

            # Video encoding parameters
            cmd.extend(['-c:v', encoder])

            # Codec-specific parameters
            if 'nvenc' in encoder:
                # NVIDIA encoder settings
                cmd.extend(['-preset', 'medium', '-cq', '23'])
            elif self.target_codec in ['h264', 'h265']:
                cmd.extend(['-preset', self.quality_preset, '-crf', '23'])
            elif self.target_codec == 'vp9':
                cmd.extend(['-b:v', '0', '-crf', '30'])  # VP9 uses different quality scale
            else:
                cmd.extend(['-q:v', '3'])  # Generic quality setting

            # Audio encoding
            cmd.extend(['-c:a', 'aac', '-b:a', '128k'])

            # Output options
            cmd.extend(['-y', str(output_path)])

            # Handle Windows executable names
            if self.is_windows:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                except FileNotFoundError:
                    # Try common Windows ffmpeg locations
                    for ffmpeg_exe in ['ffmpeg.exe', r'C:\ffmpeg\bin\ffmpeg.exe']:
                        try:
                            cmd[0] = ffmpeg_exe
                            result = subprocess.run(cmd, capture_output=True, text=True)
                            break
                        except FileNotFoundError:
                            continue
                    else:
                        raise FileNotFoundError("ffmpeg not found")
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)

            logger.info(f"Re-encoding: {input_path} -> {output_path}")
            logger.debug(f"Command: {' '.join(cmd)}")

            if result.returncode == 0:
                logger.info(f"Successfully re-encoded: {output_path}")
                return True
            else:
                logger.error(f"Failed to re-encode {input_path}: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error re-encoding {input_path}: {e}")
            return False

    def format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"

    def print_summary(self, video_files: List[Dict], dry_run: bool = True):
        """Print analysis summary"""
        files_to_process = [f for f in video_files if f['should_reencode']]
        total_original = sum(f['size'] for f in files_to_process)
        total_estimated = sum(f['estimated_new_size'] for f in files_to_process)
        estimated_savings = total_original - total_estimated

        print(f"\n{'=' * 60}")
        print(f"VIDEO ANALYSIS SUMMARY {'(DRY RUN)' if dry_run else '(PROCESSING)'}")
        print(f"{'=' * 60}")
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Total video files found: {len(video_files)}")
        print(f"Files needing re-encoding: {len(files_to_process)}")
        print(
            f"Target codec: {self.target_codec.upper()} ({self.available_encoders.get(self.target_codec, 'NOT AVAILABLE')})")
        print(f"Quality preset: {self.quality_preset}")

        print(f"\nAvailable encoders:")
        for codec, encoder in self.available_encoders.items():
            status = "✓" if codec == self.target_codec else " "
            hw_accel = " (Hardware)" if 'nvenc' in encoder or 'v4l2m2m' in encoder else ""
            print(f"  {status} {codec.upper()}: {encoder}{hw_accel}")

        if files_to_process:
            print(f"\nSize Analysis:")
            print(f"  Current total size: {self.format_size(total_original)}")
            print(f"  Estimated new size: {self.format_size(total_estimated)}")
            print(f"  Estimated savings: {self.format_size(estimated_savings)} "
                  f"({(estimated_savings / total_original) * 100:.1f}%)")

            print(f"\nCodec Distribution:")
            codec_counts = {}
            for f in video_files:
                codec = f['codec'] or 'unknown'
                codec_counts[codec] = codec_counts.get(codec, 0) + 1

            for codec, count in sorted(codec_counts.items()):
                marker = "→ CONVERT" if CODEC_EFFICIENCY.get(codec, 0) < CODEC_EFFICIENCY.get(self.target_codec,
                                                                                              0) else "✓ KEEP"
                print(f"  {codec.upper()}: {count} files {marker}")

        print(f"{'=' * 60}")

    def process_files(self, video_files: List[Dict], backup_originals: bool = True):
        """Process files for re-encoding"""
        files_to_process = [f for f in video_files if f['should_reencode']]

        if not files_to_process:
            print("No files need re-encoding!")
            return

        print(f"\nProcessing {len(files_to_process)} files...")

        for i, file_data in enumerate(files_to_process, 1):
            input_path = file_data['path']

            # Create output path
            output_path = input_path.with_suffix(f'.{self.target_codec}{input_path.suffix}')

            print(f"\n[{i}/{len(files_to_process)}] Processing: {input_path.name}")

            # Re-encode the file
            if self.reencode_video(input_path, output_path):
                # Check if new file is actually smaller
                new_size = output_path.stat().st_size
                original_size = input_path.stat().st_size

                if new_size < original_size:
                    savings = original_size - new_size
                    print(f"  Success! Saved {self.format_size(savings)} "
                          f"({(savings / original_size) * 100:.1f}%)")

                    if backup_originals:
                        backup_path = input_path.with_suffix(f'{input_path.suffix}.bak')
                        input_path.rename(backup_path)
                        print(f"  Original backed up as: {backup_path.name}")
                    else:
                        input_path.unlink()
                        print(f"  Original file deleted")

                    # Rename new file to original name
                    output_path.rename(input_path)
                else:
                    print(f"  New file not smaller, keeping original")
                    output_path.unlink()  # Delete the larger re-encoded file
            else:
                print(f"  Failed to re-encode")


def perform(recursive=True, dry_run=False, codec="h265", preset='fast', backup_orig=False):

    # Validate directory
    directory = Path(get_root_dir())
    if not directory.exists():
        print(f"Error: Directory '{directory}' does not exist!")
        return 1

    # Check for required tools
    required_tools = ['ffmpeg', 'ffprobe']
    for tool in required_tools:
        try:
            # Handle Windows executable names
            cmd = [tool, '-version']
            if platform.system() == 'Windows':
                try:
                    subprocess.run(cmd, capture_output=True, check=True, timeout=5)
                except FileNotFoundError:
                    # Try with .exe extension and common paths
                    for exe_path in [f'{tool}.exe', f'C:\\ffmpeg\\bin\\{tool}.exe']:
                        try:
                            subprocess.run([exe_path, '-version'], capture_output=True, check=True, timeout=5)
                            break
                        except (FileNotFoundError, subprocess.CalledProcessError):
                            continue
                    else:
                        raise FileNotFoundError(f"{tool} not found")
            else:
                subprocess.run(cmd, capture_output=True, check=True, timeout=5)

        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            print(f"Error: {tool} not found!")
            if platform.system() == 'Windows':
                print(f"Please install ffmpeg for Windows:")
                print(f"  1. Download from https://ffmpeg.org/download.html")
                print(f"  2. Extract to C:\\ffmpeg\\")
                print(f"  3. Add C:\\ffmpeg\\bin to your PATH")
            else:
                print(f"Please install ffmpeg: sudo apt install ffmpeg")
            return 1

    # Initialize analyzer
    analyzer = VideoAnalyzer(target_codec=codec, quality_preset=preset)

    # Validate target codec is available
    if not analyzer.validate_target_codec():
        print(f"\nSuggested alternatives:")
        if 'h264' in analyzer.available_encoders:
            print(f"  --codec h264 (most compatible)")
        if 'vp9' in analyzer.available_encoders:
            print(f"  --codec vp9 (good efficiency)")
        if 'mpeg4' in analyzer.available_encoders:
            print(f"  --codec mpeg4 (basic)")
        return 1

    # Scan directory
    print(f"Scanning {'recursively' if recursive else 'non-recursively'}: {directory}")
    video_files = analyzer.scan_directory(directory, recursive)

    if not video_files:
        print("No video files found!")
        return 0

    # Print summary
    analyzer.print_summary(video_files, dry_run=dry_run)

    # Process files if not dry run
    if not dry_run:
        response = input("\nProceed with re-encoding? (y/N): ")
        if response.lower() in ['y', 'yes']:
            analyzer.process_files(video_files, backup_originals=backup_orig)
        else:
            print("Operation cancelled.")

    return 0