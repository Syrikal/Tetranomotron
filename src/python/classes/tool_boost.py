from tool_properties import ToolType


def main():
    test()
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

    # Returns True if it's the same as another provided boost
    def matches(self, other_boost):
        return all([self.tool_type == other_boost.tool_type, self.level == other_boost.level, self.efficiency == other_boost.efficiency])


# Creates a list of tool boosts from a csv string
def create_boosts_from_csv(csv_entry):
    if len(csv_entry) == 0:
        return []

    if csv_entry.startswith("all"):
        # print("generating all")
        boosts = []
        for tool in ToolType:
            # print(f"adding tool '{tool.value}'")
            newstring = csv_entry.replace("all", tool.value)
            # print(f"generating from string {newstring}")
            boosts.append(ToolBoost.create_from_csv(newstring))
        return boosts

    else:
        split_line = csv_entry.split(", ")
        return [ToolBoost.create_from_csv(boost) for boost in split_line]


def get_toolboosts_csv_string(list_of_boosts):
    # Check if it's an 'all x y' situation
    all = True
    first_boost = list_of_boosts[0]
    x, y = first_boost.level, first_boost.efficiency
    # print(f"Level and efficiency: {x}, {y}")
    for tool in ToolType:
        seeking = ToolBoost(tool, x, y)
        if not any([seeking.matches(x) for x in list_of_boosts]):
            all = False
            # print(f"{tool.value} did not have a matching boost present")
            break

    if all:
        # print("Returning all!")
        return f"all {x} {y}"
    else:
        return ", ".join([x.get_csv_string() for x in list_of_boosts])


def test():
    csv_string = "all 1 3"
    boosts = create_boosts_from_csv(csv_string)
    print([x.get_print_string() for x in boosts])
    print(get_toolboosts_csv_string(boosts))

    pass


if __name__ == "__main__":
    main()
