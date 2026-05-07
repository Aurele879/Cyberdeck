import os
import time
import zipfile
import win32gui, win32con, os

if not os.path.exists("mods"):
    os.makedirs("mods")
    
# Codes ANSI pour les couleurs
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"  # Indispensable pour revenir à la couleur normale

def extract_archive(archive):
    archive_name = os.path.splitext(os.path.basename(archive))[0]
    extract_path = os.path.join("mods", archive_name)
    
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


def add_mod(path):
    extract_archive(path)
    
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
            open_archive()

        if choice == "2":
            pass
            time.sleep(2)

        if choice == "3":
            pass

        if choice == "4":
            print(f"{YELLOW}Exiting the Cyberdeck mod manager.{RESET}")
            time.sleep(1)
            os._exit(0)

        if choice not in ["1", "2", "3", "4"]:
            print(f"{RED}[Error] Invalid choice. Please select a valid option.{RESET}")
            time.sleep(2)


if __name__ == "__main__":
    gui_loop()