from enum import Enum

from classes.mc_version import MinecraftVersion, get_versions_csv_string
from classes.tool_boost import ToolBoost, ToolType
from classes.trait import gen_traits_from_string, get_traits_json_block, get_traits_csv_string


def main():
    # test()
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
        self.item = item
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
        new_tool_boosts = ToolBoost.create_from_csv(tool_boosts)
        new_versions = [MinecraftVersion.get_version(int(ver)) for ver in versions]
        new_modular_types = [ModularType(x) for x in modular_types]

        soc = Socket(name, mod_id, lang_name, new_versions, new_modular_types, durability, durability_multiplier,
                     integrity, tint, new_attributes, new_effects, new_tool_boosts, item, xp_cost)
        return soc

    @classmethod
    # Generates a Socket from a JSON object
    def create_from_json(cls, json_object):
        pass

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
        {self.tool_boosts.get_print_string()}
        Crafting: {self.mod_id}:{self.item}, {self.xp_cost} levels
        '''

    # Generates a block to go in a JSON
    def get_json_block(self, legacy, mod_type):
        if mod_type not in self.modular_types:
            raise ValueError(f"Illegally tried to create a {mod_type.name} block for {self.name} socket'")

        durability_block = f'''"durability": {self.durability},''' if (self.durability != 0) else ""
        durability_multiplier_block = f'''\n            "durabilityMultiplier": {self.durability_multiplier},\n'''\
            if (self.durability_multiplier != 0) else ""
        integrity_block = f'''\n            "integrity": {self.integrity},\n''' if (self.integrity != 0) else ""

        location = ""
        match mod_type:
            case ModularType.SWORD:
                location = "tetra:items/module/sword/guard/socket/default"
            case ModularType.DOUBLE:
                location = "tetra:items/module/double/binding/socket/default"
            case ModularType.SINGLE:
                location = "tetra:items/module/single/binding/socket/default"

        return f'''{{
            "key": "{mod_type}_socket/{self.variant_key}",
            "category": "gem",
            {durability_block}{durability_multiplier_block}{integrity_block}{get_traits_json_block(self.attributes)}{get_traits_json_block(self.effects)}{self.tool_boosts.get_json_block(legacy, mod_type.get_relevant_tools())}
            "glyph": {{
                "tint": "{self.tint}",
                "textureX": 80,
                "textureY": 16
            }},
            "models": [{{
                "location": "{location}",
                "tint": "{self.tint}"
            }}]
        }}'''

    # Generates a block to go in a schematic JSON
    def get_schematic_json_block(self, legacy, mod_type):
        if mod_type not in self.modular_types:
            raise ValueError(f"Illegally tried to create a {mod_type.name} schematic for {self.name} socket'")

        modern_output = f'''{{
        "material": {{
            "item": "{self.mod_id}:{self.item}"
            }},
        "experienceCost": {self.xp_cost},
        "moduleKey": "{mod_type.name}/socket",
        "moduleVariant": "{mod_type.name}_socket/{self.variant_key}"
    }}'''
        legacy_output = f'''{{
        "material": {{
            "items": [ "{self.mod_id}:{self.item}" ]
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
def gen_sockets_from_json(json_file):
    pass


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
    pass


if __name__ == "__main__":
    main()
