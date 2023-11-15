from classes.tool_requirements import ToolRequirements, convert_tool_level
from classes.trait import gen_traits_from_string, get_traits_json_block, get_traits_csv_string
from classes.mc_version import MinecraftVersion, get_versions_csv_string


class Material:
    # Generates a Material from a bunch of inputs.
    # Inputs are strings, except:
    # versions is a list of MinecraftVersions
    # textures is a list of strings
    # effects and improvements are lists of Traits
    # reqtools is a ToolRequirements
    def __init__(self, name, adjective, mod_id, versions, category, primary, secondary, tertiary, durability,
                 integrity_cost, integrity_gain, magic, tool_level, tool_efficiency, tint, texts, item, effects,
                 improvements, reqtools):
        self.name = name  # e.g. "Gold"
        self.prefix = adjective  # e.g. "Golden"
        self.mod_id = mod_id.lower()
        # Material key is used as the 'key' in the material json as well as the json filename
        self.material_key = f"{mod_id}_{name.lower()}"
        # Versions is a list of MinecraftVersions
        self.versions = versions
        # Category is one of fibre, gem, metal, scale, stone, wood
        self.category = category
        self.primary = float(primary)
        self.secondary = float(secondary)
        self.tertiary = float(tertiary)
        self.durability = int(durability)
        self.integrity_cost = int(integrity_cost)
        self.integrity_gain = int(integrity_gain)
        self.magic_capacity = int(magic)
        # Tool level is stored as a number
        self.tool_level = int(tool_level)
        self.tool_efficiency = float(tool_efficiency)
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

    @classmethod
    # Generates a Material from a CSV row
    def create_from_csv(cls, csv_row):
        print("Creating a material from a CSV row")
        if len(csv_row) != 20:
            raise ValueError(f"Failed attempt to create a material because csv row was wrong size ({len(csv_row)}): '{csv_row}'")

        name, adjective, mod_id, versions, category, primary, secondary, tertiary, dur, \
            integrity_cost, integrity_gain, magic, tool_level, tool_efficiency, \
            tint, texts, item, effects, improvements, tool_requirements \
            = csv_row

        # Turn comma-separated lists into lists of strings
        versions, texts = versions.split(", "), texts.split(", ")

        new_effects = gen_traits_from_string(effects)
        new_improvements = gen_traits_from_string(improvements)
        new_tool_requirements = ToolRequirements.create_from_csv(tool_requirements)
        new_versions = [MinecraftVersion.get_version(int(ver)) for ver in versions]

        mat = Material(name, adjective, mod_id, new_versions, category, primary, secondary, tertiary, dur, integrity_cost,
                       integrity_gain, magic, tool_level, tool_efficiency, tint, texts,
                       item, new_effects, new_improvements, new_tool_requirements)
        print(f"Generated material from CSV: {mat.get_print_string()}")
        return mat

    @classmethod
    # Generates a Material from a JSON file
    def create_from_json(cls, json_file):
        pass

    def check_valid(self):
        complaint_string = ""
        valid = True
        # Check whether material key is what it should be
        if self.material_key is not f"{self.mod_id}_{self.name}":
            valid = False
            complaint_string += f"\n      material key '{self.material_key}' does not fit pattern"
        # Check whether category is acceptable
        if self.category not in ["fibre", "gem", "metal", "scale", "stone", "wood"]:
            valid = False
            complaint_string += f"\n      '{self.category}' is not a valid material category"

        if not valid:
            print(f"Material '{self.material_key}' failed verification. Reasons: {complaint_string}")

    # Generates a string formatted for printing
    def get_print_string(self):
        return f'''
        Material: '{self.name}' from mod '{self.mod_id}'. Material key: '{self.material_key}', Material Adjective: '{self.prefix}'.
        Versions: {[ver.get_print_string() for ver in self.versions]}.
        Material category: {self.category}
        Base Stats: Hardness {self.primary}, Density {self.secondary}, Flexibility {self.tertiary}.
        Other Stats: Durability {self.durability}, Integrity cost/gain {self.integrity_cost}/{self.integrity_gain}, Magic Capacity {self.magic_capacity}, Tool Level/Efficiency {self.tool_level}/{self.tool_efficiency}.
        Visual: Tint '{self.tint}', Textures {self.textures}
        Effects: {[eff.get_print_string() for eff in self.effects]}
        Improvements: {[imp.get_print_string() for imp in self.improvements]}
        {self.required_tools.get_print_string()}
        '''

    # Generates the contents of a json file
    def get_json_block(self, legacy):
        textures = "\n        "
        for text in self.textures:
            textures += f'"{text}",\n        '
        textures = textures.rstrip().removesuffix(",")

        modern_output = f'''{{
        "key": "{self.material_key}",
        "category": "{self.category}",
        "primary": {self.primary},
        "secondary": {self.secondary},
        "tertiary": {self.tertiary},
        "durability": {self.durability},
        "integrityCost": {self.integrity_cost},
        "integrityGain": {self.integrity_gain},
        "magicCapacity": {self.magic_capacity},
        "toolLevel": "{convert_tool_level(self.tool_level)}",
        "toolEfficiency": {self.tool_efficiency},
        "tints": {{
            "glyph": "{self.tint}",
            "texture": "{self.tint}"
        }},
        "textures": [{textures}
        ],
        "material": {{
            "items": [ "{self.mod_id}:{self.item}" ]
        }},{get_traits_json_block(self.effects)}{get_traits_json_block(self.improvements)}
        "requiredTools": {{{self.required_tools.get_json_block(False)}
        }}
    }}'''

        legacy_output = f'''{{
        "key": "{self.material_key}",
        "category": "{self.category}",
        "primary": "{self.primary}",
        "secondary": "{self.secondary}",
        "tertiary": "{self.tertiary}",
        "durability": "{self.durability}",
        "integrityCost": "{self.integrity_cost}",
        "integrityGain": "{self.integrity_gain}",
        "magicCapacity": "{self.magic_capacity}",
        "toolLevel": "{self.tool_level}",
        "toolEfficiency": "{self.tool_efficiency}",
        "tints": {{
            "glyph": "{self.tint}",
            "texture": "{self.tint}"
        }},
        "textures": [{textures}
        ],
        "material": {{
            "item": "{self.mod_id}:{self.item}"
        }},{get_traits_json_block(self.effects)}{get_traits_json_block(self.improvements)}
        "requiredTools": {{{self.required_tools.get_json_block(True)}
        }}
    }}'''

        return legacy_output if legacy else modern_output

    # Generates the lang lines for a material (returned as a list, no commas)
    def get_lang_lines(self):
        output = [f'''"tetra.material.{self.material_key}": "{self.name}"''',
                  f'''tetra.material.{self.material_key}.prefix": "{self.prefix}"''']
        return output

    # Generates a CSV row
    def get_csv_row(self):
        vers = get_versions_csv_string(self.versions)
        text = ", ".join(self.textures)
        eff = get_traits_csv_string(self.effects)
        imp = get_traits_csv_string(self.improvements)
        tools = self.required_tools.get_versions_csv_string
        output = [self.name, self.prefix, self.mod_id, vers, self.category,
                  self.primary, self.secondary, self.tertiary, self.durability,
                  self.integrity_cost, self.integrity_gain, self.magic_capacity, self.tool_level, self.tool_efficiency,
                  self.tint, text, self.item,
                  eff, imp, tools]

        return output

    # Returns True if the other material matches this one.
    # Generally used for combining the same material across versions.
    def matches(self, other_material):
        mismatch = False
        unmatches = []

        # Make name not necessarily a match? Adjective too?
        if self.name != other_material.name:
            unmatches.append("name")
            mismatch = True

        if self.prefix != other_material.prefix:
            unmatches.append("adjective")
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
            print(f"{self.name} does not match {other_material.name}: mismatched {', '.join(unmatches)}")
            return False
        else:
            return True

    # Assimilates the other material
    # Should only work if they match!
    def assimilate(self, other_material):
        if not self.matches(other_material):
            raise ValueError(f"Can't assimilate {self.name} and {other_material.name}, no match detected")

        for ver in other_material.versions:
            self.versions.append(ver)
