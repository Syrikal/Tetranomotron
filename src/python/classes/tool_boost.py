from enum import Enum


def main():
    # test()
    pass


class ToolBoost:
    # Has a dictionary relating ToolTypes to lists of an int and a float (level and efficiency, respectively)
    def __init__(self, input_dict):
        self.tools = input_dict

    @classmethod
    # Generates from a string, such as from a CSV
    def create_from_csv(cls, tool_string):
        tool_boost_dict = {}
        individual_tools = tool_string.split(", ")
        for tool in individual_tools:
            split = tool.split(" ")
            if len(split) != 3:
                raise ValueError(f"Attempted to parse {split} as a tool boost. Aborting.")
            else:
                tool_type = ToolType(split[0])
                boost = [int(split[1]), float(split[2])]
                tool_boost_dict[tool_type] = boost

        output = ToolBoost(tool_boost_dict)
        return output

    def get_print_string(self):
        return f"Tool Boosts: {[(x, self.tools[x]) for x in self.tools]}"

    # Generates a json block for insertion into a socket json
    def get_json_block(self, legacy, relevant_tools):
        lines = []
        for tool in self.tools:
            if tool not in relevant_tools:
                continue
            name = tool if legacy else tool.modern_name()
            level, efficiency = self.tools[tool][0], self.tools[tool][1],
            lines.append(f'''"{name}": [{level}, {efficiency}]''')

        # If no relevant tools, do not add anything
        if not lines:
            return ""

        inner = ",\n            ".join(lines)
        return f'''
            "tools": {{
                {inner}
            }},'''

    # Generates a string formatted for storing in a CSV
    def get_csv_string(self):
        list_of_strings = []
        for tool in self.tools:
            tool_type = tool
            properties = self.tools[tool]
            list_of_strings.append(f"{tool_type} {properties[0]} {properties[1]}")
        return ", ".join(list_of_strings)


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
