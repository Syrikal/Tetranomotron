from collections import OrderedDict
from enum import Enum
import json

from jsondiff import diff

from mc_version import MinecraftVersion, get_versions_csv_string
from tool_properties import ToolType
from trait import gen_traits_from_string, get_traits_csv_string


def main():
    test()
    pass


class Socket:
    # Generates a Socket from a bunch of inputs.
    # Inputs are strings, except:
    # versions is a list of MinecraftVersions
    # effects and attributes are lists of Traits
    # tool_boosts is a list of ToolBoosts
    # modular_types is a list of ModularTypes
    def __init__(self, name, mod_id, colored_string, versions, modular_types, durability, durability_multiplier,
                 integrity_cost, tint, textures, attributes, effects, tool_level, tool_efficiency, item, xp_cost):
        self.name = name  # e.g. "Ametrine"
        self.mod_id = mod_id.lower()  # e.g. "byg"
        self.colored_string = colored_string  # e.g. "§9Blue Geode§r". Used in the lang file.
        self.variant_key = f"{mod_id}_{name.lower().replace(' ', '_')}"  # e.g. "byg_ametrine"
        self.versions = versions
        # Double, single, sword
        self.modular_types = modular_types
        self.durability = int(durability)
        self.durability_multiplier = float(durability_multiplier)
        self.integrity_cost = int(integrity_cost)
        # A single string
        self.tint = tint
        # A list of strings
        self.textures = textures
        # A list of Traits
        self.attributes = attributes
        # A list of Traits
        self.effects = effects
        # A list of ToolBoosts
        self.tool_level_boost = int(tool_level) if tool_level else 0
        self.tool_efficiency_boost = float(tool_efficiency) if tool_efficiency else 0
        self.craft_with_tag = item.startswith("tag!")
        self.item = item.removeprefix("tag!")
        self.xp_cost = int(xp_cost)
        pass

    @classmethod
    # Generates a Socket from a CSV row
    def create_from_csv(cls, csv_row):
        # print("Creating a socket from a CSV row")
        if len(csv_row) != 16:
            raise ValueError(
                f"Failed attempt to create a socket because csv row was wrong size ({len(csv_row)}): '{csv_row}'")

        name, mod_id, lang_name, versions, modular_types, durability, durability_multiplier, integrity, tint, textures, \
            attributes, effects, tool_level_boost, tool_efficiency_boost, item, xp_cost = csv_row

        versions, modular_types, textures = versions.split(", "), modular_types.split(", "), textures.split(", ")
        new_attributes = gen_traits_from_string(attributes)
        new_effects = gen_traits_from_string(effects)
        new_versions = [MinecraftVersion.get_version(int(ver)) for ver in versions]
        new_modular_types = [ModularType(x) for x in modular_types]

        soc = Socket(name, mod_id, lang_name, new_versions, new_modular_types, durability, durability_multiplier,
                     integrity, tint, textures, new_attributes, new_effects, tool_level_boost, tool_efficiency_boost,
                     item, xp_cost)
        return soc

    @classmethod
    # Generates a Socket from a JSON object
    # Specifically an old-format JSON object
    def create_socket_from_old_jsons(cls, json_object, lang_file, schematic_file, version):

        if version.value > 18:
            raise ValueError("Tried to use old socket-from-json method in version 1.19 or newer")

        schematic_object = find_schematic(json_object, schematic_file)

        material_block = schematic_object["material"]
        if "tag" in material_block.keys():
            mod_item = material_block["tag"]
        elif version == MinecraftVersion.SIXTEEN:
            mod_item = material_block["item"]
        else:
            mod_item = material_block["items"][0]

        socket_type, name = json_object["key"].split("/")
        mod_id, item = mod_item.removeprefix("tag!").split(":")
        if "tag" in material_block.keys():
            item = "tag!" + item

        lang_opened = open(lang_file)
        lang = json.load(lang_opened)
        lang_name = "Nameless Socket"
        if f"tetra.variant.sword_socket/{name}" in lang.keys():
            lang_name = lang[f"tetra.variant.sword_socket/{name}"]
        elif f"tetra.variant.double_socket/{name}" in lang.keys():
            lang_name = lang[f"tetra.variant.double_socket/{name}"]
        elif f"tetra.variant.single_socket/{name}" in lang.keys():
            lang_name = lang[f"tetra.variant.single_socket/{name}"]

        ver = str(version.value)

        modular_types = ""
        match socket_type:
            case "double_socket":
                modular_types = "double"
            case "single_socket":
                modular_types = "single"
            case "sword_socket":
                modular_types = "sword"

        durability = json_object["durability"] if "durability" in json_object.keys() else 0
        durability_multiplier = json_object["durabilityMultiplier"]\
            if "durabilityMultiplier" in json_object.keys() else 1
        integrity_cost = -1*int(json_object["integrity"]) if "integrity" in json_object.keys() else 0
        tint = json_object["glyph"]["tint"] if "glyph" in json_object.keys() else ""
        textures = "default"
        attributes = json_object["attributes"] if "attributes" in json_object.keys() else {}
        effects = json_object["effects"] if "effects" in json_object.keys() else {}
        tool_boosts = json_object["tools"] if "tools" in json_object.keys() else {}
        xp_cost = schematic_object["experienceCost"]

        new_attributes = [f"att {x} 0 {y}" for x, y in attributes.items()]
        newer_attributes = ", ".join(new_attributes)

        new_effects = []
        for x, y in effects.items():
            if isinstance(y, list):
                new_effects.append(f"eff {x} {y[0]} {y[1]}")
            else:
                new_effects.append(f"eff {x} {y} 0")
        newer_effects = ", ".join(new_effects)

        boost = list(tool_boosts.values())[0]
        tool_level_boost, tool_efficiency_boost = boost[0], boost[1]

        fake_csv_row = [name, mod_id, lang_name, ver, modular_types, durability, durability_multiplier, integrity_cost,
                        tint, textures, newer_attributes, newer_effects, tool_level_boost, tool_efficiency_boost, item, xp_cost]

        output = Socket.create_from_csv(fake_csv_row)

        return output

    @classmethod
    # Generates a Socket from a socket material file
    def create_socket_from_new_json(cls, json_file, lang_file, version):

        if version.value < 19:
            raise ValueError("Attempted to create a socket for a pre-1.19 version using the new-format method")

        mat_opened = open(json_file)
        material = json.load(mat_opened)
        lang_opened = open(lang_file)
        lang = json.load(lang_opened)

        if "models" in material.keys():
            raise ValueError("Attempted to create socket from an old-format JSON with the new-format method")

        tag = False
        material_block = material["material"]
        if "tag" in material_block.keys():
            tag = True
            mod_item = material_block["tag"]
        else:
            mod_item = material_block["items"][0]
        mod_id, item_id = mod_item.split(":")
        if tag:
            item_id = f"tag!{item_id}"

        name = material["key"].removeprefix(f"socket_{mod_id}_")

        ver = str(version.value)

        lang_name = lang[f"tetra.material.socket_{mod_id}_{name}"]

        modular_types = "double, single, sword"

        durability = material["durability"] if "durability" in material.keys() else 0

        durability_multiplier = 1

        integrity = material["integrityCost"] if "integrityCost" in material.keys() else 1

        tint = material["tints"]["glyph"]

        textures = ", ".join(material["textures"]) if "textures" in material.keys() else ""

        attributes = material["attributes"] if "attributes" in material.keys() else {}
        new_attributes = [f"att {x} 0 {y}" for x, y in attributes.items()]
        newer_attributes = ", ".join(new_attributes)

        effects = material["effects"] if "effects" in material.keys() else {}
        new_effects = []
        for x, y in effects.items():
            if isinstance(y, list):
                new_effects.append(f"eff {x} {y[0]} {y[1]}")
            else:
                new_effects.append(f"eff {x} {y} 0")
        newer_effects = ", ".join(new_effects)

        tool_level_boost = material["toolLevel"] if "toolLevel" in material.keys() else 0

        tool_efficiency_boost = material["toolEfficiency"] if "toolLevel" in material.keys() else 0

        xp_cost = material["experienceCost"]

        fake_csv_row = [name, mod_id, lang_name, ver, modular_types, durability, durability_multiplier, integrity,
                        tint, textures, newer_attributes, newer_effects, tool_level_boost, tool_efficiency_boost, item_id, xp_cost]

        return Socket.create_from_csv(fake_csv_row)

    # Compares the Socket to an original.
    def compare_to_original(self, json_object, legacy, mod_type):
        print(f"Comparing replacement of socket {self.name}...")
        jsonified = self.get_socket_json(legacy, mod_type)
        print("Difference between self and original:")
        print(diff(json_object, jsonified))
        print("Saving and restoring from CSV...")
        csvified = self.get_csv_row()
        restored = Socket.create_from_csv(csvified)
        restored_json = restored.get_socket_json(legacy, mod_type)
        print("Difference between restored and originally created:")
        print(diff(jsonified, restored_json))

    # Generates a string formatted for printing
    def get_print_string(self):
        return f'''
        Socket: '{self.name}' from mod '{self.mod_id}'. Module key: '{self.variant_key}', Lang Name: '{self.colored_string}'.
        Versions: {[ver.get_print_string() for ver in self.versions]}.
        Tool types: {[modtype.name for modtype in self.modular_types]}.
        Base Stats: Durability {self.durability}, Durability Multiplier {self.durability_multiplier}.
        Integrity: {self.integrity_cost}.
        Visual: Tint '{self.tint}'
        Effects: {[eff.get_print_string() for eff in self.effects]}.
        Attributes: {[att.get_print_string() for att in self.attributes]}
        Tool Boosts: +{self.tool_level_boost} level, +{self.tool_efficiency_boost} efficiency
        Crafting: {self.mod_id}:{self.item}, {self.xp_cost} levels
        '''

    # Generates a JSON object
    def get_socket_json(self, version, mod_type):
        # For 1.16 and 1.18, designed to go in a modules file.
        if version in [MinecraftVersion.SIXTEEN, MinecraftVersion.EIGHTEEN]:
            legacy = version == MinecraftVersion.SIXTEEN

            output = OrderedDict()
            output["key"] = f"{mod_type.value}_socket/{self.variant_key}"
            output["category"] = "gem"
            if self.durability != 0:
                output["durability"] = self.durability
            if self.durability_multiplier != 1:
                output["durabilityMultiplier"] = self.durability_multiplier
            if self.integrity_cost != 0:
                output["integrity"] = self.integrity_cost
            if self.attributes:
                att_dict = OrderedDict()
                for x in self.attributes:
                    att_dict[f"{x.name}"] = x.efficiency
                output["attributes"] = att_dict
            if self.effects:
                eff_dict = OrderedDict()
                for x in self.effects:
                    if x.efficiency != 0:
                        eff_dict[f"{x.name}"] = [x.level, x.efficiency]
                    else:
                        eff_dict[f"{x.name}"] = x.level
                output["effects"] = eff_dict
            if self.tool_level_boost or self.tool_efficiency_boost:
                tool_dict = OrderedDict()
                for tooltype in ToolType:
                    tool_dict[f"{tooltype}"] = [self.tool_level_boost, self.tool_efficiency_boost]
                output["tools"] = tool_dict

            glyph = OrderedDict()
            if self.tint:
                glyph["tint"] = self.tint
                glyph["textureX"] = 80
                glyph["textureY"] = 16
                output["glyph"] = glyph

                location = ""
                match mod_type:
                    case ModularType.SWORD:
                        location = "tetra:items/module/sword/guard/socket/default"
                    case ModularType.DOUBLE:
                        location = "tetra:items/module/double/binding/socket/default"
                    case ModularType.SINGLE:
                        location = "tetra:items/module/single/binding/socket/default"
                model = OrderedDict()
                model["location"] = location
                model["tint"] = self.tint
                output["models"] = [model]

            return output

        # For 1.19 and 1.20, creates a material.
        else:
            output = OrderedDict()

            output["key"] = f"socket_{self.variant_key}"
            output["hidden"] = True
            output["category"] = "socket"
            output["primary"] = 0
            output["secondary"] = 0
            output["tertiary"] = 0
            output["durability"] = self.durability * self.durability_multiplier
            output["integrityCost"] = self.integrity_cost
            output["integrityGain"] = 0
            output["magicCapacity"] = 0
            output["toolLevel"] = self.tool_level_boost
            output["toolEfficiency"] = self.tool_efficiency_boost

            # Attributes
            if self.attributes:
                att_dict = OrderedDict()
                for x in self.attributes:
                    att_dict[f"{x.name}"] = x.efficiency
                output["attributes"] = att_dict

            # Effects
            if self.effects:
                eff_dict = OrderedDict()
                for x in self.effects:
                    if x.efficiency != 0:
                        eff_dict[f"{x.name}"] = [x.level, x.efficiency]
                    else:
                        eff_dict[f"{x.name}"] = x.level
                output["effects"] = eff_dict

            # Tints
            tints_dict = OrderedDict()
            tints_dict["glyph"] = self.tint
            tints_dict["texture"] = self.tint
            output["tints"] = tints_dict

            # Textures (add textures to socket?)
            output["textures"] = [x for x in self.textures]

            output["experienceCost"] = self.xp_cost
            material_dict = OrderedDict()
            material_dict["items"] = [f"{self.mod_id}:{self.item}"]
            output["material"] = material_dict

            return output

    # Generates a JSON object to go in a schematic JSON file
    def get_schematic_json(self, legacy, mod_type):

        if mod_type not in self.modular_types:
            raise ValueError(f"Illegally tried to create a {mod_type.name} schematic for {self.name} socket'")

        output = OrderedDict()

        if self.craft_with_tag:
            output["material"] = {"tag": f"{self.mod_id}:{self.item}"}
        elif legacy:
            output["material"] = {"item": f"{self.mod_id}:{self.item}"}
        else:
            output["material"] = {"items": [f"{self.mod_id}:{self.item}"]}

        output["experienceCost"] = self.xp_cost
        output["moduleKey"] = f"{mod_type.value}/socket"
        output["moduleVariant"] = f"{mod_type.value}_socket/{self.variant_key}"

        # print(json.dumps(output, indent=4))

        return output

    # Generates the lang lines for a socket. Returns them as a list.
    def get_socket_lang_lines(self, post_119):
        lines = []
        if post_119:
            lines.append(f'''"tetra.material.socket_{self.variant_key}": "{self.name} socket"''')
            lines.append(f'''"tetra.material.socket_{self.variant_key}.prefix": "{self.colored_string}"''')
        else:
            for modular_type in self.modular_types:
                lines.append(f'''"tetra.variant.{modular_type.value}_socket/{self.variant_key}": "Socket [{self.colored_string}]"''')

        return lines

    # Generates a CSV row
    def get_csv_row(self):

        att = get_traits_csv_string(self.attributes)
        eff = get_traits_csv_string(self.effects)
        vers = get_versions_csv_string(self.versions)
        mods = ", ".join([x.value for x in self.modular_types])
        texts = ", ".join(self.textures)

        output = [self.name, self.mod_id, self.colored_string, vers, mods,
                  self.durability, self.durability_multiplier, self.integrity_cost, self.tint, texts,
                  att, eff, self.tool_level_boost, self.tool_efficiency_boost, self.item, self.xp_cost]

        return output

    # Checks whether it matches another socket
    def matches(self, other_socket, verbose=False):
        match = True
        unmatches = []
        if self.name != other_socket.name:
            unmatches.append("name")
            match = False
        if self.mod_id != other_socket.mod_id:
            unmatches.append("mod ID")
            match = False
        if self.colored_string != other_socket.colored_string:
            unmatches.append("colored_string")
            match = False
        if self.durability != other_socket.durability:
            unmatches.append("durability")
            match = False
        if self.durability_multiplier != other_socket.durability_multiplier:
            unmatches.append("durability_multiplier")
            match = False
        if self.integrity_cost != other_socket.integrity_cost:
            unmatches.append("integrity")
            match = False
        if self.tint != other_socket.tint:
            unmatches.append("tint")
            match = False
        if get_traits_csv_string(self.attributes) != get_traits_csv_string(other_socket.attributes):
            unmatches.append("attributes")
            match = False
        if get_traits_csv_string(self.effects) != get_traits_csv_string(other_socket.effects):
            unmatches.append("effects")
            match = False
        if self.tool_level_boost != other_socket.tool_level_boost:
            unmatches.append("tool level boost")
            match = False
        if self.tool_efficiency_boost != other_socket.tool_efficiency_boost:
            unmatches.append("tool efficiency boost")
            match = False
        if self.item != other_socket.item:
            unmatches.append("item")
            match = False
        if self.xp_cost != other_socket.xp_cost:
            unmatches.append("XP cost")
            match = False

        if match:
            if verbose:
                print(f"{self.name} socket matches {other_socket.name} socket")
            return True
        else:
            if verbose:
                print(
                    f"{self.name} socket does not match {other_socket.name} socket: mismatched {', '.join(unmatches)}")
            return False

    # Incorporates a second socket's versions and modular types
    def assimilate(self, other_socket):
        if not self.matches(other_socket):
            raise ValueError(f"Can't assimilate {self.name} and {other_socket.name}, no match detected")

        self.versions = list(set(self.versions + other_socket.versions))
        self.modular_types = list(set(self.modular_types + other_socket.modular_types))


