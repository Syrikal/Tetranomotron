import json
import os
from collections import OrderedDict

tool_improvements = ["levitator_tool", "tenacity_tool", "ambrosia_seeker_tool", "harvester"]
weapon_improvements = ["levitator_weapon", "tenacity_weapon", "ambrosia_seeker_weapon"]

tool_modules = ["double/adze", "double/basic_axe", "double/basic_hammer", "double/basic_pickaxe",
                "double/claw", "double/hoe", "double/sickle", "single/basic_shovel", "sword/machete"]
weapon_modules = ["single/spearhead", "single/trident", "sword/basic_blade", "sword/heavy_blade", "sword/short_blade", "sword/throwing_knife"]


for module in tool_modules:
    outputfolder = "modules"
    if not os.path.isdir(outputfolder):
        os.makedirs(outputfolder)
    item_type, module_name = module.split("/")
    file_name = module_name + ".json"
    item_type_folder = os.path.join(outputfolder, item_type)
    if not os.path.isdir(item_type_folder):
        os.makedirs(item_type_folder)

    json_output = OrderedDict()
    json_output["replace"] = False
    json_output["improvements"] = ["tetra:aetheric_tetranomicon/shared_tool/"]

    filepath = os.path.join(item_type_folder, file_name)

    with open(filepath, 'w') as jsonfile:
        jsonfile.write(json.dumps(json_output, indent=4))

for module in weapon_modules:
    outputfolder = "modules"
    if not os.path.isdir(outputfolder):
        os.makedirs(outputfolder)
    item_type, module_name = module.split("/")
    file_name = module_name + ".json"
    item_type_folder = os.path.join(outputfolder, item_type)
    if not os.path.isdir(item_type_folder):
        os.makedirs(item_type_folder)

    json_output = OrderedDict()
    json_output["replace"] = False
    json_output["improvements"] = ["tetra:aetheric_tetranomicon/shared_weapon/"]

    filepath = os.path.join(item_type_folder, file_name)

    with open(filepath, 'w') as jsonfile:
        jsonfile.write(json.dumps(json_output, indent=4))
