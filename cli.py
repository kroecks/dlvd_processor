# cli.py
import argparse
from config_handler import get_root_dir
from analyzer import scan_root_directory
from sanitizer import rename_recursively
from deduplicator import remove_duplicates

def run_cli():
    parser = argparse.ArgumentParser(description="Video Organizer CLI")
    parser.add_argument("-anl", "--analyze", action="store_true", help="Analyze packages")
    parser.add_argument("-san", "--sanitize", action="store_true", help="Sanitize package and file names")
    parser.add_argument("-dup", "--duplicates", action="store_true", help="Remove lower-quality duplicates")
    parser.add_argument("-all", "--all", action="store_true", help="Perform all operations")
    args = parser.parse_args()

    root_dir = get_root_dir()

    if args.all or (not any(vars(args).values())):
        if not any(vars(args).values()):
            print("Choose an operation:")
            print("1 - Analyze packages")
            print("2 - Sanitize packages")
            print("3 - Remove Duplicates")
            print("4 - Perform All")
            choice = input("Enter choice (1-4): ").strip()
            args = {
                "analyze": choice == "1",
                "sanitize": choice == "2",
                "duplicates": choice == "3",
                "all": choice == "4"
            }

        if args.get("all") or args.get("sanitize"):
            rename_recursively(root_dir)
        if args.get("all") or args.get("analyze"):
            scan_root_directory(root_dir)
        if args.get("all") or args.get("duplicates"):
            remove_duplicates(root_dir)

    else:
        if args.analyze:
            scan_root_directory(root_dir)
        if args.sanitize:
            rename_recursively(root_dir)
        if args.duplicates:
            remove_duplicates(root_dir)

    run_cli()
