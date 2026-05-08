import os
import time
import shutil
import zipfile
import stat
import win32gui, win32con

#Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"
LIGHT_PURPLE = "\033[1;35m"

#Paths
SCRIPT_DIR = os.getcwd()
MODS_DIR = os.path.join(SCRIPT_DIR, "mods")

#Mod directory setup
if not os.path.exists(MODS_DIR):
    os.makedirs(MODS_DIR)

def is_safe_path(path, base): # Ensure that the path is within the base directory to prevent directory traversal
    real_base = os.path.realpath(base)
    real_path = os.path.realpath(path)
    return real_path.startswith(real_base)

def list_installed_mods(mods_dir): # List all installed mods by checking the subdirectories in the mods directory
    try:
        mods = sorted([name for name in os.listdir(mods_dir) if os.path.isdir(os.path.join(mods_dir, name))])
        if mods:
            print(f"Installed mods:")
            for nb, mod in enumerate(mods):
                print(f"{nb} - {mod}")
            return mods
        else:
            print(f"{YELLOW}[Warning]{RESET} No mods installed.")
            return []
    except Exception as e:
        print(f"{RED}[Error]{RESET} Could not list mods: {str(e)}")
        return []

def snipe_files(mod_copy, game_dir): # Remove files from the game directory that were added by the mod, based on the contents of the mod copy directory
    if not os.path.exists(mod_copy):
        print(f"{RED}[Error]{RESET} Mod directory not found.")
        time.sleep(2)
        return False
    
    try:
        deleted_count = 0
        failed_count = 0
        
        for root, dirs, files in os.walk(mod_copy):
            for file in files:
                mod_file_path = os.path.join(root, file)
                rel_path = os.path.relpath(mod_file_path, mod_copy)
                game_file_path = os.path.join(game_dir, rel_path)
                
                if os.path.exists(game_file_path):
                    try:
                        if os.stat(game_file_path).st_mode & stat.S_IREAD:
                            os.chmod(game_file_path, stat.S_IWRITE)
                        os.remove(game_file_path)
                        print(f"{GREEN}[Deleted]{RESET} {rel_path}")
                        deleted_count += 1
                    except PermissionError:
                        print(f"{RED}[Error]{RESET} Permission denied: {rel_path}")
                        failed_count += 1
                    except Exception as e:
                        print(f"{RED}[Error]{RESET} Could not delete {rel_path}: {str(e)}")
                        failed_count += 1
        
        print(f"{GREEN}[Success]{RESET} {deleted_count} file(s) removed from the game.")
        if failed_count > 0:
            print(f"{YELLOW}[Warning]{RESET} {failed_count} file(s) could not be deleted.")
        time.sleep(2)
        return True
        
    except Exception as e:
        print(f"{RED}[Error]{RESET} Unable to remove mod files: {str(e)}")
        time.sleep(2)
        return False
    
def copy_files(mod_copy_path, game_dir): # Copy files from the mod copy directory to the game directory, checking for existing files and prompting the user before overwriting
    if not os.path.exists(mod_copy_path):
        print(f"{RED}[Error]{RESET} Mod directory not found.")
        time.sleep(2)
        return False
    
    try:
        files_to_copy = []
        existing_files = []
        
        for root, dirs, files in os.walk(mod_copy_path):
            for file in files:
                mod_file_path = os.path.join(root, file)
                rel_path = os.path.relpath(mod_file_path, mod_copy_path)
                game_file_path = os.path.join(game_dir, rel_path)
                files_to_copy.append((mod_file_path, game_file_path, rel_path))
                if os.path.exists(game_file_path):
                    existing_files.append(rel_path)
        
        if existing_files:
            print(f"{YELLOW}[Warning]{RESET} The following files already exist and will be overwritten:")
            for f in existing_files[:5]:
                print(f"  - {f}")
            if len(existing_files) > 5:
                print(f"  ... and {len(existing_files) - 5} more")
            response = input(f"Continue? (y/n): ").lower()
            if response != 'y':
                print(f"{RED}[Cancelled]{RESET} Installation aborted.")
                time.sleep(2)
                return False
        
        for mod_file_path, game_file_path, rel_path in files_to_copy:
            game_file_dir = os.path.dirname(game_file_path)
            if not os.path.exists(game_file_dir):
                os.makedirs(game_file_dir)
            try:
                shutil.copy2(mod_file_path, game_file_path)
                print(f"{CYAN}[Copied]{RESET} {rel_path}")
            except PermissionError:
                print(f"{RED}[Error]{RESET} Permission denied: {rel_path}")
            except Exception as e:
                print(f"{RED}[Error]{RESET} Could not copy {rel_path}: {str(e)}")
        
        print(f"{GREEN}[Success]{RESET} All mod files have been copied to the game directory.")
        time.sleep(2)
        return True
        
    except Exception as e:
        print(f"{RED}[Error]{RESET} Unable to copy mod files: {str(e)}")
        time.sleep(2)
        return False

