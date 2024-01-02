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
    ZERO = 0                    # Unusable things, like wool                          Legacy / Modern
    WOOD = 1                    # Wood.                     Harvest level 0    Tool level 1 / 1        Wood hammer (1)
    GOLD = 2                    # Gold.                     Harvest level 0    Tool level 1 / 2        Stone hammer (2)
    STONE = 3                   # Stone.                    Harvest level 1    Tool level 2 / 3        Iron hammer (3)
    IRON = 4                    # Iron.                     Harvest level 2    Tool level 3 / 4        Blackstone hammer (4)
    DIAMOND = 5                 # Diamond.                  Harvest level 3    Tool level 4 / 5        Obsidian hammer (5)
    NETHERITE = 6               # Netherite.                Harvest level 4    Tool level 5 / 6        Netherite hammer (6)
    NETHERITE_PLUS_ONE = 7      # One above netherite.      Harvest level 5    Tool level 6 / 7        Maxed forge hammer (7)
    NETHERITE_PLUS_TWO = 8      # Two above netherite.      Harvest level 6    Tool level 7 / 8
    NETHERITE_PLUS_THREE = 9    # Three above netherite     Harvest level 7    Tool level 8 / 9
    NETHERITE_PLUS_FOUR = 10    # Four above netherite.     Harvest level 8    Tool level 9 / 10
    NETHERITE_PLUS_FIVE = 11    # Five above netherite.     Harvest level 9    Tool level 10 / 11

    # Tool tier number in 1.16
    def get_legacy_int(self):
        if self.value in [0, 1]:
            return self.value
        else:
            return self.value - 1

    def get_legacy_hammer_int(self):
        return self.value

    # Coded into Minecraft
    def get_harvest_level(self):
        return max(self.value - 2, 0)

    # Modern string tier
    def get_modern_string(self):
        string_dict = {0: 0, 1: "minecraft:wood", 2: "minecraft:gold", 3: "minecraft:stone",
                       4: "minecraft:iron", 5: "minecraft:diamond", 6: "minecraft:netherite",
                       7: "tetra:maxed_forge_hammer", 8: "tetranomicon:tier_eight",
                       9: "tetranomicon:tier_nine", 10: "tetranomicon:tier_ten", 11: "tetranomicon:tier_eleven"}
        return string_dict[self.value]

    @classmethod
    def ToolLevel_from_legacy(cls, input_level):
        tool_level_dict = {0: ToolLevel.ZERO,
                           1: ToolLevel.WOOD,
                           2: ToolLevel.STONE,
                           3: ToolLevel.IRON,
                           4: ToolLevel.DIAMOND,
                           5: ToolLevel.NETHERITE,
                           6: ToolLevel.NETHERITE_PLUS_ONE,
                           7: ToolLevel.NETHERITE_PLUS_TWO}
        return tool_level_dict[int(input_level)]

    @classmethod
    def ToolLevel_from_legacy_hammer(cls, input_level):
        return ToolLevel(input_level)

    @classmethod
    def ToolLevel_from_string(cls, input_level):
        if input_level == "0":
            return ToolLevel.ZERO
        elif input_level in ["minecraft:wood",  "wood"]:
            return ToolLevel.WOOD
        elif input_level in ["minecraft:gold", "gold"]:
            return ToolLevel.GOLD
        elif input_level in ["minecraft:stone", "stone"]:
            return ToolLevel.STONE
        elif input_level in ["minecraft:iron", "iron"]:
            return ToolLevel.IRON
        elif input_level in ["minecraft:diamond", "diamond"]:
            return ToolLevel.DIAMOND
        elif input_level in ["minecraft:netherite", "netherite"]:
            return ToolLevel.NETHERITE
        elif input_level in ["tetranomicon:netherite_plus", "tetranomicon:tier_six", "tetranomicon:six", "netherite_plus_one", "tetra:maxed_forge_hammer"]:
            return ToolLevel.NETHERITE_PLUS_ONE
        elif input_level in ["tetranomicon:tier_seven", "tetranomicon:tier_eight", "netherite_plus_two"]:
            return ToolLevel.NETHERITE_PLUS_TWO
        else:
            raise ValueError(f"Could not convert string {input_level} to a ToolLevel")

    @classmethod
    def get_tool_level(cls, input_level):
        if isinstance(input_level, str):
            if input_level.isdigit():
                return ToolLevel(int(input_level))
            else:
                return ToolLevel.ToolLevel_from_string(input_level)
        elif isinstance(input_level, int):
            return ToolLevel(input_level)
