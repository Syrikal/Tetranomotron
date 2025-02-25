import csv
import os
import time
import traceback
import json
import requests
import sys

from classes.material import Material
from classes.mc_version import MinecraftVersion
from classes.replacement import Replacement, get_json_file
from classes.socket import Socket, generate_sockets_json, generate_schematics_json, ModularType


def main():
    # Create the output folder
    generation_name = "tetranomicon"
    # generation_name = "aetheric_tetranomicon"
    # generation_name = "undergarden"
    # generation_name = "toolbooster"
    # generation_name = "upgraded netherite"

    output_subfolder = os.path.join("outputs", f"{generation_name}_{time.strftime('%Y%m%d-%H%M%S')}")
    if not os.path.isdir(output_subfolder):
        os.makedirs(output_subfolder)

    if generation_name == "tetranomicon":

        materials_url = 'https://docs.google.com/spreadsheets/d/1FSoWhpdRc0QVefqWkJd8Z9s25QUKqp1XGZIi5TyljJ4/export?format=csv'
        sockets_url = 'https://docs.google.com/spreadsheets/d/1pLnYjArFpUox5dQ2YYy3_ZR8pIaD679-uYTnAGb9qpo/export?format=csv'
        replacements_url = 'https://docs.google.com/spreadsheets/d/1bLq3efx2RXSsxelvIUegBZkoDdE6FfSFrJ0sh9uzcPA/export?format=csv'

        materials_csv, sockets_csv, replacements_csv = download_csvs("Tetranomicon", materials_url, sockets_url, replacements_url)

    elif generation_name == "aetheric_tetranomicon":

        materials_url = 'https://docs.google.com/spreadsheets/d/1kbinIqoOmmgaEUgu2eFNQymHJrz_zHi-58KQJeBTpig/export?format=csv'
        sockets_url = 'https://docs.google.com/spreadsheets/d/1t_ckuFGq22A5SEFn5NoHFMGdcyIszNa9_1FEPS_eL_s/export?format=csv'
        replacements_url = 'https://docs.google.com/spreadsheets/d/1iKyaWeBO4Ij5fnXv2dkVF-T504HKEt3MhGgOF_JQgIU/export?format=csv'

        materials_csv, sockets_csv, replacements_csv = download_csvs("Aetheric Tetranomicon", materials_url, sockets_url, replacements_url)

    elif generation_name == "undergarden":

        materials_url = 'https://docs.google.com/spreadsheets/d/1BcpAVNItwu8o4Hl0RrAdbcDwyS5gs1mGRZEHLuG3a_E/export?format=csv'
        sockets_url = 'https://docs.google.com/spreadsheets/d/1g17Utd3usm_-NFbARCdBo2QZpuo0W8ARf6Xd-XJwS4o/export?format=csv'
        replacements_url = 'https://docs.google.com/spreadsheets/d/1qgya_I_zieDcPT6yihrAPOdABU8IkhKe0ZUvlRVtKZY/export?format=csv'

        materials_csv, sockets_csv, replacements_csv = download_csvs("Undergarden Tetranomicon", materials_url, sockets_url, replacements_url)

    elif generation_name == "toolbooster":

        sockets_url = 'https://docs.google.com/spreadsheets/d/1WJT3KBI2gmV4AzD7BoXMAHh_RkGIu3QFzvbOn9Kd0Z4/export?format=csv'

        materials_csv, sockets_csv, replacements_csv = download_csvs("Toolbooster", "", sockets_url, "")

    elif generation_name == "upgraded netherite":

        replacements_url = 'https://docs.google.com/spreadsheets/d/15WCR6lfL6rS1ARb2vrthio0ujUKxbrFpr7hIZIwd_OI/export?format=csv'

        materials_csv, sockets_csv, replacements_csv = download_csvs("Upgraded Netherite", "", "", replacements_url)

    else:
        materials_csv = ""
        sockets_csv = ""
        replacements_csv = ""

    try:
        materials, replacements, sockets = "", "", ""
        if materials_csv:
            materials = generate_materials(output_subfolder, materials_csv)
        if replacements_csv:
            generate_replacements(output_subfolder, replacements_csv)
        if sockets_csv:
            sockets = generate_sockets(output_subfolder, sockets_csv)
        if materials and sockets:
            generate_lang(output_subfolder, materials, sockets)
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
        important_columns = [i for i in range(len(headers))]
        for header in headers:
            if header.startswith("ignore"):
                important_columns.remove(headers.index(header))

        for row in reader:
            row = [row[i] for i in important_columns]
            # Add material(s) from row to materials list
            # Ignore vanilla and undergarden materials
            row_materials = Material.create_from_csv(row)
            materials.extend(row_materials)

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
                material_json = material.get_json(version)
                jsonfile.write(json.dumps(material_json, indent=4))

    return materials


