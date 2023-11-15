from classes.mc_version import MinecraftVersion, get_versions_csv_string


def main():
    # test()
    pass


class Replacement:
    # Replacement_Type is axe, hoe, knife, pick, shovel, or sword
    def __init__(self, replacement_type, versions, modid, itemid, material):
        self.replacement_type = replacement_type
        self.versions = [MinecraftVersion.get_version(int(ver)) for ver in versions]
        self.mod_id = modid
        self.item_id = itemid
        self.material_name = material.lower()

    @classmethod
    # Creates a Replacement from a CSV row
    def create_from_csv(cls, csv_row):
        print("Creating a self from a CSV row")
        if len(csv_row) != 5:
            raise ValueError(f"Failed attempt to create a self from csv row because row was wrong size: '{csv_row}'")

        replacement_type, versions, modid, itemid, material_name = csv_row

        # Turn comma-separated lists into actual lists
        versions = versions.split(", ")

        rep = Replacement(replacement_type, versions, modid, itemid, material_name)
        print(f"Generated material from CSV: {rep.get_print_string()}")
        return rep

    @classmethod
    def create_from_json(cls, json_object):
        pass

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
        Replacement of '{self.item_id}' from mod '{self.mod_id}' uses material '{self.mod_id}_{self.material_name}'. Replacement type: {self.replacement_type}.
        Versions: {[ver.get_print_string() for ver in self.versions]}.
        '''

    # Generates a json chunk
    def get_json_block(self, legacy):
        replacement_type = self.replacement_type
        modid = self.mod_id
        itemid = self.item_id
        material_name = self.material_name

        if legacy:
            match replacement_type:
                case "axe":
                    return f'''
                {{
                    "predicate": {{
                        "item": "{modid}:{itemid}"
                    }},
                    "item": "tetra:modular_double",
                    "modules": {{
                        "double/head_left": ["double/basic_axe_left", "basic_axe/{modid}_{material_name}"],
                        "double/head_right": ["double/butt_right", "butt/{modid}_{material_name}"],
                        "double/handle": ["double/basic_handle", "basic_handle/stick"]
                    }}
                }},'''

                case "hoe":
                    return f'''
                {{
                    "predicate": {{
                        "item": "{modid}:{itemid}"
                    }},
                    "item": "tetra:modular_double",
                    "modules": {{
                        "double/head_left": ["double/hoe_left", "hoe/{modid}_{material_name}"],
                        "double/head_right": ["double/butt_right", "butt/{modid}_{material_name}"],
                        "double/handle": ["double/basic_handle", "basic_handle/stick"]
                    }}
                }},'''

                case "knife":
                    return f'''
                {{
                    "predicate": {{
                        "item": "{modid}:{itemid}"
                    }},
                    "item": "tetra:modular_sword",
                    "modules": {{
                        "sword/blade": ["sword/short_blade", "short_blade/{modid}_{material_name}"],
                        "sword/hilt": ["sword/basic_hilt", "basic_hilt/stick"]
                    }}
                }},'''

                case "pick":
                    return f'''
                {{
                    "predicate": {{
                        "item": "{modid}:{itemid}"
                    }},
                    "item": "tetra:modular_double",
                    "modules": {{
                        "double/head_left": ["double/basic_pickaxe_left", "basic_pickaxe/{modid}_{material_name}"],
                        "double/head_right": ["double/basic_pickaxe_right", "basic_pickaxe/{modid}_{material_name}"],
                        "double/handle": ["double/basic_handle", "basic_handle/stick"]
                    }}
                }},'''

                case "shovel":
                    return f'''
                {{
                    "predicate": {{
                        "item": "{modid}:{itemid}"
                    }},
                    "item": "tetra:modular_single",
                    "modules": {{
                        "single/head": ["single/basic_shovel", "basic_shovel/{modid}_{material_name}"],
                        "single/handle": ["single/basic_handle", "basic_handle/stick"]
                    }}
                }},'''

                case "sword":
                    return f'''
                {{
                    "predicate": {{
                        "item": "{modid}:{itemid}"
                    }},
                    "item": "tetra:modular_sword",
                    "modules": {{
                        "sword/blade": ["sword/basic_blade", "basic_blade/{modid}_{material_name}"],
                        "sword/hilt": ["sword/basic_hilt", "basic_hilt/stick"],
                        "sword/pommel": ["sword/decorative_pommel", "decorative_pommel/{modid}_{material_name}"],
                        "sword/guard": ["sword/makeshift_guard", "makeshift_guard/{modid}_{material_name}"]
                    }}
                }},'''

            raise TypeError(
                f"Invalid type! Attempted to generate legacy replacement block with arguments: [{replacement_type}, {modid}, {itemid}, {material_name}]")

        else:
            match replacement_type:
                case "axe":
                    return f'''
                {{
                    "predicate": {{
                        "items": [ "{modid}:{itemid}" ]
                    }},
                    "item": "tetra:modular_double",
                    "modules": {{
                        "double/head_left": ["double/basic_axe_left", "basic_axe/{modid}_{material_name}"],
                        "double/head_right": ["double/butt_right", "butt/{modid}_{material_name}"],
                        "double/handle": ["double/basic_handle", "basic_handle/stick"]
                    }}
                }}, '''

                case "hoe":
                    return f'''
                {{
                    "predicate": {{
                        "items": [ "{modid}:{itemid}" ]
                    }},
                    "item": "tetra:modular_double",
                    "modules": {{
                        "double/head_left": ["double/hoe_left", "hoe/{modid}_{material_name}"],
                        "double/head_right": ["double/butt_right", "butt/{modid}_{material_name}"],
                        "double/handle": ["double/basic_handle", "basic_handle/stick"]
                    }}
                }}, '''

                case "knife":
                    return f'''
                {{
                    "predicate": {{
                        "items": [ "{modid}:{itemid}" ]
                    }},
                    "item": "tetra:modular_sword",
                    "modules": {{
                        "sword/blade": ["sword/short_blade", "short_blade/{modid}_{material_name}"],
                        "sword/hilt": ["sword/basic_hilt", "basic_hilt/stick"]
                    }}
                }}, '''

                case "pick":
                    return f'''
                {{
                    "predicate": {{
                        "items": [ "{modid}:{itemid}" ]
                    }},
                    "item": "tetra:modular_double",
                    "modules": {{
                        "double/head_left": ["double/basic_pickaxe_left", "basic_pickaxe/{modid}_{material_name}"],
                        "double/head_right": ["double/basic_pickaxe_right", "basic_pickaxe/{modid}_{material_name}"],
                        "double/handle": ["double/basic_handle", "basic_handle/stick"]
                    }}
                }}, '''

                case "shovel":
                    return f'''
                {{
                    "predicate": {{
                        "items": [ "{modid}:{itemid}" ]
                    }},
                    "item": "tetra:modular_single",
                    "modules": {{
                        "single/head": ["single/basic_shovel", "basic_shovel/{modid}_{material_name}"],
                        "single/handle": ["single/basic_handle", "basic_handle/stick"]
                    }}
                }}, '''

                case "sword":
                    return f'''
                {{
                    "predicate": {{
                        "items": [ "{modid}:{itemid}" ]
                    }},
                    "item": "tetra:modular_sword",
                    "modules": {{
                        "sword/blade": ["sword/basic_blade", "basic_blade/{modid}_{material_name}"],
                        "sword/hilt": ["sword/basic_hilt", "basic_hilt/stick"],
                        "sword/pommel": ["sword/decorative_pommel", "decorative_pommel/{modid}_{material_name}"],
                        "sword/guard": ["sword/makeshift_guard", "makeshift_guard/{modid}_{material_name}"]
                    }}
                }}, '''

            raise TypeError(
                f"Invalid type! Attempted to generate modern replacement block with arguments: [{replacement_type}, {modid}, {itemid}, {material_name}]")

    # Generates a CSV row
    def get_csv_row(self):
        return [self.replacement_type, get_versions_csv_string(self.versions), self.mod_id, self.item_id,
                self.material_name]


# Generates a bunch of replacements from a JSON file
def gen_replacements_from_json(json_file):
    pass


def test():
    pass


if __name__ == "__main__":
    main()
