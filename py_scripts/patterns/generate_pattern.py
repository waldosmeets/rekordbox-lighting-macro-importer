import os
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

def generate_lighting_edit_model(fixture_name, colours, brightness_pattern, movement_settings=None):
    model = Element("LightingEditModel", ver="1.0")

    # Add Pattern, Bank, Fixture, and Timestamp comments
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    comment = SubElement(model, "!--")
    comment.text = f" Pattern: {current_pattern_name}\n Bank: {current_bank_name}\n Fixture: {fixture_name}\n Generated: {timestamp} "

    # Colour Section
    colour_section = SubElement(model, "Colour")
    for xleft, colourleft, xright, colourright in colours:
        colour_block = SubElement(colour_section, "ColourBlock", xleft=str(xleft), colourleft=str(colourleft), 
                                  xright=str(xright), colourright=str(colourright))
        # Add descriptive comment for the transition
        transition_comment = SubElement(colour_section, "!--")
        transition_comment.text = f" Transition: {color_name(colourleft)} to {color_name(colourright)} "

    # Brightness Section
    brightness_section = SubElement(model, "Brightness")
    point_block = SubElement(brightness_section, "PointBlock", xleft="0", xright="64")
    for x, y, point_type in brightness_pattern:
        SubElement(point_block, "Point", x=str(x), y=str(y), type=str(point_type))

    # Movement Section (Optional for Moving Heads)
    if movement_settings:
        position_section = SubElement(model, "Position")
        for settings in movement_settings:
            SubElement(position_section, "MovementBlock", **settings)

    # Convert to pretty XML
    xml_string = tostring(model, 'utf-8')
    parsed = parseString(xml_string)
    return parsed.toprettyxml(indent="  ")

def color_name(rgb_value):
    color_map = {
        -65536: "Red",
        -16711936: "Green",
        -16776961: "Blue",
        -256: "Yellow",
        -16744320: "Teal",
        -8355712: "Grey",
        -16711680: "Orange",
        -14513374: "Pale Aqua",
        -10066076: "Light Steel Blue",
        -13761422: "Lavender Blue",
        -12132529: "Powder Blue",
        -8372224: "Light Moss Green",
        -10197846: "Sage Green",
        -7280651: "Pale Khaki",
        -3860763: "Peach Beige",
        -11250604: "Soft Blue Grey",
        -9782153: "Pastel Teal",
        -4751360: "Light Coral",
        -6973012: "Salmon Pink",
        -5636095: "Sunset Orange",
        -3145735: "Pale Gold",
    }
    return color_map.get(rgb_value, "Unknown")

def adjust_colours_for_looping_chase(base_colours, fixture_index, total_fixtures, cycles_per_bars_in_scene, reverse=False):
    adjusted_colours = []
    shift = fixture_index * 2  # Each fixture is delayed by 2 bars for a tighter chase
    bars_per_scene = 64 // cycles_per_bars_in_scene
    transition_duration = 64 // (len(base_colours) * cycles_per_bars_in_scene)  # Calculate duration dynamically

    starting_index = fixture_index % len(base_colours)  # Determine starting color for each fixture
    rotated_colours = base_colours[starting_index:] + base_colours[:starting_index]
    if reverse:
        rotated_colours = rotated_colours[::-1]  # Reverse the order for a reversed chase

    for cycle in range(cycles_per_bars_in_scene):  # Repeat the chase specified times within 64 bars
        for step, (xleft, colourleft, xright, colourright) in enumerate(rotated_colours):
            adjusted_xleft = (step * transition_duration + shift + cycle * bars_per_scene) % 64
            adjusted_xright = ((step + 1) * transition_duration + shift + cycle * bars_per_scene) % 64
            if adjusted_xleft < adjusted_xright:
                adjusted_colours.append((adjusted_xleft, colourleft, adjusted_xright, colourright))
            else:  # Wrap around
                adjusted_colours.append((adjusted_xleft, colourleft, 64, colourright))
                adjusted_colours.append((0, colourleft, adjusted_xright, colourright))

    # Ensure the first ColourBlock starts at xleft=0
    if adjusted_colours[0][0] > 0:
        adjusted_colours.insert(0, (0, adjusted_colours[0][1], adjusted_colours[0][0], adjusted_colours[0][1]))
    return adjusted_colours

