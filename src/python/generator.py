import csv
import os
import time
import traceback
import json

from classes.material import Material
from classes.mc_version import MinecraftVersion
from classes.replacement import Replacement, get_json_file
from classes.socket import Socket, generate_sockets_json, generate_schematics_json


def main():
    # Create the output folder
    generation_name = "testing"
    output_subfolder = os.path.join("outputs", f"{generation_name}_{time.strftime('%Y%m%d-%H%M%S')}")
    if not os.path.isdir(output_subfolder):
        os.makedirs(output_subfolder)

    materials_csv = "inputs/Tetranomotron - Curated Materials.csv"
    replacements_csv = "inputs/Tetranomotron - Curated Replacements.csv"
    sockets_csv = "inputs/Tetranomotron - Curated Sockets.csv"

    try:
        generate_materials(output_subfolder, materials_csv)
        generate_replacements(output_subfolder, replacements_csv)
        generate_sockets(output_subfolder, sockets_csv)
        generate_lang(output_subfolder, materials_csv, sockets_csv)
    except Exception as exc:
        print(traceback.format_exc())
        print(exc)

    if not os.listdir(output_subfolder):
        print("Nothing generated, removing folder.")
        os.rmdir(output_subfolder)


def generate_materials(output_folder_path, input_csv):
    print("\n\n\nGenerating materials...")

    # Go through csv and make a list of all the materials
    materials = []
    with open(input_csv, 'r', encoding='utf-8-sig') as materials_csv:
        reader = csv.reader(materials_csv)
        headers = next(reader)
        for row in reader:
            # print(f"Reading CSV row about {row[0]}")
            materials.append(Material.create_from_csv(row))

    if not materials:
        print("No materials provided. Ending run.")
        return

    print(f"\nDiscovered {len(materials)} materials to generate. Generating:")

    for material in materials:
        print(f"        ...{material.material_key}")
        for version in material.versions:
            # Create version folder if not already
            ver_output_folder = os.path.join(output_folder_path, version.get_print_string())
            if not os.path.isdir(ver_output_folder):
                os.makedirs(ver_output_folder)

            # Create materials folder if not already
            mats_output_folder = os.path.join(ver_output_folder, "data/tetra/materials")
            if not os.path.isdir(mats_output_folder):
                os.makedirs(mats_output_folder)

            # Create material category folder if not already
            category_folder = os.path.join(mats_output_folder, material.category)
            if not os.path.isdir(category_folder):
                os.makedirs(category_folder)

            # Create material JSON
            mat_json_filepath = os.path.join(category_folder, f"{material.material_key}.json")
            with open(mat_json_filepath, 'w') as jsonfile:
                legacy = version == MinecraftVersion.SIXTEEN
                material_json = material.get_json(legacy)
                jsonfile.write(json.dumps(material_json, indent=4))


def generate_replacements(output_folder_path, input_csv):
    print("\n\n\nGenerating replacements...")

    replacements = []
    with open(input_csv, 'r', encoding='utf-8-sig') as replacements_csv:
        reader = csv.reader(replacements_csv)
        headers = next(reader)
        for row in reader:
            # print(f"Reading CSV row about {row[0]}")
            replacements.append(Replacement.create_from_csv(row))

    if not replacements:
        print("No replacements provided. Ending run.")
        return

    print(f"\nDiscovered {len(replacements)} replacements to generate. Generating:")

    # Sort replacements by version
    version_dictionary = {version: [] for version in MinecraftVersion}
    for replacement in replacements:
        for version in replacement.versions:
            version_dictionary[version].append(replacement)

    # For each version:
    for version in MinecraftVersion:
        # Ignore if no replacements for that version
        if not version_dictionary[version]:
            continue
        print(version.get_print_string())

        # Create version folder if not already
        ver_output_folder = os.path.join(output_folder_path, version.get_print_string())
        if not os.path.isdir(ver_output_folder):
            os.makedirs(ver_output_folder)

        # Create replacements folder if not already
        reps_output_folder = os.path.join(ver_output_folder, "data/tetra/replacements")
        if not os.path.isdir(reps_output_folder):
            os.makedirs(reps_output_folder)

        # Sort replacements by material
        replacements_dict = {}
        for replacement in version_dictionary[version]:
            if replacement.material_key in replacements_dict.keys():
                replacements_dict[replacement.material_key].append(replacement)
            else:
                replacements_dict[replacement.material_key] = [replacement]
        print("Sorted replacements by material")

        # For each material, create a file and fill it
        for material in replacements_dict.keys():
            print(f"        ...{material}")
            filepath = os.path.join(reps_output_folder, f"{material}_replacements.json")
            with open(filepath, 'w') as jsonfile:
                legacy = version == MinecraftVersion.SIXTEEN
                replacements_json = get_json_file(replacements_dict[material], legacy)
                jsonfile.write(json.dumps(replacements_json, indent=4))


