from collections import OrderedDict
from enum import Enum

from .mc_version import MinecraftVersion, get_versions_csv_string
import json
from jsondiff import diff

from .socket import ModularType
from src.python.classes import util


def main():
    test()
    pass


class Replacement:
    # Replacement_Type is axe, double_axe, hoe, knife, pick, shovel, or sword   TO ADD: Bow, Crossbow, Spear
    # Improvements is a list of lists of length 3: module, improvement, level
    def __init__(self, itemid, modid, replacement_type, versions, toolset, material, handle_material, improvements):
        self.item_id = itemid
        self.mod_id = modid
        self.replacement_type = ReplacementType(replacement_type)
        self.versions = [MinecraftVersion.get_version(int(ver)) for ver in versions]
        self.toolset = toolset
        self.material_key = material.lower()
        self.handle_material_key = handle_material.lower()
        self.improvements = improvements
        # print(f"Generating Replacement with improvements {improvements}")

    @classmethod
    # Creates Replacement from a CSV row
    def create_from_csv(cls, csv_row):
        # print("Creating a replacement from a CSV row")
        if len(csv_row) != 8:
            raise ValueError(f"Failed attempt to create a replacement from csv row because row was wrong size: '{csv_row}'")

        itemids_raw, mod_id, replacement_type, versions_raw, toolsets_raw, material_names_raw, handle_material_names_raw, improvements = csv_row

        item_ids = itemids_raw.split(", ")
        version_lists = versions_raw.split("; ")
        toolsets = toolsets_raw.split(", ")
        material_names = material_names_raw.split(", ")
        handle_material_names = handle_material_names_raw.split(", ")

        lengths = [len(item_ids), len(version_lists), len(toolsets), len(material_names), len(handle_material_names)]
        number_of_replacements = max(lengths)

        outputs = []
        for i in range(number_of_replacements):
            itemid = item_ids[i] if len(item_ids) > 1 else item_ids[0]
            vers = version_lists[i] if len(version_lists) > 1 else version_lists[0]
            toolset = toolsets[i] if len(toolsets) > 1 else toolsets[0]
            material_name = material_names[i] if len(material_names) > 1 else material_names[0]
            handle_material_name = handle_material_names[i] if len(handle_material_names) > 1 else handle_material_names[0]

            if not vers:
                print("Error in versions for " + itemid)

            versions = vers.split(", ")
            individual_improvements = improvements.split(", ")
            improvements_new = [x.split(" ") for x in individual_improvements]
            if not improvements:
                improvements_new = []
            rep = Replacement(itemid, mod_id, replacement_type, versions, toolset, material_name, handle_material_name, improvements_new)

            outputs.append(rep)

        return outputs

    @classmethod
    # Creates a Replacement from a JSON object (*not* a file!)
    def create_from_json(cls, json_object, version):
        # print("Creating a replacement from a JSON")

        if version == MinecraftVersion.SIXTEEN:
            mod_and_item = json_object["predicate"]["item"]
        else:
            mod_and_item = json_object["predicate"]["items"][0]
        mod_id, item_id = mod_and_item.split(":")
        versions = [version.value]

        modules_dict = json_object["modules"]

        modular_item_type = None
        if "double/head_left" in modules_dict.keys():
            modular_item_type = "double"
        elif "single/head" in modules_dict.keys():
            modular_item_type = "single"
        elif "sword/blade" in modules_dict.keys():
            modular_item_type = "sword"

        match modular_item_type:
            case "double":
                module, material = modules_dict["double/head_left"][1].split("/")
                handle_material = modules_dict["double/handle"][1].split("/")[1]
            case "single":
                module, material = modules_dict["single/head"][1].split("/")
                handle_material = modules_dict["single/handle"][1].split("/")[1]
            case "sword":
                module, material = modules_dict["sword/blade"][1].split("/")
                handle_material = modules_dict["sword/hilt"][1].split("/")[1]
            case _:
                raise ValueError("Replacement not recognized!")

        if handle_material == "stick":
            handle_material = ""

        replacement_type = None
        match module:
            case "basic_axe":
                second_module = modules_dict["double/head_right"][1].split("/")[0]
                match second_module:
                    case "butt":
                        replacement_type = ReplacementType.AXE
                    case "basic_axe":
                        replacement_type = ReplacementType.DOUBLE_AXE
            case "hoe":
                replacement_type = ReplacementType.HOE
            case "short_blade":
                replacement_type = ReplacementType.KNIFE
            case "basic_pickaxe":
                replacement_type = ReplacementType.PICK
            case "basic_shovel":
                replacement_type = ReplacementType.SHOVEL
            case "basic_blade":
                replacement_type = ReplacementType.SWORD
            case "heavy_blade":
                replacement_type = ReplacementType.GREATSWORD
            case _:
                raise ValueError(f"Can't parse module {module}")

        # Double-check we have the right replacement type
        match modular_item_type:
            case "double":
                second_module_name = modules_dict["double/head_right"][1].split("/")[0]
            case "single":
                second_module_name = modules_dict["single/handle"][1].split("/")[0]
            case "sword":
                second_module_name = modules_dict["sword/hilt"][1].split("/")[0]
            case _:
                second_module_name = "ERROR NO MODULAR ITEM TYPE"

        if second_module_name != replacement_type.second_module():
            raise ValueError(f"Encountered unexpected second module {second_module_name} when creating {replacement_type.name} replacement from json")

        # print(f"Found replacement type {replacement_type}.")

        improvements = []
        if "improvements" in json_object.keys():
            for key, value in json_object["improvements"].items():
                module, imp_name = key.split(":")
                level = value
                improvements.append([module, imp_name, level])

        toolset = f"{mod_id}_{material}"

        output = Replacement(item_id, mod_id, replacement_type, versions, toolset, material, handle_material, improvements)
        return output

    def check_valid(self):
        complaint_string = ""
        valid = True
        # Check whether category is acceptable
        if self.replacement_type not in ["axe", "hoe", "knife", "pick", "shovel", "sword", "bow"]:
            valid = False
            complaint_string += f"\n      '{self.replacement_type}' is not a valid replaceable tool type"

        if not valid:
            print(f"Replacement of '{self.mod_id}:{self.item_id}' failed verification. Reasons: {complaint_string}")

    # Compares the Replacement to an original.
    def compare_to_original(self, json_object, legacy):
        print(f"Comparing replacement of {self.item_id}...")
        jsonified = self.get_json(legacy)
        print("Difference between self and original:")
        print(diff(json_object, jsonified))
        print("Saving and restoring from CSV...")
        csvified = self.get_csv_row()
        restored = Replacement.create_from_csv(csvified)
        restored_json = restored[0].get_json(legacy)
        print("Difference between restored and originally created:")
        print(diff(jsonified, restored_json))

    # Generates a string formatted for printing
    def get_print_string(self):
        handle_string = f" with handle material '{self.handle_material_key}'" if self.handle_material_key else ""
        return f'''
        Replacement of '{self.item_id}' from mod '{self.mod_id}' uses material '{self.mod_id}_{self.material_key}'{handle_string}. Replacement type: {self.replacement_type.name}.
        Improvements: {self.improvements}
        Versions: {[ver.get_print_string() for ver in self.versions]}.
        '''

    # Generates a JSON object
    def get_json(self, legacy):
        output = OrderedDict()

        util.add_mod_loaded_condition(output, self.mod_id)

        predicate = OrderedDict()
        if legacy:
            predicate["item"] = f"{self.mod_id}:{self.item_id}"
        else:
            predicate["items"] = [f"{self.mod_id}:{self.item_id}"]
        output["predicate"] = predicate

        output["item"] = f"tetra:modular_{self.replacement_type.get_modular_type().value}"

        modules = OrderedDict()
        material_key = self.material_key
        default_handle_material = "string" if self.replacement_type == ReplacementType.BOW else "stick"
        handle_material = self.handle_material_key if self.handle_material_key else default_handle_material
        match self.replacement_type:
            case ReplacementType.AXE:
                modules["double/head_left"] = ["double/basic_axe_left", f"basic_axe/{material_key}"]
                modules["double/head_right"] = ["double/butt_right", f"butt/{material_key}"]
                modules["double/handle"] = ["double/basic_handle", f"basic_handle/{handle_material}"]
            case ReplacementType.DOUBLE_AXE:
                modules["double/head_left"] = ["double/basic_axe_left", f"basic_axe/{material_key}"]
                modules["double/head_right"] = ["double/basic_axe_right", f"basic_axe/{material_key}"]
                modules["double/handle"] = ["double/basic_handle", f"basic_handle/{handle_material}"]
            case ReplacementType.PICK:
                modules["double/head_left"] = ["double/basic_pickaxe_left", f"basic_pickaxe/{material_key}"]
                modules["double/head_right"] = ["double/basic_pickaxe_right", f"basic_pickaxe/{material_key}"]
                modules["double/handle"] = ["double/basic_handle", f"basic_handle/{handle_material}"]
            case ReplacementType.HOE:
                modules["double/head_left"] = ["double/hoe_left", f"hoe/{material_key}"]
                modules["double/head_right"] = ["double/butt_right", f"butt/{material_key}"]
                modules["double/handle"] = ["double/basic_handle", f"basic_handle/{handle_material}"]
            case ReplacementType.SHOVEL:
                modules["single/head"] = ["single/basic_shovel", f"basic_shovel/{material_key}"]
                modules["single/handle"] = ["single/basic_handle", f"basic_handle/{handle_material}"]
            case ReplacementType.SPEAR:
                modules["single/head"] = ["single/spearhead", f"spearhead/{material_key}"]
                modules["single/handle"] = ["single/light_handle", f"light_handle/{handle_material}"]
            case ReplacementType.SWORD:
                modules["sword/blade"] = ["sword/basic_blade", f"basic_blade/{material_key}"]
                modules["sword/hilt"] = ["sword/basic_hilt", f"basic_hilt/{handle_material}"]
                modules["sword/pommel"] = ["sword/decorative_pommel", f"decorative_pommel/{material_key}"]
                modules["sword/guard"] = ["sword/makeshift_guard", f"makeshift_guard/{material_key}"]
            case ReplacementType.KNIFE:
                modules["sword/blade"] = ["sword/short_blade", f"short_blade/{material_key}"]
                modules["sword/hilt"] = ["sword/basic_hilt", f"basic_hilt/{handle_material}"]
                modules["sword/pommel"] = ["sword/decorative_pommel", f"decorative_pommel/{material_key}"]
                modules["sword/guard"] = ["sword/makeshift_guard", f"makeshift_guard/{material_key}"]
            case ReplacementType.BOW:
                modules["bow/stave"] = ["bow/straight_stave", f"straight_stave/{material_key}"]
                modules["bow/string"] = ["bow/basic_string", f"basic_string/{handle_material}"]
            case ReplacementType.CROSSBOW:
                modules["crossbow/stave"] = ["crossbow/basic_stave", f"basic_stave/{material_key}"]
                modules["crossbow/stock"] = ["crossbow/basic_stock", f"basic_stock/{material_key}"]
                modules["crossbow/string"] = ["crossbow/basic_string", f"basic_string/{handle_material}"]
                modules["crossbow/attachment_1"] = ["crossbow/stirrup", f"stirrup/iron"]
            case ReplacementType.SHIELD:
                modules["shield/plate"] = ["shield/tower", f"tower/{material_key}"]
                modules["shield/grip"] = ["shield/basic_grip", f"basic_grip/{handle_material}"]

        output["modules"] = modules

        if self.improvements:
            # print(f"Improvements: {self.improvements}")
            improvements = OrderedDict()
            for imp in self.improvements:
                improvements[f"{imp[0]}:{imp[1]}"] = int(imp[2])
            output["improvements"] = improvements

        return output

    # Generates a CSV row
    def get_csv_row(self):
        improvements = []
        for x in self.improvements:
            improvements.append(" ".join([str(y) for y in x]))

        output = [self.item_id, self.mod_id, self.replacement_type.value, get_versions_csv_string(self.versions),
                  self.material_key, self.handle_material_key, ", ".join(improvements)]
        # print(f"Created CSV row: {output}")
        return output

    def matches(self, other_replacement, verbose=False):
        match = True
        unmatches = []
        if self.replacement_type != other_replacement.replacement_type:
            unmatches.append("replacement type")
            match = False
        if self.mod_id != other_replacement.mod_id:
            unmatches.append("mod ID")
            match = False
        if self.item_id != other_replacement.item_id:
            unmatches.append("item ID")
            match = False
        if self.material_key != other_replacement.material_key:
            unmatches.append("material name")
            match = False
        if self.handle_material_key != other_replacement.handle_material_key:
            unmatches.append("handle material name")
            match = False
        if self.improvements != other_replacement.improvements:
            unmatches.append("improvements")
            match = False

        if match:
            if verbose or len(unmatches) < 4:
                print(f"{self.item_id} replacement matches {other_replacement.item_id} replacement")
            return True
        else:
            if verbose:
                print(f"{self.item_id} replacement does not match {other_replacement.item_id}: mismatched {', '.join(unmatches)}")
            return False

    def assimilate(self, other_replacement):
        if not self.matches(other_replacement):
            raise ValueError(f"Can't assimilate {self.item_id} and {other_replacement.item_id}, no match detected")

        self.versions = list(set(self.versions + other_replacement.versions))


