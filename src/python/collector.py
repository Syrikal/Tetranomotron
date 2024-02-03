import os
import csv

from classes.material import Material
from classes.mc_version import MinecraftVersion
from classes.replacement import gen_replacements_from_json
from classes.socket import ModularType, gen_sockets_from_json


# This file collects existing Tetranomicon content and stores it as CSVs.
def materials():
    print("Gathering 1.16 materials...")
    mats16 = "../resources/Tetranomicon 1.16/data/tetra/materials"
    lang = "../resources/Tetranomicon 1.16/assets/tetranomicon/lang/en_us.json"

    materials16 = []

    for root, dirs, files in os.walk(mats16):
        for file in files:
            filepath = os.path.join(root, file)
            material = Material.create_from_json(filepath, lang, MinecraftVersion.SIXTEEN)
            materials16.append(material)

    print("Gathering 1.18 materials...")
    mats18 = "../resources/Tetranomicon 1.18/data/tetra/materials"
    lang = "../resources/Tetranomicon 1.18/assets/tetranomicon/lang/en_us.json"

    materials18 = []

    for root, dirs, files in os.walk(mats18):
        for file in files:
            filepath = os.path.join(root, file)
            material = Material.create_from_json(filepath, lang, MinecraftVersion.EIGHTEEN)
            materials18.append(material)

    print("Gathering 1.19 materials...")
    mats19 = "../resources/Tetranomicon 1.19/data/tetra/materials"
    lang = "../resources/Tetranomicon 1.19/assets/tetranomicon/lang/en_us.json"

    materials19 = []

    for root, dirs, files in os.walk(mats19):
        for file in files:
            filepath = os.path.join(root, file)
            material = Material.create_from_json(filepath, lang, MinecraftVersion.NINETEEN)
            materials19.append(material)

    all_materials = materials16 + materials18 + materials19
    merged_materials_list = []
    print(f"There are {len(all_materials)} materials to analyze.")

    # For every material, check if it matches something in the merged list.
    # If it does, assimilate it to that one.
    # If it doesn't, add it to the list.
    for material in all_materials:
        version = material.versions[0].value
        versionstring = f"1.{version}: "
        if len(merged_materials_list) == 0:
            print(f"{versionstring}Materials list is empty, adding {material.name} to list")
            merged_materials_list.append(material)
            continue

        found_match = False
        for existing_material in merged_materials_list:
            if material.matches(existing_material):
                existing_material.assimilate_in_place(material)
                found_match = True
                # print(f"{versionstring}{material.name} matches existing material, assimilating")
                break
        if not found_match:
            # print(f"{versionstring}No match found for {material.name}, adding to list")
            merged_materials_list.append(material)

    print(f"Found {len(merged_materials_list)} final materials")

    with open("outputs/csvs/materials.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        leadingrow = ["Name", "Adjective", "Mod ID", "Versions", "Category", "Prim", "Sec", "Tert",
                      "Dur", "iCost", "iGain", "magic", "tlevel", "teff", "tint", "textures", "item",
                      "effects", "improvements", "reqTools"]
        writer.writerow(leadingrow)
        writer.writerows([mat.get_csv_row() for mat in merged_materials_list])


