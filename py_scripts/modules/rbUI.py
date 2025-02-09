import tkinter as tk
from tkinter import filedialog, ttk
import sqlite3
import os
import zipfile
import shutil
from tkinter import messagebox
from datetime import datetime

from modules.MacroDetails import MacroDetails

import modules.fileUtility as f
import modules.databaseUtil as db
import modules.constants as c

from modules.constants import ENERGY_LEVEL_MAP, BANK_MAP, INVERTED_BANK_MAP, INVERTED_ENERGY_LEVEL_MAP, SMALL_SCREEN, BIG_SCREEN

class rbUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Rekordbox Lighting Macro Import Tool - v0.0.3")

        # Initialize variables
        self.zip_file_path = tk.StringVar()
        self.xml_folder_path = tk.StringVar()
        #self.macro_name_str = tk.StringVar(value="Test")
        self.macro_id_str = tk.StringVar(value="")
        self.energy_bank_str = tk.StringVar(value="")
        self.processMode = tk.StringVar(value="new")  # Default to "Import a new macro"
        self.selectedEnergy_str = tk.StringVar(value="Select the Energy")  
        self.selectedBank_str = tk.StringVar(value="Select a Bank")

        # Create frames for the two steps
        self.step1_frame = tk.Frame(root)
        self.step2_frame = tk.Frame(root)

        self.temp_dir = f.createTempFolder()

        # maintain all new macro details in a single object
        self.newMacro = MacroDetails(self, name="Waldo Test", thumbnail="temp.png")

        # Build Step 1
        self.build_step1()

        # Build Step 2
        self.build_step2()

        # Start with Step 1 visible
        self.step1_frame.grid(row=0, column=0, sticky="nsew")
        
        self.root.geometry(SMALL_SCREEN)  # Increase height to fit all elements
        self.center_window(self.root)


    def center_window(self, window):
        """Center the app window on the display."""
        window.update_idletasks()  # Ensure geometry is updated
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def build_step1(self):
        """First step of the UI: picking the Rekordbox Backup and specifying what to do"""
        # Warning message
        warning_label = tk.Label(self.step1_frame, text="WARNING: Use this tool at your own risk.", fg="red", font="Helvetica 14 bold")
        warning_label.grid(row=0, column=0, columnspan=3, pady=10)

        # Select ZIP File
        tk.Label(self.step1_frame, text="Select Rekordbox Lighting Settings ZIP File:").grid(row=1, column=0, padx=10, pady=5, columnspan=3, sticky="w")
        tk.Entry(self.step1_frame, textvariable=self.zip_file_path, width=50).grid(row=2, column=0, padx=10, pady=5, columnspan=2, sticky="we")
        tk.Button(self.step1_frame, text="Browse", command=self.select_zip_file).grid(row=2, column=2, padx=10, pady=5)

        # Radio Buttons for Macro Mode
        tk.Label(self.step1_frame, text="I want to:").grid(row=3, column=0, sticky="e", padx=10, pady=5)
        tk.Radiobutton(self.step1_frame, text="Import a new macro", variable=self.processMode, value="new").grid(row=3, column=1, sticky="w", columnspan=2)
        tk.Radiobutton(self.step1_frame, text="Update an existing macro", variable=self.processMode, value="overwrite").grid(row=4, column=1, sticky="w", columnspan=2)

        # Next button
        tk.Button(self.step1_frame, text="Next", command=self.go_to_step2).grid(row=7, column=1, pady=10)
        tk.Button(self.step1_frame, text="Quit", command=self.handleQuit).grid(row=7, column=2, pady=10)

    def build_step2(self):
        """Build the second step of the UI."""


        uiRow = 0

        # ################ MACRO SETTINGS
        tk.Label(self.step2_frame, text="Macro Settings", font="Helvetica 14 bold").grid(row=uiRow, column=0, columnspan=3, padx=10, pady=5, sticky="w")
        
        uiRow = uiRow+1
        # Checkbox for Filtering Macros
        self.include_preset_scenes_var = tk.BooleanVar()
        self.user_scenes_checkbox = tk.Checkbutton(
            self.step2_frame,
            text="Also load preset Recordbox scenes (macros)",
            variable=self.include_preset_scenes_var,
            command=self.changeMacroFilter
        )
        self.user_scenes_checkbox.grid(row=uiRow, column=0, columnspan=3, padx=10, pady=5, sticky="w")
        
        uiRow = uiRow+1
        #existing Macro combobox
        self.macroCombobox_label = tk.Label(self.step2_frame, text="Existing Macro:").grid(row=uiRow, column=0, sticky="w", padx=10, pady=5)
        self.macroCombobox = ttk.Combobox(self.step2_frame, text="Select a macro", state='readonly')
        self.macroCombobox.grid(row=uiRow, column=1, padx=10, pady=5, sticky="w")
        self.macroCombobox.bind('<<ComboboxSelected>>', self.macroComboboxSelectionChanged) 

        # Macro ID Input
        # self.macro_id_label = tk.Label(self.step2_frame, text="Macro ID:")
        # self.macro_id_label.grid(row=uiRow, column=0, sticky="w", padx=10, pady=5)
        self.macro_id_widget = tk.Entry(self.step2_frame, textvariable=self.newMacro.id, width=5)
        self.macro_id_widget.grid(row=uiRow, column=2, padx=10, pady=5, sticky="w")
    
        uiRow = uiRow+1
        # Macro Name Input
        self.macro_name_label = tk.Label(self.step2_frame, text="Macro name:")
        self.macro_name_label.grid(row=uiRow, column=0, sticky="w", padx=10, pady=5)
        self.macro_name_widget = tk.Entry(self.step2_frame, textvariable=self.newMacro.name)
        self.macro_name_widget.grid(row=uiRow, column=1, padx=10, pady=5, sticky="w")

        tk.Button(self.step2_frame, text="Debug", command=self.debugMacro).grid(row=uiRow, column=2, pady=10, sticky="w")
        
        
        # ################ Energy - Pattern settings
        uiRow = uiRow+1
        tk.Label(self.step2_frame, text="Energy - Pattern Bank Settings", font="Helvetica 14 bold").grid(row=uiRow, column=0, columnspan=2, padx=10, pady=5, sticky="w")

        # Display assigned energy-bank combi ID for Macro
        # self.energy_bank_label = tk.Label(self.step2_frame, text="Energy-bank combi ID:", font="Helvetica 10 italic")
        # self.energy_bank_label.grid(row=uiRow, column=0, sticky="w", padx=10, pady=5)
        self.energy_bank_widget = tk.Entry(self.step2_frame, textvariable=self.energy_bank_str, width=5)
        self.energy_bank_widget.grid(row=uiRow, column=2, padx=10, pady=5, sticky="w")
        self.energy_bank_widget.config(state="disabled")

        # Energy and bank for Macro
        uiRow = uiRow+1
        tk.Label(self.step2_frame, text="Energy:").grid(row=uiRow, column=0, sticky="w", padx=10, pady=5)
        self.energy_menu = tk.OptionMenu(self.step2_frame, self.selectedEnergy_str, "") 
        self.energy_menu.grid(row=uiRow, column=1, columnspan=2, padx=10, pady=5, sticky="w")
        self.energy_menu["menu"].delete(0, "end") # Access the underlying menu and clear any existing items
        for key, value in ENERGY_LEVEL_MAP.items(): # Populate the menu with items from energy_level_map
            self.energy_menu["menu"].add_command(label=key, command=lambda val=value: self.updateSelectedEnergy(value=val))
 
        uiRow = uiRow+1
        tk.Label(self.step2_frame, text="Bank:").grid(row=uiRow, column=0, sticky="w", padx=10, pady=5)
        self.bank_menu = tk.OptionMenu(self.step2_frame, self.selectedBank_str, "") 
        self.bank_menu.grid(row=uiRow, column=1, columnspan=2, padx=10, pady=5, sticky="w") 
        self.bank_menu["menu"].delete(0, "end") # Access the underlying menu and clear any existing items
        for key, value in BANK_MAP.items(): # Populate the menu with items from energy_level_map
            self.bank_menu["menu"].add_command(label=key, command=lambda val=value: self.updateSelectedBank(value=val))

        

         # ################ Macro XML files per fixture
        uiRow = uiRow+1
        tk.Label(self.step2_frame, text="Macro XML files per fixture", font="Helvetica 14 bold").grid(row=uiRow, column=0, columnspan=3, padx=10, pady=5, sticky="w")
        
        uiRow = uiRow+1
         # Select XML Folder
        tk.Label(self.step2_frame, text="Select folder with new Macro XML files:").grid(row=uiRow, column=0, columnspan=3, padx=10, pady=5, sticky="w")
        uiRow = uiRow+1
        tk.Entry(self.step2_frame, textvariable=self.xml_folder_path).grid(row=uiRow, column=0, columnspan=2, padx=10, pady=5, sticky="we")
        tk.Button(self.step2_frame, text="Browse", command=self.select_xml_folder).grid(row=uiRow, column=2, padx=10, pady=5, sticky="w")


         # ################ ACTION AREA
        uiRow = uiRow+1
        # Progress Bar
        self.progress = ttk.Progressbar(self.step2_frame, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=uiRow, column=0, columnspan=3, padx=10, pady=10)
        
        uiRow = uiRow+1
        # Action Buttons
        back_button = tk.Button(self.step2_frame, text="Back", command=self.go_to_step1)
        back_button.grid(row=uiRow, column=0, pady=10, sticky="e")

        self.process_button = tk.Button(self.step2_frame, text="Process", command=self.handle_process_or_restart)
        self.process_button.grid(row=uiRow, column=1, pady=10, sticky="ew")

        tk.Button(self.step2_frame, text="Quit", command=self.handleQuit).grid(row=uiRow, column=2, pady=10, sticky="w")

        uiRow = uiRow+1
        # Status Display
        self.status_text = tk.Text(self.step2_frame, height=10, width=80, state="disabled")
        self.status_text.grid(row=uiRow, column=0, columnspan=3, padx=10, pady=10)

        """----- actions when building Step 2 -----------"""
        
        if self.processMode.get() == "overwrite":
            """disable macro textfield"""
            self.macro_name_widget.config(state="disabled")
            self.macro_id_widget.config(state="disabled")
            self.filter_macros()
            self.newMacro.existing = True
        else:
            self.macroCombobox.config(state="disabled")
            self.user_scenes_checkbox.config(state="disabled")
            self.macro_id_widget.config(state="disabled")
            

            # reset macro memory
            self.newMacro.existing = False
            tempName = "New Macro " + datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            self.newMacro.name.set(tempName)
            self.newMacro.id = 0
            self.newMacro.beats = c.DEFAULT_BEATS
            self.newMacro.thumbnail.set(c.DEFAULT_THUMBNAIL)
            self.newMacro.preset = 0
            self.newMacro.enabled = 1
            self.newMacro.macro_pattern_id = 0
            self.newMacro.phase = 12
            self.newMacro.initial_macro_id = 0
            self.newMacro.energy = 1
            self.newMacro.pattern = 1


        # Center the app on the screen
        self.root.geometry("600x800")  # Increase height to fit all elements
        self.center_window(self.root)
    
    def macroComboboxSelectionChanged (self, event) :
            selectedMacroLabel = self.macroCombobox.get()
            positionOfSplit = selectedMacroLabel.index(' ^ ')
            selectedId = selectedMacroLabel[0:positionOfSplit]

            macroDetail = db.loadMacroDetails(self, self.db_path, selectedId)

            # Update Macro in Memory
            self.newMacro.id = macroDetail.id
            self.newMacro.name.set(macroDetail.name.get())
            self.newMacro.beats = macroDetail.beats
            self.newMacro.fixed = macroDetail.fixed
            self.newMacro.thumbnail.set(macroDetail.thumbnail.get())
            self.newMacro.preset = macroDetail.preset
            self.newMacro.enabled = macroDetail.enabled
            self.newMacro.macro_pattern_id = macroDetail.macro_pattern_id
            self.newMacro.phase = macroDetail.phase
            self.newMacro.initial_macro_id = macroDetail.initial_macro_id
            self.newMacro.energy = macroDetail.energy
            self.newMacro.pattern = macroDetail.pattern
            self.newMacro.existing = True

            # Set Energy, Bank dropdowns and energy-bank-id field to correct name belonging to IDs
            energyName = INVERTED_ENERGY_LEVEL_MAP[macroDetail.energy] #change ID to name
            patternName = INVERTED_BANK_MAP[macroDetail.pattern] #change ID to name
            self.selectedEnergy_str.set(energyName) 
            self.selectedBank_str.set(patternName)
            self.updateAssignedEnergyBankID()

            
    def select_zip_file(self):
        """Prompt user to select a ZIP file."""
        file_path = filedialog.askopenfilename(
            title="Select Rekordbox Lighting Settings ZIP File",
            filetypes=[("ZIP Files", "*.zip")]
        )
        if file_path:
            self.zip_file_path.set(file_path)

    def select_xml_folder(self):
        """Prompt user to select a folder containing XML files."""
        folder_path = filedialog.askdirectory(title="Select XML Folder", initialdir=self.xml_folder_path.get())
        if folder_path:
            self.xml_folder_path.set(folder_path)
    
    def changeMacroFilter(self):
        self.filter_macros();
        self.macroCombobox.current(0) #This only sets focus on the first item.
        self.macroCombobox.event_generate("<<ComboboxSelected>>")

    
    def filter_macros(self):
        if self.include_preset_scenes_var.get() == 1:
            macros = db.loadAllMacros(self.db_path)
        else:
            macros = db.loadUserMacros(self.db_path)
            print("TO DO: clear downdown selections")
        

        #load into dropdown
        self.macroCombobox["values"] = [
               f"{macro_id} ^ {macro_name}" for macro_id, macro_name in macros
           ]  

    ### ENERGY-BANK LOGIC   
    def updateSelectedBank(self, value):
        #store in Object
        self.newMacro.pattern = value;
        
        #update UI
        self.selectedBank_str.set(value=INVERTED_BANK_MAP[self.newMacro.pattern])

        #update related energy-bank ID
        self.updateAssignedEnergyBankID()

    def updateSelectedEnergy(self, value):
        #store in Object
        self.newMacro.energy = value;
        
        #update UI
        self.selectedEnergy_str.set(value=INVERTED_ENERGY_LEVEL_MAP[self.newMacro.energy])

        #update related energy-bank ID
        self.updateAssignedEnergyBankID()
    
    def updateAssignedEnergyBankID(self):
        energyId = self.newMacro.energy
        patternId = self.newMacro.pattern
        energyBankId = db.loadEnergyBankIndex(self.db_path, energyIndex=energyId, patternIndex=patternId)

        #store in Object
        self.newMacro.macro_pattern_id = energyBankId
        
        #update UI
        self.energy_bank_str.set(str(energyBankId)) 
        


    def handle_process_or_restart(self):
        self.events.handle_process_or_restart()

    def debugMacro(self):
        print(self.newMacro)

    def handleQuit(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if os.path.exists(self.temp_dir):
                f.clearTempFolder(self.temp_dir)
            self.root.destroy()
    
    ### NAVIGATION
    def go_to_step2(self):
        """self.step1_frame.grid_forget()"""
        """self.step2_frame.grid(row=0, column=0, sticky="nsew")""" 

        if os.path.exists(self.zip_file_path.get()):
            self.step1_frame.grid_forget()
            for widget in self.step2_frame.winfo_children():
                widget.destroy()
            f.load_zip(self, zip_file = self.zip_file_path.get())
            self.build_step2()
            
            self.step2_frame.grid(row=0, column=0, sticky="nsew")

            # Workaround for id=o but existing=True big.... force selection of first Macro in Combobox
            self.macroCombobox.current(0) #This only sets focus on the first item.
            self.macroCombobox.event_generate("<<ComboboxSelected>>")

            # Center the app on the screen
            self.root.geometry(BIG_SCREEN)  # Increase height to fit all elements
            self.center_window(self.root)
        else:
            messagebox.showerror("Error", "Please select a valid ZIP file.")

    def go_to_step1(self):
        """Navigate back to Step 1 by rebuilding it from scratch."""
        self.step2_frame.grid_forget()

        #for widget in self.step1_frame.winfo_children():
        #    widget.destroy()

        
        self.build_step1()
        self.step1_frame.grid(row=0, column=0, sticky="nsew")
        # Center the app on the screen
        self.root.geometry(SMALL_SCREEN)  # Increase height to fit all elements
        self.center_window(self.root)
     