from enum import Enum


class MinecraftVersion(Enum):
    SIXTEEN = 16
    EIGHTEEN = 18
    NINETEEN = 19
    TWENTY = 20

    @classmethod
    # Generates a MinecraftVersion from
    def get_version(cls, version_integer):
        if version_integer not in [16, 18, 19, 20]:
            raise ValueError(f"Attempted to turn '{version_integer}' into a minecraft version. Aborting")
        return cls(version_integer)

    def get_csv_string(self):
        match self:
            case MinecraftVersion.SIXTEEN:
                return "16"
            case MinecraftVersion.EIGHTEEN:
                return "18"
            case MinecraftVersion.NINETEEN:
                return "19"
            case MinecraftVersion.TWENTY:
                return "20"

    def get_print_string(self):
        match self:
            case MinecraftVersion.SIXTEEN:
                return "1.16"
            case MinecraftVersion.EIGHTEEN:
                return "1.18"
            case MinecraftVersion.NINETEEN:
                return "1.19"
            case MinecraftVersion.TWENTY:
                return "1.20"


def get_versions_csv_string(list_of_versions):
    return ", ".join([x.get_csv_string() for x in list_of_versions])
