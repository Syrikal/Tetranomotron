from collections import OrderedDict


def add_mod_loaded_condition(json_object, modid):
    condition = OrderedDict()

    condition["type"] = "forge:mod_loaded"
    condition["modid"] = modid

    json_object["conditions"] = [condition]
