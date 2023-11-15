import csv
import os
import time
import traceback

from classes.material import Material
from classes.mc_version import MinecraftVersion


def main():
    # Create the output folder
    generation_name = "testing"
    output_subfolder = os.path.join("outputs", f"{generation_name}_{time.strftime('%Y%m%d-%H%M%S')}")
    if not os.path.isdir(output_subfolder):
        os.makedirs(output_subfolder)

    materials_csv = "inputs/Tetranomotron - Test.csv"
    # replacements_csv = ""

    try:
        generate_materials(output_subfolder, materials_csv)
        # generate_replacements(output_subfolder, replacements_csv)
    except Exception as exc:
        print(traceback.format_exc())
        print(exc)

    if not os.listdir(output_subfolder):
        print("Nothing generated, removing folder.")
        os.rmdir(output_subfolder)

    pass


def generate_materials(output_folder_path, input_csv):
    print("\n\n\nGenerating materials initialized...")

    # Go through csv and make a list of all the materials
    materials = []
    with open(input_csv, 'r', encoding='utf-8-sig') as materials_csv:
        reader = csv.reader(materials_csv)
        headers = next(reader)
        for row in reader:
            materials.append(Material.create_from_csv(row))

    if not materials:
        print("No materials provided. Ending run")
        return

    print(f"Discovered {len(materials)} materials to generate.")

    # Sort the materials by version
    version_dictionary = {version: [] for version in MinecraftVersion}

    for version in version_dictionary:
        ver, materials_list = version, version_dictionary[version]
        for material in materials:
            if ver in material.versions:
                materials_list.append(material)

    # For each version:
    for version in version_dictionary:
        ver, mats = version, version_dictionary[version]
        if not mats:
            continue

        print(f"Generating {len(mats)} materials for version {ver.get_print_string}.")
        # Create a new version folder in the output
        ver_output_folder = os.path.join(output_folder_path, ver.get_print_string)
        os.makedirs(ver_output_folder)

        # Create a materials folder, a replacements folder, and a lang string
        materials_folder = os.path.join(ver_output_folder, "materials")
        replacements_folder = os.path.join(ver_output_folder, "replacements")
        os.makedirs(materials_folder)
        os.makedirs(replacements_folder)
        materials_by_modid_dict = {}

        # For each material, generate a json and add to the lang string
        for material in mats:
            print(f"     ...generating {material.material_key}")
            # Locate or create the material category folder
            category = material.category
            material_category_folder_path = os.path.join(materials_folder, category)
            if not os.path.isdir(material_category_folder_path):
                os.makedirs(material_category_folder_path)

            # Generate the JSON file
            material_json_path = os.path.join(material_category_folder_path, f"{material.material_key}.json")
            with open(material_json_path, 'w') as jsonfile:
                legacy = ver == MinecraftVersion.SIXTEEN
                jsonfile.write(str(material.get_json_block(legacy)))

            # Add the material to the list of materials for that modid
            if material.mod_id in materials_by_modid_dict:
                materials_by_modid_dict[material.mod_id].append(material)
            else:
                materials_by_modid_dict[material.mod_id] = [material]

        # Generate the lang document.
        # The mods are sorted alphabetically, and the materials within each mod are sorted alphabetically too.
        lang = "{\n"
        mod_ids = sorted(materials_by_modid_dict.keys())
        for mod in mod_ids:
            materials = sorted(materials_by_modid_dict[mod], key=lambda x: x.name)
            for material in materials:
                lang += material.get_lang_lines()
            lang += "\n\n"

        lang = lang.rstrip().removesuffix(",")
        lang += "\n}"
        print(f"     ...generating {ver.get_print_string} lang file")
        with open(os.path.join(ver_output_folder, "en_us.json"), 'w') as lang_file:
            lang_file.write(lang)


def generate_replacements(output_folder_path, input_csv):
    # Go through csv and make a list of all the replacements
    # for each replacement:
    # Decide what versions it's in
    # For each version it's in:
    # If that version doesn't have a folder in the output yet:
    # make one and add a materials folder, a replacements folder, and a lang doc
    # Find or generate a file with the replacement's mod id and tool type
    # Generate a version-appropriate replacement block and add it to that file
    pass


if __name__ == "__main__":
    main()