def sockets():
    # 1.16
    print("Gathering 1.16 sockets...")
    modules16 = "../resources/Tetranomicon 1.16/data/tetra/modules"
    lang = "../resources/Tetranomicon 1.16/assets/tetranomicon/lang/en_us.json"
    schematics16 = "../resources/Tetranomicon 1.16/data/tetra/schematics"

    sockets16 = []

    for root, dirs, files in os.walk(modules16):
        for file in files:
            if file == "socket.json":
                filepath = os.path.join(root, file)
                # print(f"Analyzing sockets from file {filepath}")
                item_type = ModularType(os.path.split(root)[1])
                schematics_folder = os.path.join(schematics16, item_type.value)
                schematics_file = os.path.join(schematics_folder, "socket.json")
                sockets16.extend(gen_sockets_from_json(filepath, lang, schematics_file, MinecraftVersion.SIXTEEN))

    # 1.18
    print("Gathering 1.18 sockets...")
    modules18 = "../resources/Tetranomicon 1.18/data/tetra/modules"
    lang = "../resources/Tetranomicon 1.18/assets/tetranomicon/lang/en_us.json"
    schematics18 = "../resources/Tetranomicon 1.18/data/tetra/schematics"

    sockets18 = []

    for root, dirs, files in os.walk(modules18):
        for file in files:
            if file == "socket.json":
                filepath = os.path.join(root, file)
                # print(f"Analyzing sockets from file {filepath}")
                item_type = ModularType(os.path.split(root)[1])
                schematics_folder = os.path.join(schematics18, item_type.value)
                schematics_file = os.path.join(schematics_folder, "socket.json")
                sockets18.extend(gen_sockets_from_json(filepath, lang, schematics_file, MinecraftVersion.EIGHTEEN))

    # 1.19
    print("Gathering 1.19 sockets...")
    modules19 = "../resources/Tetranomicon 1.19/data/tetra/modules"
    lang = "../resources/Tetranomicon 1.19/assets/tetranomicon/lang/en_us.json"
    schematics19 = "../resources/Tetranomicon 1.19/data/tetra/schematics"

    sockets19 = []

    for root, dirs, files in os.walk(modules19):
        for file in files:
            if file == "socket.json":
                filepath = os.path.join(root, file)
                # print(f"Analyzing sockets from file {filepath}")
                item_type = ModularType(os.path.split(root)[1])
                schematics_folder = os.path.join(schematics19, item_type.value)
                schematics_file = os.path.join(schematics_folder, "socket.json")
                sockets19.extend(gen_sockets_from_json(filepath, lang, schematics_file, MinecraftVersion.NINETEEN))

    all_sockets = sockets16 + sockets18 + sockets19

    merged_sockets = []

    for soc in all_sockets:
        if not merged_sockets:
            merged_sockets.append(soc)
            continue

        new = True
        for existing_soc in merged_sockets:
            if soc.matches(existing_soc):
                existing_soc.assimilate(soc)
                new = False
                break

        if new:
            merged_sockets.append(soc)

    print(f"Found {len(merged_sockets)} final sockets")

    # Creating CSV
    with open("outputs/csvs/sockets.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        leadingrow = ["Name", "Mod ID", "Lang Name", "Versions", "Item Types", "Durability", "Durability Mod",
                      "Integrity", "Tint", "Attributes", "Effects", "Tool Boosts", "Item", "XP Cost"]
        writer.writerow(leadingrow)
        writer.writerows([sock.get_csv_row() for sock in merged_sockets])


def replacements():
    # 1.16
    print("Gathering 1.16 replacements...")
    folder = "../resources/Tetranomicon 1.16/data/tetra/replacements"

    replacements_list = []

    for file in os.listdir(folder):
        filepath = os.path.join(folder, file)
        replacements_list.extend(gen_replacements_from_json(filepath, MinecraftVersion.SIXTEEN))

    # 1.18
    print("Gathering 1.18 replacements...")
    folder = "../resources/Tetranomicon 1.18/data/tetra/replacements"

    for file in os.listdir(folder):
        filepath = os.path.join(folder, file)
        replacements_list.extend(gen_replacements_from_json(filepath, MinecraftVersion.EIGHTEEN))

    # 1.19
    print("Gathering 1.19 replacements...")
    folder = "../resources/Tetranomicon 1.19/data/tetra/replacements"

    for file in os.listdir(folder):
        filepath = os.path.join(folder, file)
        replacements_list.extend(gen_replacements_from_json(filepath, MinecraftVersion.NINETEEN))

    merged_replacements = []

    for rep in replacements_list:
        if not merged_replacements:
            merged_replacements.append(rep)
            continue

        new = True
        for existing_rep in merged_replacements:
            if rep.matches(existing_rep):
                existing_rep.assimilate(rep)
                new = False
                break

        if new:
            merged_replacements.append(rep)

    print(f"Found {len(merged_replacements)} final replacements")

    with open("outputs/csvs/replacements.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        leadingrow = ["Item ID", "Mod ID", "Replacement Type", "Versions", "Material", "Improvements"]
        writer.writerow(leadingrow)
        writer.writerows([rep.get_csv_row() for rep in merged_replacements])


# materials()
# sockets()
replacements()
