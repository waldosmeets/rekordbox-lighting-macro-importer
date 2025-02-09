import os
import zipfile
import json
from tkinter import messagebox
import tempfile
import shutil  # For removing the directory

from modules.constants import CONFIG_FILE, MACRO_DB_FILENAME, USER_DB_FILENAME

### TEMP FOLDER MANAGEMENT


def createTempFolder():
    temp_dir = tempfile.mkdtemp()
    return temp_dir

def clearTempFolder(temp_dir):
    shutil.rmtree(temp_dir)


### CONFIG LOGIC ###
def save_config(zip_file, xml_folder):
    """Save paths to a configuration file."""
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    config = {"zip_file": zip_file, "xml_folder": xml_folder}
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)

# Additional utility function to load the config
def load_config(zip_path_var, xml_path_var):
    """Load the configuration from the config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
            zip_path_var.set(config.get("zip_file", ""))
            xml_path_var.set(config.get("xml_folder", ""))
            return
    return {}


### ZIP LOGIC ###
def load_zip(self, zip_file):

    if not zip_file:
        messagebox.showerror("Error", "Please select a valid ZIP file.")
        return

    temp_dir = self.temp_dir

    """Check if the ZIP file contains required database files."""
    try:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            if MACRO_DB_FILENAME not in zip_ref.namelist() or USER_DB_FILENAME not in zip_ref.namelist():
                raise FileNotFoundError(
                    "The selected ZIP file doesn't contain the required database files. "
                    "Ensure it is exported directly from Rekordbox."
                )
            zip_ref.extract(MACRO_DB_FILENAME, temp_dir)
            zip_ref.extract(USER_DB_FILENAME, temp_dir)
    
    except zipfile.BadZipFile:
        raise FileNotFoundError("Invalid ZIP file.")
    
    else:
        """ shutil.rmtree(temp_dir, ignore_errors=True) """
        self.db_path = os.path.join(temp_dir, MACRO_DB_FILENAME)



def pack_database(db_path, zip_file, user_db_path=None, progress_callback=None):
    """
    Creates a new ZIP file with the updated database files.

    Args:
        db_path (str): Path to the macro.db3 file.
        zip_file (str): Path to save the new ZIP file.
        user_db_path (str): Path to the user.db3 file (optional).
        progress_callback (callable): Callback function for updating progress.

    Raises:
        FileNotFoundError: If any database file is missing.
    """
    
    print(f"Creating zip with\n {db_path} and \n {user_db_path}")

    try:
        with zipfile.ZipFile(zip_file, 'w') as zip_out:
            # Add macro.db3
            if os.path.exists(db_path):
                zip_out.write(db_path, MACRO_DB_FILENAME)
            else:
                raise FileNotFoundError("macro.db3 not found.")

            # Add user.db3
            if user_db_path and os.path.exists(user_db_path):
                zip_out.write(user_db_path, USER_DB_FILENAME)

            # Update progress
            if progress_callback:
                progress_callback(90, "done ZIPping")
    except Exception as e:
        raise Exception(f"Error while creating ZIP file: {e}")
