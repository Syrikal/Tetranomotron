# Traits are either Effects or Improvements. They work the same. Improvements shouldn't have efficiencies, just levels.
from enum import Enum


def main():
    # test()
    pass


class Trait:
    # Generates a Trait from a name and 1-2 numbers
    def __init__(self, trait_type, name, level, efficiency):
        self.trait_type = trait_type
        self.name = name
        self.level = int(level)
        self.efficiency = float(efficiency)

        # If efficiency is integer (e.g. 2.0), set it to an integer (e.g. 2).
        if self.efficiency.is_integer():
            self.efficiency = int(self.efficiency)

        match trait_type:
            case TraitType.IMPROVEMENT:
                if self.efficiency != 0:
                    raise ValueError(f"Error when generating trait {name}:"
                                     f" improvements cannot have nonzero efficiency.")
            case TraitType.ATTRIBUTE:
                if self.level != 0:
                    raise ValueError(f"Error when generating trait {name}: attributes cannot have nonzero level.")
                if self.efficiency == 0:
                    raise ValueError(f"Error when generating trait {name}: attributes cannot have zero efficiency.")
            case TraitType.EFFECT:
                if self.level == 0 and self.efficiency == 0:
                    raise ValueError(f"Error when generating trait {name}:"
                                     f" effects cannot have zero level and efficiency.")

    @classmethod
    # Generates a Trait from a string, such as from a CSV
    def create_from_csv(cls, trait_string):
        split = trait_string.split(" ")
        if len(split) != 4:
            raise ValueError(f"Attempted to make a trait out of {split}.")
        trait_type = TraitType(split[0])
        return Trait(trait_type, split[1], split[2], split[3])

    # Generates a string formatted for printing
    def get_print_string(self):
        return f"{self.trait_type.get_initial()} {self.name} [{self.level}, {self.efficiency}]"

    # Generates a string formatted for putting into a JSON
    def get_json_block(self):
        match self.trait_type:
            case TraitType.EFFECT:
                if self.efficiency != 0:
                    return f'''"{self.name}": [{self.level}, {self.efficiency}]'''
                else:
                    return f'''"{self.name}": {self.level}'''
            case TraitType.IMPROVEMENT:
                return f'''"{self.name}": {self.level}'''
            case TraitType.ATTRIBUTE:
                if self.efficiency == 0:
                    return f'''"{self.name}": 0'''
                else:
                    return f'''"{self.name}": {self.efficiency}'''

    # Generates a string formatted for storing in a CSV
    def get_csv_string(self):
        return f"{self.trait_type.value} {self.name} {self.level} {self.efficiency}"

    # Checks if everything is OK
    def check_valid(self):
        match self.trait_type:
            case TraitType.EFFECT:  # Effects have a level and, possibly, an efficiency
                type_check = isinstance(self.level, int) and\
                             (isinstance(self.efficiency, float) or isinstance(self.efficiency, int))
                value_check = not (self.level == 0 and self.efficiency == 0)
                return type_check and value_check
            case TraitType.IMPROVEMENT:  # Improvements have a level only
                type_check = isinstance(self.level, int)
                value_check = self.efficiency == 0
                return type_check and value_check
            case TraitType.ATTRIBUTE:  # Attributes have an efficiency only
                type_check = isinstance(self.efficiency, float) or isinstance(self.efficiency, int)
                value_check = self.level == 0 and self.efficiency != 0
                return type_check and value_check


# Generates a list of Traits from a comma-and-space-separated string.
def gen_traits_from_string(input_string):
    output = []
    if len(input_string) == 0:
        return output
    trait_strings = input_string.split(", ")
    for trait_string in trait_strings:
        output.append(Trait.create_from_csv(trait_string))
    return output


# Generates a string to be used in creating a CSV
# Works for several traits
def get_traits_csv_string(list_of_traits):
    trait_strings = [x.get_csv_string() for x in list_of_traits]
    return ", ".join(trait_strings)


# Generates a JSON block from a list of traits
def get_traits_json_block(list_of_traits):
    # Return empty block if there's no traits
    if not list_of_traits:
        return ""

    # Double-check that all traits are valid
    for trait in list_of_traits:
        if not trait.check_valid():
            raise ValueError(f"Detected invalid trait while making JSON: {trait.get_print_string()}")

    # Double-check that all traits have the same type
    trait_type = list_of_traits[0].trait_type
    for trait in list_of_traits:
        if trait.trait_type != trait_type:
            raise ValueError(
                f"Trait list contains multiple trait types: {[x.get_print_string() for x in list_of_traits]}")

    trait_type_name = trait_type.get_name().lower() + "s"

    string_list = [trait.get_json_block() for trait in list_of_traits]
    inner_string = ",\n        ".join(string_list)
    return f'''    "{trait_type_name}": {{
        {inner_string}
    }},'''


class TraitType(Enum):
    EFFECT = "eff"
    IMPROVEMENT = "imp"
    ATTRIBUTE = "att"

    def get_name(self):
        match self:
            case TraitType.EFFECT:
                return "Effect"
            case TraitType.IMPROVEMENT:
                return "Improvement"
            case TraitType.ATTRIBUTE:
                return "Attribute"

    def get_initial(self):
        match self:
            case TraitType.EFFECT:
                return "E"
            case TraitType.IMPROVEMENT:
                return "I"
            case TraitType.ATTRIBUTE:
                return "A"


def test():
    # Create some traits from strings
    toughness = Trait.create_from_csv("att generic.armor_toughness 0 2")
    damage = Trait.create_from_csv("att **generic.attack_damage 0 1.5")
    intuit = Trait.create_from_csv("eff intuit 3 0")
    fiery_self = Trait.create_from_csv("eff fierySelf 3 1")
    fire_aspect = Trait.create_from_csv("imp enchantment/fire_aspect 1 0")

    all_traits = [toughness, damage, intuit, fiery_self, fire_aspect]

    # Analyze each trait
    for trait in all_traits:
        print(f"Analyzing {trait.name}...")
        print(trait.get_print_string())
        trait.check_valid()
        print()
    print()

    # Handle lists of traits
    effects = [intuit, fiery_self]
    attributes = [toughness, damage]
    improvements = [fire_aspect]
    # bad_list = [intuit, toughness, fire_aspect]

    for trait_list in [effects, attributes, improvements]:
        print("Generating JSON block for trait list...")
        print(get_traits_json_block(trait_list))
        print()
    print()

    # Turn traits into strings and back again
    attributes_storage = get_traits_csv_string(attributes)
    print(f"Attributes: {attributes_storage}")
    new_attributes = gen_traits_from_string(attributes_storage)
    print("Regenerated attributes from storage...")
    for trait in new_attributes:
        print(f"Analyzing {trait.name}...")
        print(trait.get_print_string())
        trait.check_valid()
        print()

    print()
    print("Testing complete")


if __name__ == "__main__":
    main()
