class ToolRequirements:
    # Generates a ToolRequirements from three integers
    def __init__(self, hammer, axe, cut):
        self.hammer = hammer
        self.axe = axe
        self.cut = cut

    @classmethod
    # Generates a ToolRequirements from a string, such as from a CSV
    def create_from_csv(cls, tool_string):
        tool_strings = tool_string.split(", ")
        tool_tuples = []
        for tool_string in tool_strings:
            split = tool_string.split(" ")
            if len(split) != 2:
                raise ValueError(f"Attempted to parse {split} as a tool requirement. Aborting.")
            else:
                tool_tuples.append((split[0], split[1]))

        ham, axe, cut = 0, 0, 0
        for tool in tool_tuples:
            # print(f"Parsing {tool[0]}")
            if tool[0] == "hammer":
                # print("Requirement is for hammer")
                ham = int(tool[1])
                continue
            elif tool[0] == "axe":
                # print("Requirement is for axe")
                axe = int(tool[1])
                continue
            elif tool[0] == "cut":
                # print("Requirement is for cut")
                cut = int(tool[1])
                continue
            else:
                raise ValueError(f"Attempted to parse {tool} as a tool requirement. Aborting.")

        output = ToolRequirements(ham, axe, cut)
        # print(f"Generated tool requirements: {output.string()}")
        return output

    # Generates a json block for insertion into a material json
    def get_json_block(self, legacy):
        legacy_output = "\n        "
        if self.hammer != 0:
            legacy_output += f'"hammer": {self.hammer},\n        '
        if self.axe != 0:
            legacy_output += f'"axe": {self.axe},\n        '
        if self.cut != 0:
            legacy_output += f'"cut": {self.cut},\n        '

        legacy_output = legacy_output.rstrip().removesuffix(",")

        modern_output = "\n        "
        if self.hammer != 0:
            modern_output += f'"hammer_dig": "{convert_tool_level(self.hammer)}",\n        '
        if self.axe != 0:
            modern_output += f'"axe_dig": "{convert_tool_level(self.axe)}",\n        '
        if self.cut != 0:
            modern_output += f'"cut": "{convert_tool_level(self.cut)}",\n        '

        modern_output = modern_output.rstrip().removesuffix(",")

        return legacy_output if legacy else modern_output

    # Generates a string formatted for printing
    def get_print_string(self):
        return f"Tool Requirement: Hammer {self.hammer}, Axe {self.axe}, Cut {self.cut}"

    # Generates a string formatted for storing in a CSV
    def get_csv_string(self):
        reqs = []
        if self.hammer != 0:
            reqs.append(f"hammer {self.hammer}")
        if self.axe != 0:
            reqs.append(f"axe {self.axe}")
        if self.cut != 0:
            reqs.append(f"cut {self.cut}")
        return ", ".join(reqs)


def convert_tool_level(tool_level_integer):
    match tool_level_integer:
        case 1:
            return "minecraft:wood"
        case 2:
            return "minecraft:stone"
        case 3:
            return "minecraft:iron"
        case 4:
            return "minecraft:diamond"
        case 5:
            return "minecraft:netherite"
        case 6:
            return "tetranomicon:tier_six"
        case 7:
            return "tetranomicon:tier_seven"