def generate_replacements(output_folder_path, input_csv):
    print("\n\n\nGenerating replacements...")

    replacements = []
    with open(input_csv, 'r', encoding='utf-8-sig') as replacements_csv:
        reader = csv.reader(replacements_csv)
        headers = next(reader)
        important_columns = [i for i in range(len(headers))]
        for header in headers:
            if header.startswith("ignore"):
                important_columns.remove(headers.index(header))

        for row in reader:
            row = [row[i] for i in important_columns]
            # print(f"Reading CSV row about {row[0]}")
            replacements.extend(Replacement.create_from_csv(row))

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
            if replacement.toolset in replacements_dict.keys():
                replacements_dict[replacement.toolset].append(replacement)
            else:
                replacements_dict[replacement.toolset] = [replacement]
        print("Sorted replacements by material")

        # For each material, create a file and fill it
        for material in replacements_dict.keys():
            print(f"        ...{material}")
            filepath = os.path.join(reps_output_folder, f"{material}_replacements.json")
            with open(filepath, 'w') as jsonfile:
                legacy = version == MinecraftVersion.SIXTEEN
                replacements_dict[material].sort(key=lambda rep: rep.replacement_type.value)
                replacements_json = get_json_file(replacements_dict[material], legacy)
                jsonfile.write(json.dumps(replacements_json, indent=4))


def generate_sockets(output_folder_path, input_csv):
    print("\n\n\nGenerating sockets...")

    sockets = []
    with open(input_csv, 'r', encoding='utf-8-sig') as sockets_csv:
        reader = csv.reader(sockets_csv)
        headers = next(reader)
        important_columns = [i for i in range(len(headers))]
        for header in headers:
            if header.startswith("ignore"):
                important_columns.remove(headers.index(header))
        for row in reader:
            row = [row[i] for i in important_columns]
            # print(f"Reading CSV row about {row[0]}")
            sockets.extend(Socket.create_from_csv(row))

    if not sockets:
        print("No sockets provided. Ending run.")
        return

    print(f"\nDiscovered {len(sockets)} sockets to generate. Generating:")

    # Sort sockets by version
    version_dictionary = {version: [] for version in MinecraftVersion}
    for socket in sockets:
        for version in socket.versions:
            version_dictionary[version].append(socket)

    # For old versions:
    for version in [MinecraftVersion.SIXTEEN, MinecraftVersion.EIGHTEEN]:
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
                modular_type_dict[modular_type].sort(key=lambda soc: soc.mod_id + socket.variant_key)
                replacements_json = generate_sockets_json(modular_type_dict[modular_type], version, modular_type)
                jsonfile.write(json.dumps(replacements_json, indent=4))

            # Create a schematics folder and a socket.json file in it
            schematics_folder = os.path.join(schematics_output_folder, modular_type.value)
            os.makedirs(schematics_folder)
            filepath = os.path.join(schematics_folder, "socket.json")
            with open(filepath, 'w') as jsonfile:
                schematics_json = generate_schematics_json(modular_type_dict[modular_type], legacy, modular_type)
                jsonfile.write(json.dumps(schematics_json, indent=4))

    # For new versions:
    for version in [MinecraftVersion.NINETEEN, MinecraftVersion.TWENTY]:
        # Ignore if no sockets for that version
        if not version_dictionary[version]:
            continue

        print(version.get_print_string())

        # Create version folder if not already
        ver_output_folder = os.path.join(output_folder_path, version.get_print_string())
        if not os.path.isdir(ver_output_folder):
            os.makedirs(ver_output_folder)

        # Create materials/sockets folder if not already
        sockets_folder = os.path.join(ver_output_folder, "data/tetra/materials/socket")
        if not os.path.isdir(sockets_folder):
            os.makedirs(sockets_folder)

        # Add each socket to the folder
        for socket in version_dictionary[version]:
            socket_json_filepath = os.path.join(sockets_folder, f"socket_{socket.variant_key}.json")
            with open(socket_json_filepath, 'w') as jsonfile:
                socket_json = socket.get_socket_json(version, ModularType.DOUBLE)
                jsonfile.write(json.dumps(socket_json, indent=4))

    return sockets


def generate_lang(output_folder_path, materials, sockets):
    print("\n\nGenerating lang files\n")

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
                post_119 = version.value > 18
                lang_rows.extend(socket.get_socket_lang_lines(post_119))

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


def download_csvs(name, mats_url, sockets_url, replacements_url):
    outputs = []
    if mats_url:
        materials_response = requests.get(mats_url)

        if materials_response.status_code == 200:
            filepath = os.path.join("inputs", f"{name} - Materials.csv")
            with open(filepath, 'wb') as f:
                f.write(materials_response.content)
                print('CSV file saved to: {}'.format(filepath))
            outputs.append(filepath)
        else:
            print(f'Error downloading Google Sheet: {materials_response.status_code}')
            sys.exit(1)
    else:
        outputs.append("")

    if sockets_url:
        sockets_response = requests.get(sockets_url)
        if sockets_response.status_code == 200:
            filepath = os.path.join("inputs", f"{name} - Sockets.csv")
            with open(filepath, 'wb') as f:
                f.write(sockets_response.content)
                print('CSV file saved to: {}'.format(filepath))
            outputs.append(filepath)
        else:
            print(f'Error downloading Google Sheet: {sockets_response.status_code}')
            sys.exit(1)
    else:
        outputs.append("")

    if replacements_url:
        replacements_response = requests.get(replacements_url)
        if replacements_response.status_code == 200:
            filepath = os.path.join("inputs", f"{name} - Replacements.csv")
            with open(filepath, 'wb') as f:
                f.write(replacements_response.content)
                print('CSV file saved to: {}'.format(filepath))
            outputs.append(filepath)
        else:
            print(f'Error downloading Google Sheet: {replacements_response.status_code}')
            sys.exit(1)
    else:
        outputs.append("")

    return outputs


if __name__ == "__main__":
    main()