# Generates a bunch of replacements from a JSON file
def gen_replacements_from_json(json_file, version):
    print(f"Generating replacements from json {json_file}")
    opened = open(json_file)
    reps = json.load(opened)
    outputs = []
    for item in reps:
        outputs.append(Replacement.create_from_json(item, version))
    return outputs


# # Generates a full JSON file object from a bunch of replacements
def get_json_file(list_of_replacements, legacy):
    return [x.get_json(legacy) for x in list_of_replacements]


class ReplacementType(Enum):
    AXE = "axe"
    DOUBLE_AXE = "double_axe"
    HOE = "hoe"
    PICK = "pick"
    SHOVEL = "shovel"
    SWORD = "sword"
    GREATSWORD = "greatsword"
    KNIFE = "knife"
    SPEAR = "spear"
    BOW = "bow"
    CROSSBOW = "crossbow"
    SHIELD = "shield"

    def second_module(self):
        if self in [ReplacementType.AXE, ReplacementType.HOE]:
            return "butt"
        elif self in [ReplacementType.DOUBLE_AXE]:
            return "basic_axe"
        elif self in [ReplacementType.PICK]:
            return "basic_pickaxe"
        elif self in [ReplacementType.SHOVEL]:
            return "basic_handle"
        elif self in [ReplacementType.SWORD, ReplacementType.GREATSWORD, ReplacementType.KNIFE]:
            return "basic_hilt"
        elif self in [ReplacementType.BOW]:
            return "basic_string"
        elif self in [ReplacementType.CROSSBOW]:
            return "basic_stock"
        elif self in [ReplacementType.SHIELD]:
            return "basic_grip"

    def get_modular_type(self):
        if self in [ReplacementType.AXE, ReplacementType.DOUBLE_AXE, ReplacementType.PICK, ReplacementType.HOE]:
            return ModularType.DOUBLE
        elif self in [ReplacementType.SHOVEL, ReplacementType.SPEAR]:
            return ModularType.SINGLE
        elif self in [ReplacementType.SWORD, ReplacementType.GREATSWORD, ReplacementType.KNIFE]:
            return ModularType.SWORD
        elif self in [ReplacementType.BOW]:
            return ModularType.BOW
        elif self in [ReplacementType.CROSSBOW]:
            return ModularType.CROSSBOW
        elif self in [ReplacementType.SHIELD]:
            return ModularType.SHIELD


def test():
    axesfile = "../../resources/Tetranomicon 1.16/data/tetra/replacements/tetranomiconaxes.json"
    # axes = gen_replacements_from_json(axesfile, MinecraftVersion.SIXTEEN)
    # for axe in axes:
    # print(f"{axe.get_print_string()}")
    # print(get_json_file(axes, True))

    opened = open(axesfile)
    reps = json.load(opened)
    axes = []
    for item in reps:
        replacement_object = Replacement.create_from_json(item, MinecraftVersion.SIXTEEN)
        axes.append(replacement_object)
        replacement_object.compare_to_original(item, True)
        print("\n\n")

    # axejsons = [x.get_json(True) for x in axes]

    # print(json.dumps(axejsons, indent=4))

    pass


if __name__ == "__main__":
    main()
