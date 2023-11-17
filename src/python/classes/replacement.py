from enum import Enum

from classes.mc_version import MinecraftVersion, get_versions_csv_string
import json


def main():
    test()
    pass


class Replacement:
    # Replacement_Type is axe, double_axe hoe, knife, pick, shovel, or sword
    # Improvements is a list of lists of length 3: module, improvement, level
    def __init__(self, replacement_type, versions, modid, itemid, material, improvements):
        self.replacement_type = ReplacementType(replacement_type)
        self.versions = [MinecraftVersion.get_version(int(ver)) for ver in versions]
        self.mod_id = modid
        self.item_id = itemid
        self.material_name = material.lower()
        self.improvements = improvements

    @classmethod
    # Creates a Replacement from a CSV row
    def create_from_csv(cls, csv_row):
        print("Creating a self from a CSV row")
        if len(csv_row) != 5:
            raise ValueError(f"Failed attempt to create a self from csv row because row was wrong size: '{csv_row}'")

        replacement_type, versions, modid, itemid, material_name, improvements = csv_row

        # Turn comma-separated lists into actual lists
        versions = versions.split(", ")
        improvements_new = [[x.split(" ") for x in improvements.split(", ")]]

        rep = Replacement(replacement_type, versions, modid, itemid, material_name, improvements_new)
        print(f"Generated material from CSV: {rep.get_print_string()}")
        return rep

    @classmethod
    # Creates a Replacement from a JSON object (*not* a file!)
    def create_from_json(cls, json_object, version):
        print("Creating a replacement from a JSON")
        mod_and_item = json_object["predicate"]["item"]
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

        replacement_type = ""
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
            case "basic_pickaxe_left":
                replacement_type = ReplacementType.PICK
            case "basic_shovel":
                replacement_type = ReplacementType.SHOVEL
            case "basic_blade":
                replacement_type = ReplacementType.SWORD

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

        print(f"Found replacement type {replacement_type}.")

        improvements = []
        if "improvements" in json_object.keys():
            for key, value in json_object["improvements"].items():
                module, imp_name = key.split(":")
                level = value
                improvements.append([module, imp_name, level])

        # print("Generating Replacement item."

        return Replacement(replacement_type, versions, mod_id, item_id, material, improvements)

    def check_valid(self):
        complaint_string = ""
        valid = True
        # Check whether category is acceptable
        if self.replacement_type not in ["axe", "hoe", "knife", "pick", "shovel", "sword"]:
            valid = False
            complaint_string += f"\n      '{self.replacement_type}' is not a valid replaceable tool type"

        if not valid:
            print(f"Replacement of '{self.mod_id}:{self.item_id}' failed verification. Reasons: {complaint_string}")

    # Generates a string formatted for printing
    def get_print_string(self):
        return f'''
        Replacement of '{self.item_id}' from mod '{self.mod_id}' uses material '{self.mod_id}_{self.material_name}'. Replacement type: {self.replacement_type.name}.
        Improvements: {self.improvements}
        Versions: {[ver.get_print_string() for ver in self.versions]}.
        '''

    # Generates a json chunk
    def get_json_block(self, legacy):
        replacement_type = self.replacement_type
        modid = self.mod_id
        itemid = self.item_id
        material_name = self.material_name
        predicate_row = self.get_predicate_row(legacy)
        improvements_block = self.get_improvements_json_block()

        match replacement_type:
            case ReplacementType.AXE:
                return f'''{{
        "predicate": {{
            {predicate_row}
        }},
        "item": "tetra:modular_double",
        "modules": {{
            "double/head_left": ["double/basic_axe_left", "basic_axe/{modid}_{material_name}"],
            "double/head_right": ["double/butt_right", "butt/{modid}_{material_name}"],
            "double/handle": ["double/basic_handle", "basic_handle/stick"]
        }}{improvements_block}
    }}'''

            case ReplacementType.DOUBLE_AXE:
                return f'''{{
        "predicate": {{
            {predicate_row}
        }},
        "item": "tetra:modular_double",
        "modules": {{
            "double/head_left": ["double/basic_axe_left", "basic_axe/{modid}_{material_name}"],
            "double/head_right": ["double/basic_axe_right", "basic_axe/{modid}_{material_name}"],
            "double/handle": ["double/basic_handle", "basic_handle/stick"]
        }}{improvements_block}
    }}'''

            case ReplacementType.HOE:
                return f'''{{
        "predicate": {{
            {predicate_row}
        }},
        "item": "tetra:modular_double",
        "modules": {{
            "double/head_left": ["double/hoe_left", "hoe/{modid}_{material_name}"],
            "double/head_right": ["double/butt_right", "butt/{modid}_{material_name}"],
            "double/handle": ["double/basic_handle", "basic_handle/stick"]
        }}{improvements_block}
    }}'''

            case ReplacementType.KNIFE:
                return f'''{{
        "predicate": {{
            {predicate_row}
        }},
        "item": "tetra:modular_sword",
        "modules": {{
            "sword/blade": ["sword/short_blade", "short_blade/{modid}_{material_name}"],
            "sword/hilt": ["sword/basic_hilt", "basic_hilt/stick"]
        }}{improvements_block}
    }}'''

            case ReplacementType.PICK:
                return f'''{{
        "predicate": {{
            {predicate_row}
        }},
        "item": "tetra:modular_double",
        "modules": {{
            "double/head_left": ["double/basic_pickaxe_left", "basic_pickaxe/{modid}_{material_name}"],
            "double/head_right": ["double/basic_pickaxe_right", "basic_pickaxe/{modid}_{material_name}"],
            "double/handle": ["double/basic_handle", "basic_handle/stick"]
        }}{improvements_block}
    }}'''

            case ReplacementType.SHOVEL:
                return f'''{{
        "predicate": {{
            {predicate_row}
        }},
        "item": "tetra:modular_single",
        "modules": {{
            "single/head": ["single/basic_shovel", "basic_shovel/{modid}_{material_name}"],
            "single/handle": ["single/basic_handle", "basic_handle/stick"]
        }}{improvements_block}
    }}'''

            case ReplacementType.SWORD:
                return f'''{{
        "predicate": {{
            {predicate_row}
        }},
        "item": "tetra:modular_sword",
        "modules": {{
            "sword/blade": ["sword/basic_blade", "basic_blade/{modid}_{material_name}"],
            "sword/hilt": ["sword/basic_hilt", "basic_hilt/stick"],
            "sword/pommel": ["sword/decorative_pommel", "decorative_pommel/{modid}_{material_name}"],
            "sword/guard": ["sword/makeshift_guard", "makeshift_guard/{modid}_{material_name}"]
        }}{improvements_block}
    }}'''

        raise TypeError(
            f"Invalid type! Attempted to generate replacement block with arguments: [{replacement_type}, {modid}, {itemid}, {material_name}]")

    # Returns the improvements block to put in a json
    def get_improvements_json_block(self):
        if not self.improvements:
            return ""
        else:
            imps = []
            for imp in self.improvements:
                module = imp[0]
                improve = imp[1]
                level = int(imp[2])
                imps.append(f'''"{module}:{improve}": {level}''')
            inner_string = ",\n            ".join(imps)
            return f''',
        "improvements": {
            {inner_string}
        }'''

    # Returns the predicate row to put in a json
    # This is the only difference between legacy and modern formatting
    def get_predicate_row(self, legacy):
        if legacy:
            return f'''"item": "{self.mod_id}:{self.item_id}"'''
        else:
            return f'''"items": [ "{self.mod_id}:{self.item_id}" ]'''
        pass

    # Generates a CSV row
    def get_csv_row(self):
        return [self.replacement_type, get_versions_csv_string(self.versions), self.mod_id, self.item_id,
                self.material_name, ", ".join([" ".join(x) for x in self.improvements])]


