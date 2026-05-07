import os
import time
import shutil
import zipfile
import win32gui, win32con, os

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODS_DIR = os.path.join(SCRIPT_DIR, "mods")

if not os.path.exists(MODS_DIR):
    os.makedirs(MODS_DIR)

def list_installed_mods(mods_dir):
    mods = [name for name in os.listdir(mods_dir) if os.path.isdir(os.path.join(mods_dir, name))]
    if mods:
        print(f"Installed mods:")
        nb = 0
        for mod in mods:
            print(f"{nb} - {mod}")
            nb +=1
    else:
        print(f"{YELLOW}No mods installed.{RESET}")
    input(f"{YELLOW}Press Enter to continue...{RESET}")

def snipe_files(mod_copy, game_dir):
    try:
        for root, dirs, files in os.walk(mod_copy):
            for file in files:
                mod_file_path = os.path.join(root, file)
                rel_path = os.path.relpath(mod_file_path, mod_copy)
                game_file_path = os.path.join(game_dir, rel_path)
                if os.path.exists(game_file_path):
                    try:
                        os.remove(game_file_path)
                        print(f"{GREEN}[Deleted] {rel_path}{RESET}")
                    except Exception as e:
                        print(f"{RED}[Error] Could not delete {rel_path}: {str(e)}{RESET}")
                else:
                    print(f"{YELLOW}[Info] {rel_path} not found in game directory{RESET}")
        
        print(f"{GREEN}[Success] All mod files have been removed from the game.{RESET}")
        time.sleep(2)
        
    except Exception as e:
        print(f"{RED}[Error] Unable to remove mod files: {str(e)}{RESET}")
        time.sleep(2)
    
def copy_files(mod_copy_path, game_dir):
    try:
        for root, dirs, files in os.walk(mod_copy_path):
            for file in files:
                mod_file_path = os.path.join(root, file)
                rel_path = os.path.relpath(mod_file_path, mod_copy_path)
                game_file_path = os.path.join(game_dir, rel_path)
                game_file_dir = os.path.dirname(game_file_path)
                if not os.path.exists(game_file_dir):
                    os.makedirs(game_file_dir)
                try:
                    shutil.copy2(mod_file_path, game_file_path)
                    print(f"{CYAN}[Copied] {rel_path}{RESET}")
                except Exception as e:
                    print(f"{RED}[Error] Could not copy {rel_path}: {str(e)}{RESET}")
        
        print(f"{GREEN}[Success] All mod files have been copied to the game directory.{RESET}")
        time.sleep(2)
        
    except Exception as e:
        print(f"{RED}[Error] Unable to copy mod files: {str(e)}{RESET}")
        time.sleep(2)

def extract_archive(archive):
    archive_name = os.path.splitext(os.path.basename(archive))[0]
    extract_path = os.path.join(MODS_DIR, archive_name)
    
    if os.path.exists(extract_path):
        print(f"{RED}[Error] This mod has already been installed.{RESET}")
        time.sleep(2)
    else:
        os.makedirs(extract_path)
    
        try:
            if archive.endswith('.zip'):
                with zipfile.ZipFile(archive, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                    print(f"{GREEN}[Success] archive successfully extracted.{RESET}")
                    time.sleep(2)
            else:
                print(f"{RED}[Error] unsupported archive format. Please use the .zip format.{RESET}")
                time.sleep(2)
                
        except Exception as e:
            print(f"{RED}[Error] Unable to extract this file.{RESET}")
            time.sleep(2)
    
    
def open_archive():
    filter_str = "ZIP Files\0*.zip\0All Files\0*.*\0"
    
    try:
        file_path, _, _ = win32gui.GetOpenFileNameW(
            InitialDir=os.getcwd(),
            Flags=win32con.OFN_EXPLORER | win32con.OFN_FILEMUSTEXIST | win32con.OFN_HIDEREADONLY,
            Title='Select a mod (.zip)',
            Filter=filter_str
        )
        
        if file_path:
            return os.path.abspath(file_path)
        else:
            print(f"{RED}[Error] No file selected.{RESET}")
            return None
            
    except Exception as e:
        print(f"{RED}[Error] Unable to open file dialog.{RESET}")
        time.sleep(2)
        return None
    
def gui_loop():
    while True:
        time.sleep(1)
        os.system('cls' if os.name == 'nt' else 'clear')
        print("||Cyberdeck 0.1||")
        print("Welcome to the Cyberdeck mod manager")
        print("[1] Install a mod")
        print("[2] Unnstall a mod")
        print("[3] Display installed mods")
        print("[4] Exit")
        choice = input("-> ")
        
        if choice == "1":
            chemin_archive = open_archive()
            if chemin_archive:
                extract_archive(chemin_archive)
                copy_files(os.path.join(MODS_DIR, os.path.splitext(os.path.basename(chemin_archive))[0]), GAME_DIR)

        if choice == "2":
            pass
            time.sleep(2)

        if choice == "3":
            list_installed_mods(MODS_DIR)

        if choice == "4":
            print(f"{YELLOW}Exiting the Cyberdeck mod manager.{RESET}")
            time.sleep(1)
            os._exit(0)

        if choice not in ["1", "2", "3", "4"]:
            print(f"{RED}[Error] Invalid choice. Please select a valid option.{RESET}")
            time.sleep(2)


if __name__ == "__main__":
    GAME_DIR = input("Welcome ! Please indicate the path to your game directory: ")
    while not os.path.exists(GAME_DIR):
        print(f"{RED}[Error] The specified path does not exist. Please try again.{RESET}")
        GAME_DIR = input("Please indicate the path to your game directory: ")
    gui_loop()
