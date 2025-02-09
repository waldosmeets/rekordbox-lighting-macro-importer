import tkinter as tk

class MacroDetails:
    def __init__(
        self,
        master: tk.Widget,  # The master widget is required for creating StringVar instances.
        id: int = 0,
        name: tk.StringVar = '',
        beats: int = 0,
        fixed: bool = False,
        thumbnail: tk.StringVar = '',
        preset: bool = False,
        enabled: bool = False,
        macro_pattern_id: int = 0,
        phase: int = 0,
        initial_macro_id: int = 0,
        energy: int = 0,
        pattern: int = 0,
        existing: bool = False
    ) -> None:
        """
        Initializes a MacroDetails object.

        Parameters:
            master (tk.Widget): The Tkinter master (or parent) widget.
            id (int): Identifier for the macro.
            name (str): Name of the macro. Converted to tk.StringVar.
            beats (int): Number of beats.
            fixed (bool): Flag indicating if the macro is fixed.
            thumbnail (str): Thumbnail path or identifier. Converted to tk.StringVar.
            preset (bool): preset in rekordbox?
            enabled (bool): Whether the macro is enabled.
            macro_pattern_id (int): Identifier for the macro pattern.
            phase (int): Phase of the macro.
            initial_macro_id (int): The initial macro identifier.
            energy (int): Energy value associated with the macro.
            pattern (int): The pattern value.
            existing (bool): Indicates whether the macro already exists.
        """
        self.master = master
        self.id: int = id
        self.name: tk.StringVar = tk.StringVar(value=name)
        self.beats: int = beats
        self.fixed: bool = fixed
        self.thumbnail: tk.StringVar = tk.StringVar(value=thumbnail)
        self.preset: bool = preset
        self.enabled: bool = enabled
        self.macro_pattern_id: int = macro_pattern_id
        self.phase: int = phase
        self.initial_macro_id: int = initial_macro_id
        self.energy: int = energy
        self.pattern: int = pattern
        self.existing: bool = existing

    @classmethod
    def from_row(cls, master: tk.Widget, row: tuple) -> "MacroDetails":
        """
        Creates a MacroDetails instance from a tuple.

        Expects the tuple in the following order:
            (id, name, beats, fixed, thumbnail, preset, enabled,
             macro_pattern_id, phase, initial_macro_id, energy, pattern)
             
        The provided string values will be converted into tk.StringVar objects.
        """
        return cls(master, *row)

    def __repr__(self) -> str:
        """
        Returns a string representation of the MacroDetails object.
        The tk.StringVar values are displayed using their .get() method.
        """
        return (
            f"MacroDetails(id={self.id}, name={self.name.get()!r}, beats={self.beats}, fixed={self.fixed}, "
            f"thumbnail={self.thumbnail.get()!r}, preset={self.preset}, enabled={self.enabled}, "
            f"macro_pattern_id={self.macro_pattern_id}, phase={self.phase}, "
            f"initial_macro_id={self.initial_macro_id}, energy={self.energy}, pattern={self.pattern}, "
            f"existing={self.existing})"
        )