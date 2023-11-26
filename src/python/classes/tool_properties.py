from enum import Enum


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
        elif input_level in ["tetra:maxed_forge_hammer", "tetranomicon:netherite_plus",
                             "tetranomicon:tier_six", "tetranomicon:six", "6"]:
            return ToolLevel.SIX
        elif input_level in ["tetranomicon:tier_seven", "tetranomicon:seven", "7"]:
            return ToolLevel.SEVEN
        else:
            raise ValueError(f"Could not convert string {input_level} to a ToolLevel")

    @classmethod
    def get_tool_level(cls, input_level):
        if isinstance(input_level, str):
            return ToolLevel.ToolLevel_from_string(input_level)
        elif isinstance(input_level, int):
            return ToolLevel(input_level)