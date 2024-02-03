from collections import OrderedDict

from .tool_properties import ToolLevel


class ToolRequirements:
    # Generates a ToolRequirements from three integers.
    # Integers refer to tier level
    def __init__(self, hammer, axe, cut):
        self.hammer = ToolLevel.get_tool_level(hammer)
        self.axe = ToolLevel.get_tool_level(axe)
        self.cut = ToolLevel.get_tool_level(cut)

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
                ham = tool[1]
                continue
            elif tool[0] == "axe" or tool[0] == "axe_dig":
                # print("Requirement is for axe")
                axe = tool[1]
                continue
            elif tool[0] == "cut":
                # print("Requirement is for cut")
                cut = tool[1]
                continue
            else:
                raise ValueError(f"Attempted to parse {tool} as a tool requirement. Aborting.")

        output = ToolRequirements(ham, axe, cut)
        # print(f"Generated tool requirements: {output.string()}")
        return output

    # Generates a JSON dict to be assigned as the value of the "requiredTools" key
    def get_json_object(self, version):
        output = OrderedDict()
        # print(f"             ...Generating a tool requirements for version {version}")

        if self.hammer != ToolLevel.ZERO:
            if version.value == 16:
                # print("triggered v16 hammer")
                # Hammers are different numbers in 1.16
                # Or rather, they're the only ones that are the same in both versions
                output["hammer"] = self.hammer.get_legacy_hammer_int()
            elif version.value == 18:
                # print("triggered v18 hammer")
                output["hammer_dig"] = self.hammer.get_18_string()
            else:
                # print("triggered v19-20 hammer")
                output["hammer_dig"] = self.hammer.get_modern_string()
        if self.axe != ToolLevel.ZERO:
            if version.value == 16:
                output["axe"] = self.axe.get_legacy_int()
            elif version.value == 18:
                output["axe_dig"] = self.axe.get_18_string()
            else:
                output["axe_dig"] = self.axe.get_modern_string()
        if self.cut != ToolLevel.ZERO:
            if version.value == 16:
                output["cut"] = self.cut.get_legacy_int()
            elif version.value == 18:
                output["cut"] = self.cut.get_18_string()
            else:
                output["cut"] = self.cut.get_modern_string()

        # print(output)
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
