from collections import OrderedDict
from enum import Enum

from classes.mc_version import MinecraftVersion, get_versions_csv_string
import json
from jsondiff import diff

from classes.socket import ModularType
from classes.trait import get_traits_csv_string


def main():
    test()
    pass


class Replacement:
    # Replacement_Type is axe, double_axe hoe, knife, pick, shovel, or sword
    # Improvements is a list of lists of length 3: module, improvement, level
    def __init__(self, itemid, modid, replacement_type, versions, material, improvements):
        self.item_id = itemid
        self.mod_id = modid
        self.replacement_type = ReplacementType(replacement_type)
        self.versions = [MinecraftVersion.get_version(int(ver)) for ver in versions]
        self.material_name = material.lower()
        self.improvements = improvements
        # print(f"Generating Replacement with improvements {improvements}")

    @classmethod
    # Creates a Replacement from a CSV row
    def create_from_csv(cls, csv_row):
        print("Creating a replacement from a CSV row")
        if len(csv_row) != 6:
            raise ValueError(f"Failed attempt to create a replacement from csv row because row was wrong size: '{csv_row}'")

        itemid, mod_id, replacement_type, versions, material_name, improvements = csv_row

        # Turn comma-separated lists into actual lists
        versions = versions.split(", ")
        individual_improvements = improvements.split(", ")
        improvements_new = [x.split(" ") for x in individual_improvements]
        if not improvements:
            improvements_new = []

        rep = Replacement(itemid, mod_id, replacement_type, versions, material_name, improvements_new)
        # print(f"Generated replacement from CSV: {rep.get_print_string()}")
        return rep

    @classmethod
    # Creates a Replacement from a JSON object (*not* a file!)
    def create_from_json(cls, json_object, version):
        # print("Creating a replacement from a JSON")
        predicate_block = json_object["predicate"]
        mod_and_item = ""
        if version == MinecraftVersion.SIXTEEN:
            mod_and_item = json_object["predicate"]["item"]
        else:
            mod_and_item = json_object["predicate"]["items"][0]
        mod_id, item_id = mod_and_item.split(":")
        versions = [version.value]
        # print(f"Found mod id {mod_id} and item id {item_id} from combined form {mod_and_item}.")
        # print(f"Given versions {versions}.")

        modules_dict = json_object["modules"]
        # print(f"List of modules: {modules_dict}")

        first_module = None
        if "double/head_left" in modules_dict.keys():
            first_module = modules_dict["double/head_left"]
        elif "single/head" in modules_dict.keys():
            first_module = modules_dict["single/head"]
        elif "sword/blade" in modules_dict.keys():
            first_module = modules_dict["sword/blade"]

        # print(f"First module: {first_module}")
        module_type, module_key = first_module[0], first_module[1]
        # print(f"Module type: {module_type}. Module key: {module_key}")
        module, material = module_key.split("/")
        # print(f"Split module key into module {module} and material {material}.")

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
        second_module = None
        if "double/head_right" in modules_dict.keys():
            second_module = modules_dict["double/head_right"]
        elif "single/handle" in modules_dict.keys():
            second_module = modules_dict["single/handle"]
        elif "sword/hilt" in modules_dict.keys():
            second_module = modules_dict["sword/hilt"]
        name = second_module[1].split("/")[0]

        if name != replacement_type.second_module():
            raise ValueError(f"Encountered unexpected second module {name} when creating {replacement_type.name} replacement from json")

        # print(f"Found replacement type {replacement_type}.")

        improvements = []
        if "improvements" in json_object.keys():
            for key, value in json_object["improvements"].items():
                module, imp_name = key.split(":")
                level = value
                improvements.append([module, imp_name, level])

        # print("Generating Replacement item."
        output = Replacement(item_id, mod_id, replacement_type, versions, material, improvements)
        # legacy = version == MinecraftVersion.SIXTEEN
        # output_json = output.get_json(legacy)
        # print("Generated replacement from JSON. Output JSON has differences: ")
        # print(diff(json_object, output_json))

        return output

    def check_valid(self):
        complaint_string = ""
        valid = True
        # Check whether category is acceptable
        if self.replacement_type not in ["axe", "hoe", "knife", "pick", "shovel", "sword"]:
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
        restored_json = restored.get_json(legacy)
        print("Difference between restored and originally created:")
        print(diff(jsonified, restored_json))

    # Generates a string formatted for printing
    def get_print_string(self):
        return f'''
        Replacement of '{self.item_id}' from mod '{self.mod_id}' uses material '{self.mod_id}_{self.material_name}'. Replacement type: {self.replacement_type.name}.
        Improvements: {self.improvements}
        Versions: {[ver.get_print_string() for ver in self.versions]}.
        '''

    # Generates a JSON object
    def get_json(self, legacy):
        output = OrderedDict()

        predicate = OrderedDict()
        if legacy:
            predicate["item"] = f"{self.mod_id}:{self.item_id}"
        else:
            predicate["items"] = [f"{self.mod_id}:{self.item_id}"]
        output["predicate"] = predicate

        output["item"] = f"tetra:modular_{self.replacement_type.get_modular_type().value}"

        modules = OrderedDict()
        material_name = self.material_name
        modid = self.mod_id
        stick = "stick"
        match self.replacement_type:
            case ReplacementType.AXE:
                modules["double/head_left"] = ["double/basic_axe_left", f"basic_axe/{modid}_{material_name}"]
                modules["double/head_right"] = ["double/butt_right", f"butt/{modid}_{material_name}"]
                modules["double/handle"] = ["double/basic_handle", f"basic_handle/{stick}"]
            case ReplacementType.DOUBLE_AXE:
                modules["double/head_left"] = ["double/basic_axe_left", f"basic_axe/{modid}_{material_name}"]
                modules["double/head_right"] = ["double/basic_axe_right", f"basic_axe/{modid}_{material_name}"]
                modules["double/handle"] = ["double/basic_handle", "basic_handle/stick"]
            case ReplacementType.PICK:
                modules["double/head_left"] = ["double/basic_pickaxe_left", f"basic_pickaxe/{modid}_{material_name}"]
                modules["double/head_right"] = ["double/basic_pickaxe_right", f"basic_pickaxe/{modid}_{material_name}"]
                modules["double/handle"] = ["double/basic_handle", "basic_handle/stick"]
            case ReplacementType.HOE:
                modules["double/head_left"] = ["double/hoe_left", f"hoe/{modid}_{material_name}"]
                modules["double/head_right"] = ["double/butt_right", f"butt/{modid}_{material_name}"]
                modules["double/handle"] = ["double/basic_handle", "basic_handle/stick"]
            case ReplacementType.SHOVEL:
                modules["single/head"] = ["single/basic_shovel", f"basic_shovel/{modid}_{material_name}"]
                modules["single/handle"] = ["single/basic_handle", "basic_handle/stick"]
            case ReplacementType.SWORD:
                modules["sword/blade"] = ["sword/basic_blade", f"basic_blade/{modid}_{material_name}"]
                modules["sword/hilt"] = ["sword/basic_hilt", "basic_hilt/stick"]
                modules["sword/pommel"] = ["sword/decorative_pommel", f"decorative_pommel/{modid}_{material_name}"]
                modules["sword/guard"] = ["sword/makeshift_guard", f"makeshift_guard/{modid}_{material_name}"]
            case ReplacementType.KNIFE:
                modules["sword/blade"] = ["sword/short_blade", f"short_blade/{modid}_{material_name}"]
                modules["sword/hilt"] = ["sword/basic_hilt", "basic_hilt/stick"]
                modules["sword/pommel"] = ["sword/decorative_pommel", f"decorative_pommel/{modid}_{material_name}"]
                modules["sword/guard"] = ["sword/makeshift_guard", f"makeshift_guard/{modid}_{material_name}"]
        output["modules"] = modules

        if self.improvements:
            print(f"Improvements: {self.improvements}")
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
                self.material_name, ", ".join(improvements)]
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
        if self.material_name != other_replacement.material_name:
            unmatches.append("material name")
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

    def get_modular_type(self):
        if self in [ReplacementType.AXE, ReplacementType.DOUBLE_AXE, ReplacementType.PICK, ReplacementType.HOE]:
            return ModularType.DOUBLE
        elif self in [ReplacementType.SHOVEL]:
            return ModularType.SINGLE
        elif self in [ReplacementType.SWORD, ReplacementType.GREATSWORD, ReplacementType.KNIFE]:
            return ModularType.SWORD


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
