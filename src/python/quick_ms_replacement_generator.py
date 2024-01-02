materials_list = '''amethyst
aquamarine
black_diamond
blaze
bronze
chromite
citrine
cobalt
demonite
hellfire
jade
linium
mithril
neridium
obsidian
olivine
onyx
opal
platinum
pyridium
quartz
redstone
ruby
sapphire
scarlet_emerald
silver
steel
tanzanite
tin
titanium
topaz
trio
tungsten
turquoise
uranium
violium
white_opal'''.split("\n")

for material in materials_list:
    print(f'''tool/{material}_axe	ms	axe	18, 19, 20	ms_{material}
tool/{material}_hoe	ms	hoe	18, 19, 20	ms_{material}
tool/{material}_pickaxe	ms	pickaxe	18, 19, 20	ms_{material}
tool/{material}_shovel	ms	shovel	18, 19, 20	ms_{material}
tool/{material}_sword	ms	sword	18, 19, 20	ms_{material}\n''')
