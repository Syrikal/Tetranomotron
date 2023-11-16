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
            if tool[0] == "hammer" or tool[0] == "hammer_dig":
                # print("Requirement is for hammer")
                ham = int(tool[1])
                continue
            elif tool[0] == "axe" or tool[0] == "axe_dig":
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
            modern_output += f'"hammer_dig": "{tool_level_as_string(self.hammer)}",\n        '
        if self.axe != 0:
            modern_output += f'"axe_dig": "{tool_level_as_string(self.axe)}",\n        '
        if self.cut != 0:
            modern_output += f'"cut": "{tool_level_as_string(self.cut)}",\n        '

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


def tool_level_format_swap(input_t_level):
    if isinstance(input_t_level, str):
        # print(f"swapping t_level '{input_t_level}' from string to int")

        output = None
        try:
            output = int(input_t_level)
            # print("Successfully converted directly to int")
        except TypeError:
            # print("Could not convert to int directly")
            pass
        finally:
            if output is not None:
                return output
            match input_t_level:
                case "minecraft:wood":
                    return 1
                case "minecraft:stone":
                    return 2
                case "minecraft:iron":
                    return 3
                case "minecraft:diamond":
                    return 4
                case "minecraft:netherite":
                    return 5
                case "tetranomicon:tier_six":
                    return 6
                case "tetranomicon:six":
                    return 6
                case "tetranomicon:tier_seven":
                    return 7
                case _:
                    raise ValueError(f"Failed to do a tool-level format swap on {input_t_level}")

    elif isinstance(input_t_level, int):
        # print(f"swapping t_level '{input_t_level}' from int to string")
        match input_t_level:
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
            case _:
                raise ValueError(f"Failed to do a tool-level format swap on {input_t_level}")

    else:
        raise TypeError(f"Failed to do a tool-level format swap on {input_t_level}")


def tool_level_as_int(input_t_level):
    # print(f"changing t_level '{input_t_level}' to int")
    if isinstance(input_t_level, int):
        # print("t_level already int")
        return input_t_level
    else:
        # print("t_level in string form, swapping")
        return tool_level_format_swap(input_t_level)


def tool_level_as_string(input_t_level):
    # print(f"changing t_level '{input_t_level}' to string")
    if isinstance(input_t_level, str):
        # print("t_level already string")
        return input_t_level
    else:
        # print("t_level in int form, swapping")
        return tool_level_format_swap(input_t_level)
