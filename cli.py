# cli.py
import argparse
from config_handler import get_root_dir
from analyzer import scan_root_directory, count_files
from sanitizer import rename_recursively
from deduplicator import remove_duplicates
from part_remover import remote_parts

def run_cli():
    parser = argparse.ArgumentParser(description="Video Organizer CLI")
    parser.add_argument("-anl", "--analyze", action="store_true", help="Analyze packages")
    parser.add_argument("-san", "--sanitize", action="store_true", help="Sanitize package and file names")
    parser.add_argument("-dup", "--duplicates", action="store_true", help="Remove lower-quality duplicates")
    parser.add_argument("-prt", "--parts", action="store_true", help="Remove Part files")
    parser.add_argument("-all", "--all", action="store_true", help="Perform all operations")
    args = parser.parse_args()

    root_dir = get_root_dir()

    if args.all or (not any(vars(args).values())):
        if not any(vars(args).values()):
            print("Choose an operation:")
            print("1 - Analyze packages")
            print("2 - Sanitize packages")
            print("3 - Remove Duplicates")
            print("4 - Remove part files")
            print("5 - Count Files")
            print("9 - Perform All")
            print("0 - Exit")
            choice = input("Enter choice (1-9): ").strip()
            args = {
                "analyze": choice == "1",
                "sanitize": choice == "2",
                "duplicates": choice == "3",
                "parts": choice == "4",
                "all": choice == "9",
                "count": choice == "5",
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

        if args.get("all") or args.get("count"):
            count_files(root_dir)

    else:
        if args.analyze:
            scan_root_directory(root_dir)
        if args.sanitize:
            rename_recursively(root_dir)
        if args.duplicates:
            remove_duplicates(root_dir)

    run_cli()
