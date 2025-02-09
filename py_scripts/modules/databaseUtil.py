import sqlite3
import glob
import os
from modules.constants import DEFAULT_BEATS, DEFAULT_THUMBNAIL
from modules.MacroDetails import MacroDetails

def loadAllMacros(db_path):    
    if os.path.exists(db_path):
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT id, name FROM Macro")
        macros = cursor.fetchall()
        print(f"Number of macros found: {len(macros)}")
        connection.close()
        return macros
    else:
        print("ERROR: No db_path...")

def loadUserMacros(db_path):
    if os.path.exists(db_path):
        print("Connecting to DB.macro ...")
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT id, name FROM Macro WHERE preset !=1")
        macros = cursor.fetchall()
        print(f"Number of macros found: {len(macros)}")
        connection.close()
        return macros
    else:
        print("ERROR: No db_path...")

def loadEnergyBankIndex(db_path, energyIndex, patternIndex):
    if os.path.exists(db_path):
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute("SELECT id, energy, pattern FROM macro_pattern WHERE (energy=" + str(energyIndex) + " AND pattern="+str(patternIndex)+") ")
        energyPatternBank = cursor.fetchall()
        connection.close()

        return energyPatternBank[0][0]
    else:
        print("ERROR: No db_path...")

def loadMacroDetails(self, db_path, macro_id):
    
    if os.path.exists(db_path):
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT t1.id AS id, name, beats, fixed, thumbnail, preset, enabled, macro_pattern_id, phase, initial_macro_id, energy, pattern " +
                       "FROM macro t1 " +
                       "JOIN macro_assign t2 ON t1.id = t2.macro_id " +
                       "JOIN macro_pattern t3 ON t2.macro_pattern_id = t3.id " +
                       "WHERE t1.id=" + macro_id )
        
        row = cursor.fetchone()
        if row is not None:
            # Convert the row into a MacroDetails object
            macro_detail = MacroDetails.from_row(master=self, row=row)
            print("START Dropdown Macro Details: ")
            print(macro_detail)
            print("END Dropdown Macro Details: ")
        else:
            print("No data found.")
        connection.close()
        return macro_detail
    else:
        print("ERROR: No db_path...")

def update_database(self, db_path, xml_folder, status_logger, progress_callback=None, macro: MacroDetails = None):
    """
    Updates the database with macro and XML data.

    Args:
        db_path (str): Path to the macro.db3 database.
        xml_folder (str): Folder containing the XML files.
        status_logger (tk.Text): Text widget for logging status messages.
        progress_callback (callable): Callback function for updating progress.
        macro (MacroDetails): Name of the macro to be used in the database.

    Raises:
        FileNotFoundError: If XML files are missing.
    """

    progress_callback(20, "Starting database operations") 
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    macro_name = macro.name.get()

    try:
        # Locate XML files
        xml_files = glob.glob(os.path.join(xml_folder, "f*.xml"))
        if not xml_files:
            raise FileNotFoundError("No XML files found in the specified folder.")

        progress_callback(25, "Identified fixture XML files") 
        
        total_files = len(xml_files)
        progress_per_file = 40 // total_files #ending at 80

        # Insert or update Macro
        # Even though client code should already know if this Macro is new or not
        # Better be safe than sorry, and check once more
        cursor.execute("SELECT id FROM Macro WHERE id = ?", (macro.id,))
        row = cursor.fetchone()
        
        ###### START macro DB UPDATES
        if not row:
            #self.update_progress_and_log(15, f"The Macro '{macro_name}' is a NEW macr, inserting into macro table.")
            macro.existing = False
            cursor.execute(
                "INSERT INTO macro (name, beats, fixed, thumbnail, preset, enabled) VALUES (?, ?, ?, ?, ?, ?)",
                (macro_name, DEFAULT_BEATS, 0, DEFAULT_THUMBNAIL, 0, 1),
            )

            # Commit changes and retrieve the last inserted ID
            macro.id = cursor.lastrowid
            progress_callback(30, f"Inserted '{macro_name}' with {macro.id} into macro table")

        else:
            macro.existing = True
            cursor.execute(
                "UPDATE Macro SET name = ?, beats = ?, fixed = ?, thumbnail = ?, preset = ?, enabled = ? WHERE id = ?",
                (macro_name, DEFAULT_BEATS, 0, DEFAULT_THUMBNAIL, 0, 1, macro.id)
            )

            progress_callback(30, f"Updated macro '{macro_name}' with id {macro.id}")
        ###### END macro DB UPDATES

        ###### START macro_assign DB UPDATES
        macro_pattern_id = macro.macro_pattern_id

        if not macro.existing: # If Macro is new, then enter a new row in macro_assign
            # find the highest phase (position in the UI) available for this energy-bank combination
            #progress_callback(35, f"New Macro --> new macro_assign needed, querying for available phase (UI position)")
            cursor.execute(
                "SELECT MAX(phase) FROM macro_assign WHERE macro_pattern_id = ?;",
                (macro_pattern_id,)
            )
            max_phase = cursor.fetchone()[0]
            next_phase = (max_phase + 1) if max_phase else 1

            # create new macro_assign entry for this macro.id
            cursor.execute(
                    "INSERT INTO macro_assign (macro_pattern_id, phase, macro_id, initial_macro_id) VALUES (?, ?, ?, ?);",
                    (macro_pattern_id, next_phase, macro.id, macro.id)
                )
            progress_callback(40, f"Created new macro_assign with macro_pattern_id {macro_pattern_id} at phase {next_phase}")
        else:
            # macro exists, update macro_pattern_id belonging to the macro.id
            progress_callback(35, f"Exsting Macro --> find macro_assign and update pattern_id according to UI selections")

            cursor.execute(
                "SELECT macro_id FROM macro_assign WHERE macro_pattern_id = ? AND macro_id = ?;",
                (macro_pattern_id, macro.id)
            )

            cursor.execute(
                "UPDATE macro_assign SET macro_pattern_id = ? WHERE macro_id = ?",
                (macro_pattern_id, macro.id)
            )
            progress_callback(40, f"Updated macro_assign to macro_pattern_id {macro_pattern_id} ")
        ###### END macro_assign DB UPDATES
                
        ###### START Macro_data DB UPDATES
        for index, xml_file in enumerate(xml_files): #Loop over fixctures to load into DB
            fileName = os.path.basename(xml_file)
            fixtureId = int(fileName[1:-4])

            with open(xml_file, "r") as file:
                xml_content = file.read()

            # Insert or update Macro_data
            cursor.execute(
                "SELECT macro_id FROM Macro_data WHERE macro_id = ? AND macro_fixture_id = ?",
                (macro.id, fixtureId),
            )
            if cursor.fetchone():
                cursor.execute(
                    "UPDATE Macro_data SET data = ? WHERE macro_id = ? AND macro_fixture_id = ?",
                    (xml_content, macro.id, fixtureId),
                )
        
            else:
                cursor.execute(
                    "INSERT INTO Macro_data (macro_id, macro_fixture_id, data) VALUES (?, ?, ?)",
                    (macro.id, fixtureId, xml_content),
                )

            # Log progress
            #status_logger.insert("end", f"Processed {fileName}\n")
            progress_callback(40 + (index + 1) * progress_per_file, f"Inserted Fixture: {fixtureId} with file {fileName} into Macro_data table")
        ###### END Macro_data DB UPDATES

        connection.commit()

        
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()
