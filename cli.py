# cli.py
import argparse
from config_handler import get_root_dir, get_target_dir
from analyzer import scan_root_directory, count_files
from sanitizer import rename_recursively
from deduplicator import remove_duplicates
from part_remover import remote_parts
from codec_processor import perform
from file_mover import copy_all_contents, move_all_contents

def run_cli():
    parser = argparse.ArgumentParser(description="Video Organizer CLI")
    parser.add_argument("-anl", "--analyze", action="store_true", help="Analyze packages")
    parser.add_argument("-san", "--sanitize", action="store_true", help="Sanitize package and file names")
    parser.add_argument("-dup", "--duplicates", action="store_true", help="Remove lower-quality duplicates")
    parser.add_argument("-prt", "--parts", action="store_true", help="Remove Part files")
    parser.add_argument("-all", "--all", action="store_true", help="Perform all operations")
    parser.add_argument("-cdr", "--codecdr", action="store_true", help="Codec Dry Run")
    parser.add_argument("-cds", "--codecsv", action="store_true", help="Codec Save")
    parser.add_argument("-mov", "--move", action="store_true", help="Move Files")
    parser.add_argument("-copy", "--copy", action="store_true", help="Copy Files")
    args = parser.parse_args()

    root_dir = get_root_dir()

    if args.all or (not any(vars(args).values())):
        if not any(vars(args).values()):
            print("Choose an operation:")
            print("anal - Analyze packages")
            print("sani - Sanitize packages")
            print("remd - Remove Duplicates")
            print("remp - Remove part files")
            print("count - Count Files")
            print("codecdr - Codec Dry Run")
            print("codecsv - Codec Save")
            print("mov - Move Files")
            print("copy - Copy Files")
            print("all - Perform All")
            print("0 - Exit")
            choice = input("Enter choice: ").strip()
            args = {
                "analyze": choice == "anal",
                "sanitize": choice == "sani",
                "duplicates": choice == "remd",
                "parts": choice == "remp",
                "all": choice == "all",
                "count": choice == "count",
                "codecdr": choice == "codecdr",
                "codecsv": choice == "codecsv",
                "copy": choice == "copy",
                "move": choice == "mov",
                "group": choice == "group",
                "exit": choice == "0"
            }

        if args.get("exit"):
            exit(0)

        if args.get("all") or args.get("sanitize"):
            rename_recursively(root_dir)
        if args.get("all") or args.get("analyze"):
            scan_root_directory(root_dir)
        if args.get("all") or args.get("duplicates"):
            remove_duplicates(root_dir)
        if args.get("all") or args.get("parts"):
            remote_parts(root_dir)

        if args.get("all") or args.get("codecdr"):
            perform(dry_run=True)
        if args.get("all") or args.get("codecsv"):
            perform(dry_run=False)

        if args.get("all") or args.get("count"):
            count_files(root_dir)
        if args.get("all") or args.get("copy"):
            copy_all_contents(get_target_dir())
        if args.get("all") or args.get("move"):
            move_all_contents(get_target_dir())

    else:
        if args.analyze:
            scan_root_directory(root_dir)
        if args.sanitize:
            rename_recursively(root_dir)
        if args.duplicates:
            remove_duplicates(root_dir)

    run_cli()
