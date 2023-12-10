import json
import os
from collections import OrderedDict

from jsondiff import diff

from tool_requirements import ToolRequirements
from tool_properties import ToolLevel
from trait import gen_traits_from_string, get_traits_csv_string
from mc_version import MinecraftVersion, get_versions_csv_string


def main():
    test()
    pass


class Material:
    # Generates a Material from a bunch of inputs.
    # Inputs are strings, except:
    # versions is a list of MinecraftVersions
    # textures is a list of strings
    # effects and improvements are lists of Traits
    # reqtools is a ToolRequirements
    # tool_level is input as a ToolLevel
    def __init__(self, name, adjective, mod_id, versions, category, primary, secondary, tertiary, durability,
                 integrity_cost, integrity_gain, magic, tool_level, tool_efficiency, tint, texts, item, effects,
                 improvements, reqtools):
        self.name = name  # e.g. "Gold", "Aurora Crystal"
        self.prefix = adjective  # e.g. "Golden"
        self.mod_id = mod_id.lower()
        # Material key is used as the 'key' in the material json as well as the json filename
        self.material_key = f"{mod_id}_{name.lower().replace(' ', '_')}"
        # Versions is a list of MinecraftVersions
        self.versions = versions
        # Category is one of fibre, gem, metal, scale, stone, wood
        self.category = category
        self.primary = int(primary) if float(primary).is_integer() else float(primary)
        self.secondary = int(secondary) if float(secondary).is_integer() else float(secondary)
        self.tertiary = int(tertiary) if float(tertiary).is_integer() else float(tertiary)
        self.durability = int(durability)
        self.integrity_cost = int(integrity_cost)
        self.integrity_gain = int(integrity_gain)
        self.magic_capacity = int(magic)
        # Tool level is stored as a ToolLevel
        self.tool_level = tool_level
        self.tool_efficiency = int(tool_efficiency) if float(tool_efficiency).is_integer() else float(tool_efficiency)
        self.tint = tint
        # Textures is a list of strings
        self.textures = texts
        self.item = item
        # A list of Traits
        self.effects = effects
        # A list of Traits
        self.improvements = improvements
        # A ToolRequirements object
        self.required_tools = reqtools
        self.primary = int(primary) if isinstance(primary, int) else self.primary

    @classmethod
    # Generates one or more Materials from a CSV row
    def create_from_csv(cls, csv_row):
        # print("Creating a material from a CSV row")
        if len(csv_row) != 20:
            raise ValueError(
                f"Failed attempt to create a material because csv row was wrong size ({len(csv_row)}): '{csv_row}'")

        names_raw, prefixes_raw, mod_ids_raw, versions, category, primary, secondary, tertiary, dur, \
            integrity_cost, integrity_gain, magic, tool_level, tool_efficiency, \
            tints_raw, texts, items_raw, effects, improvements, tool_requirements \
            = csv_row

        # Turn comma-separated lists into lists of strings
        versions, texts = versions.split(", "), texts.split(", ")

        new_effects = gen_traits_from_string(effects)
        new_improvements = gen_traits_from_string(improvements)
        new_tool_requirements = ToolRequirements.create_from_csv(tool_requirements)
        # Tool Level must be input as tier number, not 1.16 version!
        new_tool_level = ToolLevel.get_tool_level(tool_level)

        # Multiple materials can share a row. This allows individual entries for name, prefix, mod id, tints, items
        # Any of these with only one entry is applied to all
        names = names_raw.split(", ")
        prefixes = prefixes_raw.split(", ")
        mod_ids = mod_ids_raw.split(", ")
        tints = tints_raw.split(", ")
        items = items_raw.split(", ")
        version_lists = versions.split("; ")

        number_of_materials = len(names)
        outputs = []
        for i in range(number_of_materials):
            name = names[i] if len(names) > 1 else names[0]
            prefix = prefixes[i] if len(prefixes) > 1 else prefixes[0]
            mod_id = mod_ids[i] if len(mod_ids) > 1 else mod_ids[0]
            tint = tints[i] if len(tints) > 1 else tints[0]
            item = items[i] if len(items) > 1 else items[0]
            vers = version_lists[i] if len(version_lists) > 1 else version_lists[0]

            new_versions = [MinecraftVersion.get_version(int(ver)) for ver in vers]

            mat = Material(name, prefix, mod_id, new_versions, category, primary, secondary, tertiary, dur, integrity_cost,
                           integrity_gain, magic, new_tool_level, tool_efficiency, tint, texts,
                           item, new_effects, new_improvements, new_tool_requirements)
            outputs.append(mat)
        # print(f"Generated material from CSV: {mat.get_print_string()}")
        return outputs

    @classmethod
    # Generates a Material from a JSON file
    def create_from_json(cls, json_file, lang_file, version):
        opened = open(json_file)
        mat = json.load(opened)

        # print(f"Creating material {mat['key']} from JSON")

        key = mat["key"]
        cat = mat["category"]
        pri = mat["primary"]
        sec = mat["secondary"]
        dur = mat["durability"]
        ter = mat["tertiary"]
        ic = mat["integrityCost"]
        ig = mat["integrityGain"]
        mc = mat["magicCapacity"]
        tl = mat["toolLevel"] if "toolLevel" in mat.keys() else 0
        te = mat["toolEfficiency"]
        tin = mat["tints"]["glyph"]
        tex = mat["textures"]
        it = mat["material"]
        imp = mat["improvements"] if "improvements" in mat.keys() else {}
        eff = mat["effects"] if "effects" in mat.keys() else {}
        req = mat["requiredTools"]

        modid, item = "", ""
        for name, value in it.items():
            if name == "item":
                modid, item = value.split(":")
            if name == "items":
                modid, item = value[0].split(":")

        lang_opened = open(lang_file)
        lang = json.load(lang_opened)

        # Get name and prefix from lang file
        name = lang[f"tetra.material.{key}"] if f"tetra.material.{key}" in lang.keys() else "NAMELESS"
        prefix = lang[f"tetra.material.{key}.prefix"] if f"tetra.material.{key}.prefix" in lang.keys() else "PREFIXLESS"

        implist = []
        efflist = []
        reqlist = []

        for key, value in imp.items():
            implist.append(f"imp {key} {value} {0}")
        for key, value in eff.items():
            if isinstance(value, list):
                efflist.append(f"eff {key} {value[0]} {value[1]}")
            else:
                efflist.append(f"eff {key} {value} {0}")
        for key, value in req.items():
            if version == MinecraftVersion.SIXTEEN:
                tool_level = ToolLevel.ToolLevel_from_legacy(value)
            else:
                tool_level = ToolLevel.get_tool_level(value)
            reqlist.append(f"{key} {tool_level.value}")
            # print("added to requirements list: " + f"{key} {tool_level_as_int(value)}")

        newimp = ", ".join(implist)
        neweff = ", ".join(efflist)
        newreq = ", ".join(reqlist)

        if version == MinecraftVersion.SIXTEEN:
            new_tl = ToolLevel.ToolLevel_from_legacy(tl)
        else:
            new_tl = ToolLevel.get_tool_level(tl)
        new_tl = new_tl.value()

        ver = version.value
        texts = ", ".join(tex)

        fake_csv_row = [name, prefix, modid, str(ver), cat, pri, sec, ter, dur, ic, ig, mc, new_tl, te, tin, texts, item,
                        neweff, newimp, newreq]

        # print(f"Creating {name} material from JSON")
        output = Material.create_from_csv(fake_csv_row)[0]
        # print(f"Material has a tool level of {output.tool_level}")

        return output

    def check_valid(self):
        complaint_string = ""
        valid = True
        # Check whether material key is what it should be
        if self.material_key != f"{self.mod_id}_{self.name.lower().replace(' ', '_')}":
            valid = False
            complaint_string += f"\n      material key '{self.material_key}' does not fit pattern"
        # Check whether category is acceptable
        if self.category not in ["fibre", "gem", "metal", "scale", "stone", "wood"]:
            valid = False
            complaint_string += f"\n      '{self.category}' is not a valid material category"

        if not valid:
            print(f"Material '{self.material_key}' failed verification. Reasons: {complaint_string}")

    # Compares the Material to an original.
    def compare_to_original(self, json_object, legacy):
        printed = False
        # print(f"Comparing replacement of material {self.name}...")
        jsonified = self.get_json(legacy)
        difference1 = diff(json_object, jsonified)
        if difference1:
            print(f"1.{self.versions[0].value}/{self.material_key}: Difference between self and original: " + str(difference1))
            printed = True
        # print("Saving and restoring from CSV...")
        csvified = self.get_csv_row()
        restored = Material.create_from_csv(csvified)[0]
        restored_json = restored.get_json(legacy)
        difference2 = diff(jsonified, restored_json)
        if difference2:
            print(f"1.{self.versions[0].value}/{self.material_key}: Difference between restored and originally created: " + str(difference2))
            printed = True
        if printed:
            print()

    # Generates a string formatted for printing
    def get_print_string(self):
        return f'''
        Material: '{self.name}' from mod '{self.mod_id}'. Material key: '{self.material_key}', Material Adjective: '{self.prefix}'.
        Versions: {[ver.get_print_string() for ver in self.versions]}.
        Material category: {self.category}
        Base Stats: Hardness {self.primary}, Density {self.secondary}, Flexibility {self.tertiary}.
        Other Stats: Durability {self.durability}, Integrity cost/gain {self.integrity_cost}/{self.integrity_gain}, Magic Capacity {self.magic_capacity}, Tool Level/Efficiency {self.tool_level.value}/{self.tool_efficiency}.
        Visual: Tint '{self.tint}', Textures {self.textures}
        Effects: {[eff.get_print_string() for eff in self.effects]}
        Improvements: {[imp.get_print_string() for imp in self.improvements]}
        {self.required_tools.get_print_string()}
        '''

    # Generates a JSON object
    def get_json(self, legacy):
        output = OrderedDict()

        # print(f"Getting JSON for material {self.material_key}")

        output["key"] = self.material_key
        output["category"] = self.category
        output["primary"] = self.primary
        output["secondary"] = self.secondary
        output["tertiary"] = self.tertiary
        output["durability"] = self.durability
        output["integrityCost"] = self.integrity_cost
        output["integrityGain"] = self.integrity_gain
        output["magicCapacity"] = self.magic_capacity
        # print(f"Material's tool level is {self.tool_level}")
        output["toolLevel"] = self.tool_level.get_legacy_int() if legacy else self.tool_level.get_modern_string()
        output["toolEfficiency"] = self.tool_efficiency

        if self.improvements:
            imps_dict = OrderedDict()
            for imp in self.improvements:
                imps_dict[f"{imp.name}"] = imp.level
            output["improvements"] = imps_dict

        if self.effects:
            effs_dict = OrderedDict()
            for eff in self.effects:
                if eff.efficiency != 0:
                    effs_dict[f"{eff.name}"] = [eff.level, eff.efficiency]
                else:
                    effs_dict[f"{eff.name}"] = eff.level
            output["effects"] = effs_dict

        tints_dict = OrderedDict()
        tints_dict["glyph"] = self.tint
        tints_dict["texture"] = self.tint
        output["tints"] = tints_dict

        output["textures"] = self.textures

        material_dict = OrderedDict()
        if legacy:
            material_dict["item"] = f"{self.mod_id}:{self.item}"
        else:
            material_dict["items"] = [f"{self.mod_id}:{self.item}"]
        output["material"] = material_dict

        output["requiredTools"] = self.required_tools.get_json_object(legacy)

        # Turn stuff into strings if legacy
        if legacy:
            output["primary"] = str(self.primary)
            output["secondary"] = str(self.secondary)
            output["tertiary"] = str(self.tertiary)
            output["durability"] = str(self.durability)
            output["integrityCost"] = str(self.integrity_cost)
            output["integrityGain"] = str(self.integrity_gain)
            output["magicCapacity"] = str(self.magic_capacity)
            output["toolLevel"] = str(output["toolLevel"])
            output["toolEfficiency"] = str(self.tool_efficiency)

        return output

    # Generates the lang lines for a material (returned as a list, no commas)
    def get_lang_lines(self):
        output = [f'''"tetra.material.{self.material_key}": "{self.name}"''',
                  f'''"tetra.material.{self.material_key}.prefix": "{self.prefix}"''']
        return output

    # Generates a CSV row
    def get_csv_row(self):
        vers = get_versions_csv_string(self.versions)
        text = ", ".join(self.textures)
        eff = get_traits_csv_string(self.effects)
        imp = get_traits_csv_string(self.improvements)
        tools = self.required_tools.get_csv_string()
        output = [self.name, self.prefix, self.mod_id, vers, self.category,
                  self.primary, self.secondary, self.tertiary, self.durability,
                  self.integrity_cost, self.integrity_gain, self.magic_capacity, self.tool_level.value, self.tool_efficiency,
                  self.tint, text, self.item,
                  eff, imp, tools]

        return output

    # Returns True if the other material matches this one.
    # Generally used for combining the same material across versions.
    def matches(self, other_material, verbose=False):
        mismatch = False
        unmatches = []

        # Make name not necessarily a match? Prefix too?
        if self.name.lower() != other_material.name.lower():
            unmatches.append("name")
            mismatch = True

        if self.prefix.lower() != other_material.prefix.lower():
            unmatches.append("prefix")
            mismatch = True

        if self.mod_id != other_material.mod_id:
            unmatches.append("mod_id")
            mismatch = True

        if self.category != other_material.category:
            unmatches.append("category")
            mismatch = True

        if self.primary != other_material.primary:
            unmatches.append("primary")
            mismatch = True

        if self.secondary != other_material.secondary:
            unmatches.append("secondary")
            mismatch = True

        if self.tertiary != other_material.tertiary:
            unmatches.append("tertiary")
            mismatch = True

        if self.durability != other_material.durability:
            unmatches.append("durability")
            mismatch = True

        if self.integrity_cost != other_material.integrity_cost:
            unmatches.append("integrity_cost")
            mismatch = True

        if self.integrity_gain != other_material.integrity_gain:
            unmatches.append("integrity_gain")
            mismatch = True

        if self.magic_capacity != other_material.magic_capacity:
            unmatches.append("magic_capacity")
            mismatch = True

        if self.tool_level != other_material.tool_level:
            unmatches.append("tool_level")
            mismatch = True

        if self.tool_efficiency != other_material.tool_efficiency:
            unmatches.append("tool_efficiency")
            mismatch = True

        if self.tint != other_material.tint:
            unmatches.append("tint")
            mismatch = True

        if self.textures != other_material.textures:
            unmatches.append("textures")
            mismatch = True

        if self.item != other_material.item:
            unmatches.append("item")
            mismatch = True

        # effects, improvements, and required tools
        pass

        if mismatch:
            if verbose or len(unmatches) < 5:
                print(f"{self.name} does not match {other_material.name}: mismatched {', '.join(unmatches)}")
            return False
        else:
            if verbose:
                print(f"{self.name} matches {other_material.name}")
            return True

    # Assimilates the other material
    # Should only work if they match!
    def assimilate(self, other_material):
        if not self.matches(other_material):
            raise ValueError(f"Can't assimilate {self.name} and {other_material.name}, no match detected")

        new_material = self
        for ver in other_material.versions:
            new_material.versions.append(ver)

        return new_material

    def assimilate_in_place(self, other_material):
        if not self.matches(other_material):
            raise ValueError(f"Can't assimilate {self.name} and {other_material.name}, no match detected")

        self.versions.extend(other_material.versions)