def generate_sockets(output_folder_path, input_csv):
    print("\n\n\nGenerating sockets...")

    sockets = []
    with open(input_csv, 'r', encoding='utf-8-sig') as sockets_csv:
        reader = csv.reader(sockets_csv)
        headers = next(reader)
        for row in reader:
            # print(f"Reading CSV row about {row[0]}")
            sockets.append(Socket.create_from_csv(row))

    if not sockets:
        print("No sockets provided. Ending run.")
        return

    print(f"\nDiscovered {len(sockets)} sockets to generate. Generating:")

    # Sort sockets by version
    version_dictionary = {version: [] for version in MinecraftVersion}
    for socket in sockets:
        for version in socket.versions:
            version_dictionary[version].append(socket)

    # For each version:
    for version in MinecraftVersion:
        # Ignore if no sockets for that version
        if not version_dictionary[version]:
            continue

        print(version.get_print_string())

        # Create version folder if not already
        ver_output_folder = os.path.join(output_folder_path, version.get_print_string())
        if not os.path.isdir(ver_output_folder):
            os.makedirs(ver_output_folder)

        # Create modules and schematics folders if not already
        module_output_folder = os.path.join(ver_output_folder, "data/tetra/modules")
        if not os.path.isdir(module_output_folder):
            os.makedirs(module_output_folder)
        schematics_output_folder = os.path.join(ver_output_folder, "data/tetra/schematics")
        if not os.path.isdir(schematics_output_folder):
            os.makedirs(schematics_output_folder)

        # Sort sockets by modular type
        modular_type_dict = {}
        for socket in version_dictionary[version]:
            for modular_type in socket.modular_types:
                if modular_type in modular_type_dict.keys():
                    modular_type_dict[modular_type].append(socket)
                else:
                    modular_type_dict[modular_type] = [socket]
        print("Sorted sockets by modular type")

        # For each modular type
        for modular_type in modular_type_dict.keys():
            legacy = version == MinecraftVersion.SIXTEEN
            print(f"        ...{modular_type.value}")

            # Create a modules folder and a socket.json file in it
            folder = os.path.join(module_output_folder, modular_type.value)
            os.makedirs(folder)
            filepath = os.path.join(folder, "socket.json")
            with open(filepath, 'w') as jsonfile:
                replacements_json = generate_sockets_json(modular_type_dict[modular_type], legacy, modular_type)
                jsonfile.write(json.dumps(replacements_json, indent=4))

            # Create a schematics folder and a socket.json file in it
            schematics_folder = os.path.join(schematics_output_folder, modular_type.value)
            os.makedirs(schematics_folder)
            filepath = os.path.join(schematics_folder, "socket.json")
            with open(filepath, 'w') as jsonfile:
                schematics_json = generate_schematics_json(modular_type_dict[modular_type], legacy, modular_type)
                jsonfile.write(json.dumps(schematics_json, indent=4))


def generate_lang(output_folder_path, materials_csv, sockets_csv):
    print("\n\nGenerating lang files\n")

    # Go through csv and make a list of all the materials
    materials = []
    with open(materials_csv, 'r', encoding='utf-8-sig') as materials_csv_file:
        reader = csv.reader(materials_csv_file)
        headers = next(reader)
        for row in reader:
            # print(f"Reading CSV row about {row[0]}")
            materials.append(Material.create_from_csv(row))

    sockets = []
    with open(sockets_csv, 'r', encoding='utf-8-sig') as sockets_csv_file:
        reader = csv.reader(sockets_csv_file)
        headers = next(reader)
        for row in reader:
            # print(f"Reading CSV row about {row[0]}")
            sockets.append(Socket.create_from_csv(row))

    for version in MinecraftVersion:
        print(f"Working on lang file for version {version.get_print_string()}")

        materials_in_this_version = []
        sockets_in_this_version = []

        for material in materials:
            if version in material.versions:
                materials_in_this_version.append(material)
        for socket in sockets:
            if version in socket.versions:
                sockets_in_this_version.append(socket)

        print(f"Found {len(materials_in_this_version)} materials and {len(sockets_in_this_version)} sockets for version {version.get_print_string()}\n")

        if not materials_in_this_version and not sockets_in_this_version:
            continue

        version_folder = os.path.join(output_folder_path, version.get_print_string())
        lang_folder = os.path.join(version_folder, "assets/tetranomicon/lang")
        os.makedirs(lang_folder)

        materials_by_mod_id = {}
        sockets_by_mod_id = {}

        for material in materials_in_this_version:
            if material.mod_id in materials_by_mod_id.keys():
                materials_by_mod_id[material.mod_id].append(material)
            else:
                materials_by_mod_id[material.mod_id] = [material]
        for socket in sockets_in_this_version:
            if socket.mod_id in sockets_by_mod_id.keys():
                sockets_by_mod_id[socket.mod_id].append(socket)
            else:
                sockets_by_mod_id[socket.mod_id] = [socket]

        all_mod_ids = list(set(list(materials_by_mod_id.keys()) + list(sockets_by_mod_id.keys())))
        all_mod_ids.sort()

        lang_rows = []
        last_mod = all_mod_ids[-1]
        for mod_id in all_mod_ids:
            mod_materials = materials_by_mod_id[mod_id] if mod_id in materials_by_mod_id.keys() else []
            mod_sockets = sockets_by_mod_id[mod_id] if mod_id in sockets_by_mod_id.keys() else []

            mod_materials.sort(key=lambda x: x.material_key)
            mod_sockets.sort(key=lambda x: x.name)

            for material in mod_materials:
                lang_rows.extend(material.get_lang_lines())

            if mod_materials and mod_sockets:
                lang_rows.append("")

            for socket in mod_sockets:
                lang_rows.extend(socket.get_lang_lines())

            if mod_id != last_mod:
                lang_rows.append("")
                lang_rows.append("")

        lang_file_content = f"{{\n    "
        for row in lang_rows:
            lang_file_content += row
            if len(row) > 0:
                lang_file_content += ","
            lang_file_content += "\n    "
        lang_file_content = lang_file_content.rstrip().removesuffix(",")
        lang_file_content += f"\n}}"

        filepath = os.path.join(lang_folder, "en_us.json")
        with open(filepath, 'w', encoding="utf-8-sig") as jsonfile:
            jsonfile.write(lang_file_content)


if __name__ == "__main__":
    main()