# Generates a bunch of sockets from a JSON file
def gen_sockets_from_json(json_file, lang_file, schematic_file, version):
    socks = open(json_file)
    socs = json.load(socks)
    sockets = []
    for x in socs["variants"]:
        sockets.append(Socket.create_socket_from_old_jsons(x, lang_file, schematic_file, version))
    return sockets


# Returns the schematic JSON object matching a particular socket
def find_schematic(socket_json_object, schematic_file):
    key = socket_json_object["key"]
    schem = open(schematic_file)
    schematics = json.load(schem)
    for schematic in schematics["outcomes"]:
        if schematic["moduleVariant"] == key:
            return schematic


# Generates a full JSON file given a modular item type and a list of Socket objects
def generate_sockets_json(list_of_sockets, version, mod_type):
    output = OrderedDict()
    output["replace"] = False
    output["variants"] = [x.get_socket_json(version, mod_type) for x in list_of_sockets]
    return output


# Generates a full schematics JSON file given a list of sockets
def generate_schematics_json(list_of_sockets, legacy, mod_type):
    output = OrderedDict()
    output["replace"] = False
    output["outcomes"] = [x.get_schematic_json(legacy, mod_type) for x in list_of_sockets]
    return output


class ModularType(Enum):
    DOUBLE = "double"
    SINGLE = "single"
    SWORD = "sword"