# Generates a bunch of replacements from a JSON file
def gen_replacements_from_json(json_file, version):
    opened = open(json_file)
    reps = json.load(opened)
    outputs = []
    for item in reps:
        outputs.append(Replacement.create_from_json(item, version))
    return outputs


# Generates a full JSON file from a bunch of replacements
def get_json_file(list_of_replacements, legacy):
    blocks = [x.get_json_block(legacy) for x in list_of_replacements]
    inner = ",\n    ".join(blocks)
    return f'''[
    {inner}\n]'''


class ReplacementType(Enum):
    AXE = "axe"
    DOUBLE_AXE = "double_axe"
    HOE = "hoe"
    PICK = "pick"
    SHOVEL = "shovel"
    SWORD = "sword"
    KNIFE = "knife"

    def second_module(self):
        match self:
            case ReplacementType.AXE:
                return "butt"
            case ReplacementType.DOUBLE_AXE:
                return "basic_axe"
            case ReplacementType.HOE:
                return "butt"
            case ReplacementType.PICK:
                return "basic_pickaxe"
            case ReplacementType.SHOVEL:
                return "basic_handle"
            case ReplacementType.SWORD:
                return "basic_hilt"
            case ReplacementType.KNIFE:
                return "basic_hilt"


def test():
    axesfile = "../../resources/Tetranomicon 1.16/data/tetra/replacements/tetranomiconaxes.json"
    axes = gen_replacements_from_json(axesfile, MinecraftVersion.SIXTEEN)
    for axe in axes:
        print(f"{axe.get_print_string()}")
    print(get_json_file(axes, True))
    pass


if __name__ == "__main__":
    main()
