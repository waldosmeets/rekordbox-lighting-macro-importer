
from tkinter import filedialog
from tkinter import messagebox

import os
import tempfile
import shutil
import time

import modules.fileUtility as f


from modules.fileUtility import load_config
from modules.databaseUtil import update_database
from modules.constants import MACRO_DB_FILENAME, USER_DB_FILENAME

class rbEvents:
    def __init__(self, ui):
        self.ui = ui
        self.is_processing_complete = False
        load_config(self.ui.zip_file_path, self.ui.xml_folder_path)


    def handle_process_or_restart(self):
        """Handle the Process button logic (Process or Restart)."""
        if self.is_processing_complete:
            self.restart_application()
        else:
            self.process()

    def update_progress_and_log(self, progress_value, log_message):
        """Update the progress bar and log a message to the status text with detailed database operations."""
        self.ui.progress["value"] = progress_value
        self.ui.status_text.config(state="normal")
        self.ui.status_text.insert("end", log_message + "\n")
        self.ui.status_text.config(state="disabled")
        self.ui.status_text.see("end")
        time.sleep(0.1)  # Add a minor delay to ensure UI updates are visible
        self.ui.root.update_idletasks()  # Ensure the UI updates immediately

    def process(self):
        """Perform the extraction, update, and save the new ZIP file."""
        self.update_progress_and_log(0, "Import process STARTED.")

        zip_file = self.ui.zip_file_path.get()
        xml_folder = self.ui.xml_folder_path.get()
        macro_name = self.ui.newMacro.name.get()
        

        if not zip_file or not xml_folder:
            self.update_progress_and_log(100, "Error: ZIP file and XML folder are required.\n")
            return
        
        if not os.path.exists(xml_folder):
            self.update_progress_and_log(100, "Error: XML folder does not exist.\n")
            return

        if not macro_name.strip():
            self.update_progress_and_log(100, "Error: Macro name is required.\n")
            return
        
        if not self.ui.newMacro.macro_pattern_id:
            self.update_progress_and_log(100, "Error: No proper macro-pattern combination is set.\n")
            return
        
        if not self.ui.newMacro.id:
            if self.macro.existing:
                self.update_progress_and_log(100, "Error: Congrats, you find a glicht in the system! Restart the app and you'll be fine...\n")
                return

        self.update_progress_and_log(8, f"Verified all things needed to start rocessing macro: {macro_name}\n")

        self.update_progress_and_log(10, "File and folder validation completed.")

        temp_dir = self.ui.temp_dir
        db_path = os.path.join(temp_dir, MACRO_DB_FILENAME)
        user_db_path = os.path.join(temp_dir, USER_DB_FILENAME)

        try:

            # Update the database
            update_database(self, db_path, xml_folder, self.ui.status_text, lambda progress, msg: self.update_progress_and_log(progress, msg), self.ui.newMacro)

            # Prompt the user to save the new ZIP file
            save_file = filedialog.asksaveasfilename(
                title="Save Updated ZIP File",
                defaultextension=".zip",
                filetypes=[("ZIP Files", "*.zip")]
            )

            if save_file:
                # Pack the updated database back into a ZIP file
                f.pack_database(db_path, save_file, user_db_path, lambda progress, msg: self.update_progress_and_log(progress, msg))

                self.update_progress_and_log(90, f"New ZIP file saved to: {save_file}")
                self.update_progress_and_log(100, f"Process complete.")

                self.on_processing_complete()
            else:
                self.update_progress_and_log(100, f"Process cancelled by user.")

        except Exception as e:
            self.update_progress_and_log(100, f"Error: {e}")

        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
            self.update_progress_and_log(100, f"Removed temp files")
        

    def on_processing_complete(self):
        """Handle UI updates after processing is complete."""
        self.is_processing_complete = True
        self.ui.process_button.config(text="Start Over")
        # Disable all fields except 'Start Over'
        #self.ui.zip_file_path.set("")
        #self.ui.xml_folder_path.set("")
        #self.ui.newMacro.name.set("")
        #for widget in [self.ui.zip_file_path, self.ui.xml_folder_path, self.ui.macro_name_]:
        #    widget.trace_vdelete("w", widget.trace_id)  # Remove existing traces to prevent editing
        self.ui.root.update_idletasks()

    def restart_application(self):
        """Restart the application to its initial state."""
        self.is_processing_complete = False
        #self.ui.zip_file_path.set("")
        #self.ui.xml_folder_path.set("")
        #self.ui.newMacro.name.set("")
        self.ui.status_text.config(state="normal")
        self.ui.status_text.delete("1.0", "end")
        self.ui.status_text.config(state="disabled")
        self.ui.progress["value"] = 0
        self.ui.process_button.config(text="Process")
        self.ui.go_to_step1()
    
 
