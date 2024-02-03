import json
import os
from collections import OrderedDict

items = "sword, axe, pickaxe, hoe, shovel, cape, bow, helmet, chestplate, leggings, boots, gloves, ring"
phoenix_items = ["lost_aether_content:phoenix_sword",
                 "lost_aether_content:phoenix_axe",
                 "lost_aether_content:phoenix_pickaxe",
                 "lost_aether_content:phoenix_hoe",
                 "lost_aether_content:phoenix_shovel",
                 "lost_aether_content:phoenix_cape",
                 "aether:phoenix_bow",
                 "aether:phoenix_helmet",
                 "aether:phoenix_chestplate",
                 "aether:phoenix_leggings",
                 "aether:phoenix_boots",
                 "aether:phoenix_gloves",
                 "aether_redux:phoenix_ring"]
#
# for item in items.split(", "):
#     print(f'''"lost_aether_content:phoenix_{item}",''')

for item in phoenix_items:
    print(f"Generating recipe from {item}")

    mod_id, item = item.split(":")

    output = OrderedDict()
    output["type"] = "aether:enchanting"
    output["cookingtime"] = 1500
    output["ingredient"] = {"item": f"{mod_id}:{item}"}
    output["result"] = {"item": "aetheric_tetranomicon:phoenix_scrap",
                        "count": 3}

    path = os.path.join("phoenix_recipes", f"phoenix_scrap_from_{item}.json")
    with open(path, "w") as jsonfile:
        jsonfile.write(json.dumps(output, indent=4))
