from collections import OrderedDict
from enum import Enum


class ToolRequirements:
    # Generates a ToolRequirements from three integers
    def __init__(self, hammer, axe, cut):
        self.hammer = ToolLevel(hammer)
        self.axe = ToolLevel(axe)
        self.cut = ToolLevel(cut)

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

    # Generates a JSON dict to be assigned as the value of the "requiredTools" key
    def get_json_object(self, legacy):
        output = OrderedDict()

        if self.hammer != 0:
            if legacy:
                output["hammer"] = self.hammer.get_legacy_int()
            else:
                output["hammer_dig"] = self.hammer.get_modern_string()
        if self.axe != 0:
            if legacy:
                output["axe"] = self.axe.get_legacy_int()
            else:
                output["axe_dig"] = self.axe.get_modern_string()
        if self.cut != 0:
            if legacy:
                output["cut"] = self.cut.get_legacy_int()
            else:
                output["cut"] = self.cut.get_modern_string()

        return output

    # Generates a string formatted for printing
    def get_print_string(self):
        return f"Tool Requirement: Hammer {self.hammer.value}, Axe {self.axe.value}, Cut {self.cut.value}"

    # Generates a string formatted for storing in a CSV
    def get_csv_string(self):
        reqs = []
        if self.hammer != 0:
            reqs.append(f"hammer {self.hammer.value}")
        if self.axe != 0:
            reqs.append(f"axe {self.axe.value}")
        if self.cut != 0:
            reqs.append(f"cut {self.cut.value}")
        return ", ".join(reqs)


# def tool_level_format_swap(input_t_level):
#     if isinstance(input_t_level, str):
#         # print(f"swapping t_level '{input_t_level}' from string to int")
#
#         output = None
#         try:
#             output = int(input_t_level)
#             # print("Successfully converted directly to int")
#         except TypeError:
#             # print("Could not convert to int directly")
#             pass
#         finally:
#             if output is not None:
#                 return output
#             match input_t_level:
#                 case "minecraft:wood":
#                     return 1
#                 case "minecraft:gold":
#                     return 1
#                 case "minecraft:stone":
#                     return 2
#                 case "minecraft:iron":
#                     return 3
#                 case "minecraft:diamond":
#                     return 4
#                 case "minecraft:netherite":
#                     return 5
#                 case "tetranomicon:tier_six":
#                     return 6
#                 case "tetranomicon:six":
#                     return 6
#                 case "tetranomicon:netherite_plus":
#                     return 6
#                 case "tetra:maxed_forge_hammer":
#                     return 6
#                 case "tetranomicon:tier_seven":
#                     return 7
#                 case "tetranomicon:seven":
#                     return 7
#                 case _:
#                     raise ValueError(f"Failed to do a tool-level format swap on {input_t_level}")
#
#     elif isinstance(input_t_level, int):
#         # print(f"swapping t_level '{input_t_level}' from int to string")
#         match input_t_level:
#             case 1:
#                 return "minecraft:wood"
#             case 2:
#                 return "minecraft:stone"
#             case 3:
#                 return "minecraft:iron"
#             case 4:
#                 return "minecraft:diamond"
#             case 5:
#                 return "minecraft:netherite"
#             case 6:
#                 return "tetra:maxed_forge_hammer"
#             case 7:
#                 return "tetranomicon:tier_seven"
#             case _:
#                 raise ValueError(f"Failed to do a tool-level format swap on {input_t_level}")
#
#     else:
#         raise TypeError(f"Failed to do a tool-level format swap on {input_t_level}")
#
#
# def tool_level_as_int(input_t_level):
#     # print(f"changing t_level '{input_t_level}' to int")
#     if isinstance(input_t_level, int):
#         # print("t_level already int")
#         return input_t_level
#     else:
#         # print("t_level in string form, swapping")
#         return tool_level_format_swap(input_t_level)
#
#
# def tool_level_as_string(input_t_level):
#     # print(f"changing t_level '{input_t_level}' to string")
#     if isinstance(input_t_level, str):
#         # print("t_level already string")
#         return input_t_level
#     else:
#         # print("t_level in int form, swapping")
#         return tool_level_format_swap(input_t_level)


class ToolLevel(Enum):
    ZERO = 0  # Unusable things, like wool
    ONE = 1  # Wood or gold
    TWO = 2  # Stone
    THREE = 3  # Iron
    FOUR = 4  # Diamond
    FIVE = 5  # Netherite
    SIX = 6  # Maxed forge hammer in 1.18?
    SEVEN = 7  # Maxed forge hammer in 1.16?

    def get_legacy_int(self):
        return self.value

    def get_harvest_level(self):
        return self.value - 1

    def get_modern_string(self):
        string_dict = {0: 0, 1: "minecraft:wood", 2: "minecraft:stone", 3: "minecraft:iron",
                       4: "minecraft:diamond", 5: "minecraft:netherite", 6: "tetra:maxed_forge_hammer",
                       7: "tetranomicon:tier_seven"}
        return string_dict[self.value]

    @classmethod
    def ToolLevel_from_string(cls, input_level):
        if input_level == 0 or input_level == "0":
            return ToolLevel.ZERO
        elif input_level in ["minecraft:wood", "minecraft:gold", "1"]:
            return ToolLevel.ONE
        elif input_level in ["minecraft:stone", "2"]:
            return ToolLevel.TWO
        elif input_level in ["minecraft:iron", "3"]:
            return ToolLevel.THREE
        elif input_level in ["minecraft:diamond", "4"]:
            return ToolLevel.FOUR
        elif input_level in ["minecraft:netherite", "5"]:
            return ToolLevel.FIVE
        elif input_level in ["tetra:maxed_forge_hammer", "tetranomicon:six", "tetranomicon:seven",
                             "tetranomicon:tier_six", "tetranomicon:tier_seven", "tetranomicon:netherite_plus",
                             "6", "7"]:
            return ToolLevel.SIX
        else:
            raise ValueError(f"Could not convert string {input_level} to a ToolLevel")

    @classmethod
    def get_tool_level(cls, input_level):
        if isinstance(input_level, str):
            return ToolLevel.ToolLevel_from_string(input_level)
        elif isinstance(input_level, int):
            return ToolLevel(input_level)
