from collections import OrderedDict
from enum import Enum
import json

from jsondiff import diff

from classes.mc_version import MinecraftVersion, get_versions_csv_string
from classes.tool_boost import ToolType, create_boosts_from_csv
from classes.trait import gen_traits_from_string, get_traits_csv_string


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
    def __init__(self, name, mod_id, lang_name, versions, modular_types, durability, durability_multiplier,
                 integrity, tint, attributes, effects, tool_boosts, item, xp_cost):
        self.name = name  # e.g. "ametrine"
        self.mod_id = mod_id.lower()  # e.g. "byg"
        self.lang_name = lang_name  # e.g. "Socket [§9Blue Geode§r]"
        self.variant_key = f"{mod_id}_{name.lower()}"
        self.versions = versions
        # Double, single, sword
        self.modular_types = modular_types
        self.durability = int(durability)
        self.durability_multiplier = float(durability_multiplier)
        self.integrity = int(integrity)
        # A single string
        self.tint = tint
        # A list of Traits
        self.attributes = attributes
        # A list of Traits
        self.effects = effects
        # A list of ToolBoosts
        self.tool_boosts = tool_boosts
        self.craft_with_tag = item.startswith("tag!")
        self.item = item.removeprefix("tag!")
        self.xp_cost = int(xp_cost)
        pass

    @classmethod
    # Generates a Socket from a CSV row
    def create_from_csv(cls, csv_row):
        # print("Creating a socket from a CSV row")
        if len(csv_row) != 14:
            raise ValueError(
                f"Failed attempt to create a socket because csv row was wrong size ({len(csv_row)}): '{csv_row}'")

        name, mod_id, lang_name, versions, modular_types, durability, durability_multiplier, integrity, tint, \
            attributes, effects, tool_boosts, item, xp_cost = csv_row

        versions, modular_types = versions.split(", "), modular_types.split(", ")
        new_attributes = gen_traits_from_string(attributes)
        new_effects = gen_traits_from_string(effects)
        new_tool_boosts = create_boosts_from_csv(tool_boosts)
        new_versions = [MinecraftVersion.get_version(int(ver)) for ver in versions]
        new_modular_types = [ModularType(x) for x in modular_types]

        soc = Socket(name, mod_id, lang_name, new_versions, new_modular_types, durability, durability_multiplier,
                     integrity, tint, new_attributes, new_effects, new_tool_boosts, item, xp_cost)
        return soc

    @classmethod
    # Generates a Socket from a JSON object
    def create_from_json(cls, json_object, lang_file, schematic_file, version):
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
        durability_multiplier = json_object[
            "durabilityMultiplier"] if "durabilityMultiplier" in json_object.keys() else 1
        integrity = json_object["integrity"] if "integrity" in json_object.keys() else 0
        tint = json_object["glyph"]["tint"] if "glyph" in json_object.keys() else ""
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

        new_tools = []
        for x, y in tool_boosts.items():
            new_tools.append(f"{x} {y[0]} {y[1]}")
        newer_tools = ", ".join(new_tools)

        # print(f"newer_tools: {newer_tools}")

        fake_csv_row = [name, mod_id, lang_name, ver, modular_types, durability, durability_multiplier, integrity,
                        tint, newer_attributes, newer_effects, newer_tools, item, xp_cost]

        output = Socket.create_from_csv(fake_csv_row)
        # legacy = version == MinecraftVersion.SIXTEEN
        # mod_type = ModularType(modular_types)
        # output_json = output.get_json(legacy, mod_type)
        # print("Generated socket from JSON. Differences:")
        # print(diff(json_object, output_json))

        return output

    # Compares the Socket to an original.
    def compare_to_original(self, json_object, legacy, mod_type):
        print(f"Comparing replacement of socket {self.name}...")
        jsonified = self.get_json(legacy, mod_type)
        print("Difference between self and original:")
        print(diff(json_object, jsonified))
        print("Saving and restoring from CSV...")
        csvified = self.get_csv_row()
        restored = Socket.create_from_csv(csvified)
        restored_json = restored.get_json(legacy, mod_type)
        print("Difference between restored and originally created:")
        print(diff(jsonified, restored_json))

    # Generates a string formatted for printing
    def get_print_string(self):
        return f'''
        Socket: '{self.name}' from mod '{self.mod_id}'. Module key: '{self.variant_key}', Lang Name: '{self.lang_name}'.
        Versions: {[ver.get_print_string() for ver in self.versions]}.
        Tool types: {[modtype.name for modtype in self.modular_types]}.
        Base Stats: Durability {self.durability}, Durability Multiplier {self.durability_multiplier}.
        Integrity: {self.integrity}.
        Visual: Tint '{self.tint}'
        Effects: {[eff.get_print_string() for eff in self.effects]}.
        Attributes: {[att.get_print_string() for att in self.attributes]}
        Tool Boosts: {[boost.get_print_string() for boost in self.tool_boosts]}
        Crafting: {self.mod_id}:{self.item}, {self.xp_cost} levels
        '''

    # Generates a JSON object
    def get_json(self, legacy, mod_type):
        output = OrderedDict()
        output["key"] = f"{mod_type.value}_socket/{self.variant_key}"
        output["category"] = "gem"
        if self.durability != 0:
            output["durability"] = self.durability
        if self.durability_multiplier != 1:
            output["durabilityMultiplier"] = self.durability_multiplier
        if self.integrity != 0:
            output["integrity"] = self.integrity
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
        if self.tool_boosts:
            tool_dict = OrderedDict()
            for boost in self.tool_boosts:
                if boost.tool_type in mod_type.get_relevant_tools():
                    name = boost.tool_type.value if legacy else boost.tool_type.modern_name()
                    tool_dict[f"{name}"] = [boost.level, boost.efficiency]
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

    # Generates the lang lines for a socket. Returns them as an OrderedDict.
    def get_lang_lines(self):
        lines = OrderedDict()
        for modular_type in self.modular_types:
            lines[f"tetra.variant.{modular_type.name}_socket/{self.variant_key}"] = f"{self.lang_name}"
        return lines

    # Generates a CSV row
    def get_csv_row(self):

        att = get_traits_csv_string(self.attributes)
        eff = get_traits_csv_string(self.effects)
        boost = ", ".join([x.get_csv_string() for x in self.tool_boosts])
        vers = get_versions_csv_string(self.versions)
        mods = ", ".join([x.value for x in self.modular_types])

        output = [self.name, self.mod_id, self.lang_name, vers, mods,
                  self.durability, self.durability_multiplier, self.integrity, self.tint,
                  att, eff, boost, self.item, self.xp_cost]

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
        if self.lang_name != other_socket.lang_name:
            unmatches.append("lang name")
            match = False
        if self.durability != other_socket.durability:
            unmatches.append("durability")
            match = False
        if self.durability_multiplier != other_socket.durability_multiplier:
            unmatches.append("durability_multiplier")
            match = False
        if self.integrity != other_socket.integrity:
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
        if ", ".join([x.get_csv_string() for x in self.tool_boosts]) != ", ".join(
                [x.get_csv_string() for x in other_socket.tool_boosts]):
            unmatches.append("tool boosts")
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
        sockets.append(Socket.create_from_json(x, lang_file, schematic_file, version))
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
def generate_sockets_json(list_of_sockets, legacy, mod_type):
    output = OrderedDict()
    output["replace"] = False
    output["variants"] = [x.get_json(legacy, mod_type) for x in list_of_sockets]
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

    def get_relevant_tools(self):
        match self:
            case ModularType.DOUBLE:
                return [ToolType.AXE, ToolType.HOE, ToolType.PICKAXE]
            case ModularType.SINGLE:
                return [ToolType.SHOVEL]
            case ModularType.SWORD:
                return [ToolType.CUT]


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
        socket_object = Socket.create_from_json(og_json, sixteen_lang, sixteen_schematics, MinecraftVersion.SIXTEEN)
        socket_object.compare_to_original(og_json, True, ModularType.DOUBLE)
        print("\n\n")

    # for socket in sockets:
    #     print(json.dumps(socket.get_schematic_json_object(True, ModularType.DOUBLE), indent=4))

    pass


if __name__ == "__main__":
    main()