def test():
    sixteen_double_sockets = "../../resources/Tetranomicon 1.16/data/tetra/modules/double/socket.json"
    sixteen_lang = "../../resources/Tetranomicon 1.16/assets/tetranomicon/lang/en_us.json"
    sixteen_schematics = "../../resources/Tetranomicon 1.16/data/tetra/schematics/double/socket.json"

    # sockets = gen_sockets_from_json(sixteen_double_sockets, sixteen_lang, sixteen_schematics, MinecraftVersion.SIXTEEN)
    #
    # output_json = generate_sockets_json(sockets, False, ModularType.DOUBLE)
    # # print(json.dumps(output_json, indent=4))
    # schematics_json = generate_schematics_json(sockets, True, ModularType.DOUBLE)
    # print(json.dumps(schematics_json, indent=4))

    socks = open(sixteen_double_sockets)
    socs = json.load(socks)
    for og_json in socs["variants"]:
        socket_object = Socket.create_socket_from_old_jsons(og_json, sixteen_lang, sixteen_schematics,
                                                            MinecraftVersion.SIXTEEN)
        socket_object.compare_to_original(og_json, True, ModularType.DOUBLE)
        print("\n\n")

    # for socket in sockets:
    #     print(json.dumps(socket.get_schematic_json_object(True, ModularType.DOUBLE), indent=4))

    pass


if __name__ == "__main__":
    main()