def test():
    # print("1.16 testing")
    mats16 = "../../resources/Tetranomicon 1.16/data/tetra/materials"
    lang = "../../resources/Tetranomicon 1.16/assets/tetranomicon/lang/en_us.json"

    materials16 = []

    for root, dirs, files in os.walk(mats16):
        for file in files:
            filepath = os.path.join(root, file)
            material = Material.create_from_json(filepath, lang, MinecraftVersion.SIXTEEN)
            materials16.append(material)
            opened = open(filepath)
            og_json = json.load(opened)
            material.compare_to_original(og_json, True)

    # print("\n\n\n1.18 testing")
    mats18 = "../../resources/Tetranomicon 1.18/data/tetra/materials"
    lang = "../../resources/Tetranomicon 1.18/assets/tetranomicon/lang/en_us.json"

    materials18 = []

    for root, dirs, files in os.walk(mats18):
        for file in files:
            filepath = os.path.join(root, file)
            material = Material.create_from_json(filepath, lang, MinecraftVersion.EIGHTEEN)
            materials18.append(material)
            opened = open(filepath)
            og_json = json.load(opened)
            material.compare_to_original(og_json, False)

    mats19 = "../../resources/Tetranomicon 1.19/data/tetra/materials"
    lang = "../../resources/Tetranomicon 1.19/assets/tetranomicon/lang/en_us.json"

    materials19 = []

    for root, dirs, files in os.walk(mats19):
        for file in files:
            filepath = os.path.join(root, file)
            material = Material.create_from_json(filepath, lang, MinecraftVersion.NINETEEN)
            materials19.append(material)
            opened = open(filepath)
            og_json = json.load(opened)
            material.compare_to_original(og_json, False)


if __name__ == "__main__":
    main()
