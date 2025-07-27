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

def set_config():
    get_root_dir(True)
    get_target_dir(True)

def get_root_dir(update=False):
    config = load_config()
    currentDirectory = ""
    if "ROOT_DIR" in config and os.path.exists(config["ROOT_DIR"]):
        currentDirectory = config["ROOT_DIR"]

    if not update and currentDirectory != "":
        return currentDirectory

    root = input("Enter the root download directory:" + "(" + config["ROOT_DIR"] + ") :").strip()
    if root == "" or root == None and "ROOT_DIR" in config and os.path.exists(config["ROOT_DIR"]):
        root = config["ROOT_DIR"]
    while not os.path.exists(root):
        print("Invalid directory. Try again.")
        root = input("Enter the root download directory: ").strip()

    config["ROOT_DIR"] = root
    save_config(config)
    return root

def get_target_dir(update=False):
    config = load_config()
    currentDirectory = ""
    if "TGT_DIR" in config and os.path.exists(config["TGT_DIR"]):
        currentDirectory = config["TGT_DIR"]

    if not update and currentDirectory != "":
        return currentDirectory

    root = input("Enter the final target directory:" + "(" + currentDirectory + ") :").strip()
    if (root == "" or root is None) and ("TGT_DIR" in config and os.path.exists(config["TGT_DIR"])):
        root = config["TGT_DIR"]
    while not os.path.exists(root):
        print("Invalid directory. Try again.")
        root = input("Enter the final target directory: ").strip()

    config["TGT_DIR"] = root
    save_config(config)
    return root
