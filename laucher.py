""" THIS IS AN UNUSED  FILE.  """






import sys
import os
import subprocess
import json

def get_internal_path(relative_path):
    
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_config_path():
    """ Stores 'first run' flag in User Home (so it survives deleting the EXE) """
    config_dir = os.path.join(os.path.expanduser("~"), ".ringzauber")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    return os.path.join(config_dir, "launcher_state.json")

def main():
    config_file = get_config_path()
    # Path to the bundled python interpreter inside the one-file exe
    executable = sys.executable
    
    # Check if first run
    is_first_run = True
    if os.path.exists(config_file):
        is_first_run = False

    # 1. Launch Intro (Only first time)
    if is_first_run:
        intro_script = get_internal_path("ringzauber_intro.py")
        # Run and wait for it to close
        subprocess.run([executable, intro_script], check=False)
        
        # Mark as finished
        with open(config_file, 'w') as f:
            json.dump({"first_run": False}, f)

    # 2. Launch Main App
    main_script = get_internal_path("ringzauber_ui.py")
    
    # Run the main app as a subprocess and exit the launcher
    subprocess.Popen([executable, main_script])
    sys.exit(0)

if __name__ == "__main__":
    main()
