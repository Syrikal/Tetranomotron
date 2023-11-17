from enum import Enum


def main():
    # test()
    pass


class ToolBoost:
    # Has a ToolType, an int level, and a float efficiency
    def __init__(self, type, level, efficiency):
        self.tool_type = type
        self.level = int(level)
        self.efficiency = float(efficiency)

    @classmethod
    # Generates from a string, such as from a CSV
    def create_from_csv(cls, tool_string):
        split = tool_string.split(" ")
        if len(split) != 3:
            raise ValueError(f"Attempted to parse {split} as a tool boost. Aborting.")
        else:
            return ToolBoost(ToolType(split[0]), split[1], split[2])

    def get_print_string(self):
        return f"{self.tool_type.name}: [{self.level}, {self.efficiency}]"

    # Generates a json block for insertion into a socket json
    def get_json_line(self, legacy):
        name = self.tool_type if legacy else self.tool_type.modern_name()
        return f'''"{name}": [{self.level}, {self.efficiency}]'''

    # Generates a string formatted for storing in a CSV
    def get_csv_string(self):
        return f"{self.tool_type} {self.level} {self.efficiency}"


# Returns a JSON block for a list of tool boosts
def get_tool_boost_json_block(list_of_boosts, legacy, relevant_tools):
    lines = []
    for boost in list_of_boosts:
        if boost.tool_type in relevant_tools:
            lines.append(boost.get_json_line(legacy))

    # If no relevant tools, do not add anything
    if not lines:
        return ""

    inner = ",\n                ".join(lines)
    return f'''
            "tools": {{
                {inner}
            }}'''


# Creates a list of tool boosts from a csv string
def create_boosts_from_csv(csv_line):
    if len(csv_line) == 0:
        return []
    split_line = csv_line.split(", ")
    return [ToolBoost.create_from_csv(boost) for boost in split_line]


class ToolType(Enum):
    AXE = "axe"
    SHOVEL = "shovel"
    PICKAXE = "pickaxe"
    HOE = "hoe"
    CUT = "cut"

    def modern_name(self):
        match self:
            case ToolType.AXE:
                return "axe_dig"
            case ToolType.SHOVEL:
                return "shovel_dig"
            case ToolType.HOE:
                return "hoe_dig"
            case ToolType.PICKAXE:
                return "pickaxe_dig"
            case ToolType.CUT:
                return "cut"


def test():
    pass


if __name__ == "__main__":
    main()