def main(output_dir, cycles_per_bars_in_scene=4, pattern="Knight Rider Chase 2", bank="COOL", reverse=False):
    global current_pattern_name, current_bank_name
    current_pattern_name = pattern
    current_bank_name = bank

    os.makedirs(output_dir, exist_ok=True)

    bank_colors = {
        # Cool colors are soft and calming shades of blue and green
        "COOL": [
            (0, -14513374, 1, -10066076),  # Pale Aqua to Light Steel Blue
            (1, -10066076, 2, -13761422),  # Light Steel Blue to Lavender Blue
            (2, -13761422, 3, -12132529),  # Lavender Blue to Powder Blue
            (3, -12132529, 4, -14513374),  # Powder Blue to Pale Aqua
        ],
        # Natural colors are inspired by earthy and organic tones
        "NATURAL": [
            (0, -8372224, 1, -10197846),  # Light Moss Green to Sage Green
            (1, -10197846, 2, -7280651),  # Sage Green to Pale Khaki
            (2, -7280651, 3, -3860763),   # Pale Khaki to Peach Beige
            (3, -3860763, 4, -8372224),   # Peach Beige to Light Moss Green
        ],
        # Subtle colors are muted and neutral tones
        "SUBTLE": [
            (0, -11250604, 1, -9782153),  # Soft Blue Grey to Pastel Teal
            (1, -9782153, 2, -8355712),   # Pastel Teal to Grey
            (2, -8355712, 3, -14513374),  # Grey to Pale Aqua
            (3, -14513374, 4, -11250604), # Pale Aqua to Soft Blue Grey
        ],
        # Warm colors are vibrant and energizing shades of red and orange
        "WARM": [
            (0, -4751360, 1, -6973012),   # Light Coral to Salmon Pink
            (1, -6973012, 2, -5636095),   # Salmon Pink to Sunset Orange
            (2, -5636095, 3, -3145735),   # Sunset Orange to Pale Gold
            (3, -3145735, 4, -4751360),   # Pale Gold to Light Coral
        ],
        # Hot colors are intense and fiery shades
        "HOT": [
            (0, -65536, 1, -16711680),    # Red to Orange
            (1, -16711680, 2, -256),      # Orange to Yellow
            (2, -256, 3, -65536),         # Yellow to Red
            (3, -65536, 4, -16711680),    # Red to Orange
        ],
        # Vivid colors are bright and saturated shades
        "VIVID": [
            (0, -65536, 1, -16711936),    # Red to Green
            (1, -16711936, 2, -16776961), # Green to Blue
            (2, -16776961, 3, -256),      # Blue to Yellow
            (3, -256, 4, -65536),         # Yellow to Red
        ],
        # Club1 colors are dynamic and exciting shades
        "CLUB1": [
            (0, -16711936, 1, -16776961), # Green to Blue
            (1, -16776961, 2, -256),      # Blue to Yellow
            (2, -256, 3, -65536),         # Yellow to Red
            (3, -65536, 4, -16711936),    # Red to Green
        ],
        # Club2 colors are funky and fun shades
        "CLUB2": [
            (0, -16711680, 1, -256),      # Orange to Yellow
            (1, -256, 2, -16711680),      # Yellow to Orange
            (2, -16711680, 3, -65536),    # Orange to Red
            (3, -65536, 4, -16711680),    # Red to Orange
        ],
    }

    if pattern == "Knight Rider Chase 2":
        if bank not in bank_colors:
            raise ValueError(f"Bank '{bank}' is not recognized.")
        base_colours = bank_colors[bank]

        # Define brightness pattern
        brightness_pattern = [
            (0, 0.3, 1),
            (8, 0.5, 2),
            (16, 0.7, 2),
            (24, 0.5, 2),
            (32, 0.3, 2),
            (40, 0.5, 2),
            (48, 0.7, 2),
            (56, 0.5, 2),
            (63.898, 0.3, 2),
            (63.998, 0.3, 3),
        ]

        # Define movement settings for Moving Heads
        movinghead_movement = [
            {
                "xleft": "0", "xright": "8", "pattern": "Line", "width": "127", "height": "127",
                "offset_x": "50", "offset_y": "127", "round_angle": "0", "offset_angle": "0",
                "period_time": "20000", "frequency_x": "2", "frequency_y": "2", "phase_x": "0", "phase_y": "0",
                "type": "Loop", "direction": "Forward"
            },
        ]
    else:
        raise ValueError(f"Pattern '{pattern}' is not recognized.")

    # Fixtures to generate
    fixtures = [
        "MovingHead_1",
        "PAR_Light_1",
        "PAR_Light_2",
        "PAR_Light_3",
        "PAR_Light_4",
        "MovingHead_2",
    ]

    # Generate and save files
    total_fixtures = len(fixtures)
    for index, fixture_name in enumerate(fixtures):
        adjusted_colours = adjust_colours_for_looping_chase(base_colours, index, total_fixtures, cycles_per_bars_in_scene, reverse=reverse)
        movement = movinghead_movement if "MovingHead" in fixture_name else None
        xml_content = generate_lighting_edit_model(fixture_name, adjusted_colours, brightness_pattern, movement)
        output_file = os.path.join(output_dir, f"{pattern.replace(' ', '_').lower()}--{bank}--{fixture_name}.xml")
        with open(output_file, "w") as file:
            file.write(xml_content)

    print(f"Files successfully created in {output_dir} for pattern '{pattern}' and bank '{bank}'")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate lighting XML files for looping chase patterns.")
    parser.add_argument("--output_dir", type=str, default="looping_chase_output", help="Directory to save the generated files.")
    parser.add_argument("--cycles_per_bars_in_scene", type=int, default=4, help="Number of chase cycles per scene length.")
    parser.add_argument("--pattern", type=str, default="Knight Rider Chase 2", help="Pattern name for the generated files.")
    parser.add_argument("--bank", type=str, default="NATURAL", help="Bank name for the generated files.")
    parser.add_argument("--reverse", action="store_true", help="Reverse the chase direction.")
    args = parser.parse_args()

    main(output_dir=args.output_dir, cycles_per_bars_in_scene=args.cycles_per_bars_in_scene, pattern=args.pattern, bank=args.bank, reverse=args.reverse)