def extract_archive(archive): # Extract the mod archive to a mod copy directory, checking for existing mods and validating the archive format before extraction
    archive_name = os.path.splitext(os.path.basename(archive))[0]
    extract_path = os.path.join(MODS_DIR, archive_name)
    
    if os.path.exists(extract_path):
        print(f"{RED}[Error]{RESET} This mod has already been installed.")
        time.sleep(2)
        return False
    
    if not archive.endswith('.zip'):
        print(f"{RED}[Error]{RESET} Unsupported archive format. Please use the .zip format.")
        time.sleep(2)
        return False
    
    try:
        os.makedirs(extract_path)
        with zipfile.ZipFile(archive, 'r') as zip_ref:
            # Vérifier que les fichiers ne s'échappent pas du répertoire
            for name in zip_ref.namelist():
                member_path = os.path.normpath(os.path.join(extract_path, name))
                if not is_safe_path(member_path, extract_path):
                    print(f"{RED}[Error]{RESET} Archive contains malicious path: {name}")
                    shutil.rmtree(extract_path)
                    return False
            zip_ref.extractall(extract_path)
        print(f"{GREEN}[Success]{RESET} Archive successfully extracted.")
        time.sleep(2)
        return True
    except zipfile.BadZipFile:
        print(f"{RED}[Error]{RESET} The file is not a valid ZIP archive.")
        time.sleep(2)
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        return False
    except Exception as e:
        print(f"{RED}[Error]{RESET} Unable to extract this file: {str(e)}")
        time.sleep(2)
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        return False
    
    
def open_archive(): # Open a file dialog to select a mod archive, filtering for .zip files
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
            print(f"{RED}[Error]{RESET} No file selected.")
            return None
            
    except Exception as e:
        print(f"{RED}[Error]{RESET} Unable to open file dialog.")
        time.sleep(2)
        return None
    
def gui_loop(): # Main loop of the mod manager, displaying a menu and handling user input to install, uninstall, or list mods, or exit the program
    while True:
        time.sleep(1)
        os.system('cls' if os.name == 'nt' else 'clear')
        print("==============================")
        print(f"{LIGHT_PURPLE}Cyberdeck Mod Manager{RESET}")
        print("==============================")
        print("")
        print("[1] Install a mod")
        print("[2] Unnstall a mod")
        print("[3] Display installed mods")
        print("[4] Exit")
        choice = input("-> ")
        
        if choice == "1":
            os.system('cls' if os.name == 'nt' else 'clear')
            chemin_archive = open_archive()
            if chemin_archive:
                if extract_archive(chemin_archive):
                    mod_path = os.path.join(MODS_DIR, os.path.splitext(os.path.basename(chemin_archive))[0])
                    copy_files(mod_path, GAME_DIR)

        if choice == "2":
            os.system('cls' if os.name == 'nt' else 'clear')
            mods = list_installed_mods(MODS_DIR)
            if not mods:
                input(f"{YELLOW}Press Enter to continue...{RESET}")
            else:
                mod_nb = input("Enter the number of the mod to uninstall: ")
                if mod_nb.isdigit():
                    mod_index = int(mod_nb)
                    if 0 <= mod_index < len(mods):
                        mod_path = os.path.join(MODS_DIR, mods[mod_index])
                        snipe_files(mod_path, GAME_DIR)
                        try:
                            shutil.rmtree(mod_path)
                            print(f"{GREEN}[Success]{RESET} Mod uninstalled.")
                        except Exception as e:
                            print(f"{RED}[Error]{RESET} Could not remove mod directory: {str(e)}")
                        time.sleep(2)
                    else:
                        print(f"{RED}[Error]{RESET} Invalid number. Please select a valid option.")
                        time.sleep(2)
                else:
                    print(f"{RED}[Error]{RESET} Invalid input. Please enter a number.")
                    time.sleep(2)

        if choice == "3":
            os.system('cls' if os.name == 'nt' else 'clear')
            list_installed_mods(MODS_DIR)
            input(f"Press Enter to continue...")

        if choice == "4":
            print(f"{YELLOW}Exiting the Cyberdeck mod manager.{RESET}")
            time.sleep(1)
            os._exit(0)

        if choice not in ["1", "2", "3", "4"]:
            print(f"{RED}[Error]{RESET} Invalid choice. Please select a valid option.")
            time.sleep(2)


if __name__ == "__main__":
    GAME_DIR = input("Welcome ! Please indicate the path to your game directory: ")
    while not os.path.exists(GAME_DIR):
        print(f"{RED}[Error] The specified path does not exist. Please try again.{RESET}")
        GAME_DIR = input("Please indicate the path to your game directory: ")
    gui_loop()