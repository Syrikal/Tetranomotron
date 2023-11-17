from enum import Enum
import json

from classes.mc_version import MinecraftVersion, get_versions_csv_string
from classes.tool_boost import ToolType, create_boosts_from_csv, get_tool_boost_json_block
from classes.trait import gen_traits_from_string, get_traits_json_block, get_traits_csv_string


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
        self.mod_id = mod_id.lower()
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
        print("Creating a socket from a CSV row")
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

        modular_types = []
        match socket_type:
            case "double_socket":
                modular_types = "double"
            case "single_socket":
                modular_types = "single"
            case "sword_socket":
                modular_types = "sword"

        durability = json_object["durability"] if "durability" in json_object.keys() else 0
        durability_multiplier = json_object[
            "durabilityMultiplier"] if "durabilityMultiplier" in json_object.keys() else 0
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

        return Socket.create_from_csv(fake_csv_row)

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

    # Generates a block to go in a JSON
    def get_json_block(self, legacy, mod_type):
        if mod_type not in self.modular_types:
            raise ValueError(f"Illegally tried to create a {mod_type.name} block for {self.name} socket'")

        durability_block = f'''"durability": {self.durability}''' if (self.durability != 0) else ""
        durability_multiplier_block = f'''            "durabilityMultiplier": {self.durability_multiplier}''' \
            if (self.durability_multiplier != 0) else ""
        integrity_block = f'''            "integrity": {self.integrity}''' if (self.integrity != 0) else ""

        location = ""
        match mod_type:
            case ModularType.SWORD:
                location = "tetra:items/module/sword/guard/socket/default"
            case ModularType.DOUBLE:
                location = "tetra:items/module/double/binding/socket/default"
            case ModularType.SINGLE:
                location = "tetra:items/module/single/binding/socket/default"

        model_block = ""
        glyph_block = ""
        if self.tint:
            model_block = f'''"models": [{{
                "location": "{location}",
                "tint": "{self.tint}"
            }}]'''
            glyph_block = f'''"glyph": {{
                "tint": "{self.tint}",
                "textureX": 80,
                "textureY": 16
            }}'''

        stat_blocks = ",\n".join([durability_block, durability_multiplier_block, integrity_block, get_tool_boost_json_block(self.tool_boosts, legacy, mod_type.get_relevant_tools())])
        visual_blocks = ",\n".join([glyph_block, model_block])

        output = f'''        {{
            "key": "{mod_type.value}_socket/{self.variant_key}",
            "category": "gem",
            {stat_blocks},
            {get_traits_json_block(self.attributes)}{get_traits_json_block(self.effects)}
            {visual_blocks}
        }}'''
        print(output)

        json_output = json.loads(output)
        new_output = json.dumps(json_output, indent=4)
        return new_output

    # Generates a block to go in a schematic JSON
    def get_schematic_json_block(self, legacy, mod_type):
        if mod_type not in self.modular_types:
            raise ValueError(f"Illegally tried to create a {mod_type.name} schematic for {self.name} socket'")

        material_key = ""
        if self.craft_with_tag:
            material_key = "tag"
        elif legacy:
            material_key = "items"
        else:
            material_key = "item"

        modern_output = f'''{{
        "material": {{
            {material_key}: "{self.mod_id}:{self.item}"
            }},
        "experienceCost": {self.xp_cost},
        "moduleKey": "{mod_type.name}/socket",
        "moduleVariant": "{mod_type.name}_socket/{self.variant_key}"
    }}'''
        legacy_output = f'''{{
        "material": {{
            {material_key}: [ "{self.mod_id}:{self.item}" ]
            }},
        "experienceCost": {self.xp_cost},
        "moduleKey": "{mod_type.name}/socket",
        "moduleVariant": "{mod_type.name}_socket/{self.variant_key}"
    }}'''
        return legacy_output if legacy else modern_output

    # Generates the lang lines for a socket
    def get_lang_lines(self):
        lines = []
        for modular_type in self.modular_types:
            lines.append(f'''"tetra.variant.{modular_type.name}_socket/{self.variant_key}": "{self.lang_name}"''')
        return lines

    # Generates a CSV row
    def get_csv_row(self):

        att = get_traits_csv_string(self.attributes)
        eff = get_traits_csv_string(self.effects)
        boost = self.tool_boosts.get_versions_csv_string
        vers = get_versions_csv_string(self.versions)
        mods = ", ".join([x.name for x in self.modular_types])

        output = [self.name, self.mod_id, self.lang_name, vers, mods,
                  self.durability, self.durability_multiplier, self.integrity, self.tint,
                  att, eff, boost, self.item, self.xp_cost]

        return output


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


# Generates the text for a full JSON file given a modular item type and a list of sockets
def generate_full_json(mod_type, list_of_sockets):
    pass


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

    sockets = gen_sockets_from_json(sixteen_double_sockets, sixteen_lang, sixteen_schematics, MinecraftVersion.SIXTEEN)

    for socket in sockets:
        print(socket.get_print_string())
        print()
        print(socket.get_json_block(True, ModularType.DOUBLE))

    pass


if __name__ == "__main__":
    main()
