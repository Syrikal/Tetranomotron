from enum import Enum


def main():
    # test()
    pass


class ToolBoost:
    # Has a ToolType, an int level, and a float efficiency
    def __init__(self, tool_type, level, efficiency):
        self.tool_type = tool_type
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

    # Generates a print-formatted string.
    # (Also formatted for a JSON, but don't need that anymore.)
    def get_print_string(self):
        return f"{self.tool_type.name}: [{self.level}, {self.efficiency}]"

    # Generates a string formatted for storing in a CSV
    def get_csv_string(self):
        return f"{self.tool_type.value} {self.level} {self.efficiency}"


# Creates a list of tool boosts from a csv string
def create_boosts_from_csv(csv_entry):
    if len(csv_entry) == 0:
        return []
    split_line = csv_entry.split(", ")
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
