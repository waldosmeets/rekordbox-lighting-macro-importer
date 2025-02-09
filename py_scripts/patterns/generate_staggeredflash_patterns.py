import os

# Define banks, fixtures, and output folder
banks = ["cool", "warm", "vivid", "hot", "subtle", "natural", "club1", "club2"]
fixtures = range(1, 5)  # Fixture numbers: 1 to 4
output_folder = "staggered_flash_patterns"

# Define color palettes for each bank
color_palettes = {
    "cool": ["-16711681", "-16776961", "-1", "-65536"],  # Cyan, Blue, White, Ice Blue
    "warm": ["-65536", "-23296", "-256", "-32768"],      # Red, Amber, Yellow, Orange
    "vivid": ["-65281", "-16711681", "-8323328", "-256"], # Magenta, Cyan, Lime Green, Yellow
    "hot": ["-65536", "-32768", "-16711681", "-65281"],  # Red, Orange, Cyan, Magenta
    "subtle": ["-1", "-32768", "-23296", "-16711936"],   # White, Orange, Amber, Green
    "natural": ["-23296", "-16711936", "-8323328", "-65536"], # Amber, Green, Lime, Red
    "club1": ["-16776961", "-65281", "-256", "-16711681"], # Blue, Magenta, Yellow, Cyan
    "club2": ["-32768", "-65536", "-16711681", "-8323328"]  # Orange, Red, Cyan, Lime
}

# Function to generate XML content
def generate_xml_content(bank, fixture_number):
    # Get color palette and determine the fixture's pair
    palette = color_palettes[bank]
    color = palette[(fixture_number - 1) % len(palette)]

    # Pair logic for staggered flash
    pair_on = (fixture_number % 2 == 1)  # Odd fixtures are ON during one phase, even during the other

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<LightingEditModel ver="1.0">
  <!-- Fixture: Static PAR Light {fixture_number} | {bank.upper()} Bank -->
  <Colour>
    <ColourBlock xleft="0" colourleft="{color}" xright="64" colourright="{color}"/>
  </Colour>
  <Brightness>
    <PointBlock xleft="0" xright="64">
      <Point x="0" y="{'1.0' if pair_on else '0.3'}" type="1"/> <!-- Start Brightness -->
      <Point x="16" y="{'0.3' if pair_on else '1.0'}" type="2"/> <!-- Alternate -->
      <Point x="32" y="{'1.0' if pair_on else '0.3'}" type="2"/> <!-- Alternate -->
      <Point x="48" y="{'0.3' if pair_on else '1.0'}" type="2"/> <!-- Alternate -->
      <Point x="63.898" y="{'1.0' if pair_on else '0.3'}" type="2"/> <!-- Near End -->
      <Point x="63.998" y="{'1.0' if pair_on else '0.3'}" type="3"/> <!-- End Brightness -->
    </PointBlock>
  </Brightness>
</LightingEditModel>
"""

# Create the output folder
os.makedirs(output_folder, exist_ok=True)

# Generate XML files for each bank and fixture
for bank in banks:
    for fixture in fixtures:
        filename = f"staggered_flash-{bank}-fixture{fixture}.xml"
        filepath = os.path.join(output_folder, filename)
        with open(filepath, "w") as file:
            file.write(generate_xml_content(bank, fixture))

print(f"All files have been generated in the folder: {os.path.abspath(output_folder)}")
