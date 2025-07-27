# config_handler.py
import os
import json

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def get_root_dir():
    config = load_config()
    if "ROOT_DIR" in config and os.path.exists(config["ROOT_DIR"]):
        return config["ROOT_DIR"]

    root = input("Enter the root download directory: ").strip()
    while not os.path.exists(root):
        print("Invalid directory. Try again.")
        root = input("Enter the root download directory: ").strip()

    config["ROOT_DIR"] = root
    save_config(config)
    return root

def get_temp_dir():
    config = load_config()
    if "TEMP_DIR" in config and os.path.exists(config["TEMP_DIR"]):
        return config["TEMP_DIR"]

    root = input("Enter the temp directory: ").strip()
    while not os.path.exists(root):
        print("Invalid directory. Try again.")
        root = input("Enter the temp directory: ").strip()

    config["TEMP_DIR"] = root
    save_config(config)
    return root


def get_target_dir():
    config = load_config()
    if "TGT_DIR" in config and os.path.exists(config["TGT_DIR"]):
        return config["TGT_DIR"]

    root = input("Enter the final target directory: ").strip()
    while not os.path.exists(root):
        print("Invalid directory. Try again.")
        root = input("Enter the final target directory: ").strip()

    config["TGT_DIR"] = root
    save_config(config)
    return root
