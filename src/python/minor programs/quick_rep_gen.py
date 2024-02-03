
input = '''bluebright/blue_skies/16, 18, 19, 20/blue_skies_bluebright/
starlit/blue_skies/16, 18, 19, 20/blue_skies_starlit_wood/
frostbright/blue_skies/16, 18, 19, 20/blue_skies_frostbright/
lunar/blue_skies/16, 18, 19, 20/blue_skies_lunar_wood/
dusk/blue_skies/16, 18, 19, 20/blue_skies_dusk/
maple/blue_skies/16, 18, 19, 20/blue_skies_maple/
comet/blue_skies/20/blue_skies_comet/
cherry/blue_skies/16, 18, 19/blue_skies_cherry/
turquoise_stone/blue_skies/16, 18, 19, 20/blue_skies_turquoise_stone/
lunar_stone/blue_skies/16, 18, 19, 20/blue_skies_lunar_stone/
pyrope/blue_skies/16, 18, 19, 20/blue_skies_pyrope/
aquite/blue_skies/16, 18, 19, 20/blue_skies_aquite/
diopside/blue_skies/16, 18, 19, 20/blue_skies_diopside/
charoite/blue_skies/16, 18, 19, 20/blue_skies_charoite/
horizonite/blue_skies/16, 18, 19, 20/blue_skies_horizonite/
////
kuko/organics/16, 18, 19, 20/organics_kuko/
iridite/organics/16, 18, 19, 20/organics_iridite/
venomite/organics/16, 18, 19, 20/organics_venomite/
endium/organics/16, 18, 19, 20/organics_endium/
flint/organics/16, 18, 19, 20/flint/
////
voidic_crystal/voidscape/16, 18, 19, 20/voidscape_voidic_crystal/
titanite/voidscape/16, 18, 19, 20/voidscape_titanite/
ichor/voidscape/16, 18, 19, 20/voidscape_ichor/
astral/voidscape/16, 18, 19, 20/voidscape_astral_crystal/
////
adamantite/enlightened_end/16, 18, 19, 20/enlightened_end_adamantite/
////
crystalline/phantasm/16, 18, 19, 20/phantasm_crystalline/
////
plasma/deep_dark_regrowth/19, 20/deep_dark_regrowth_plasma/
////
aluminium/nature_arise/20/nature_arise_aluminium/
copper/nature_arise/20/copper/
////
totemic_gold/l2complements/19, 20/emerald/totemic_gold
poseidite/l2complements/19, 20/l2complements_poseidite/
shulkerate/l2complements/19, 20/l2complements_shulkerate/iron
sculkium/l2complements/19, 20/l2complements_sculkium/netherite
eternium/l2complements/19, 20/l2complements_eternium/netherite
////
glowood/ms/18, 19, 20/ms_glowood/ms_glowood
flint/ms/18, 19, 20/flint/'''

aetherinput = '''skyjade/deep_aether/19, 20/deep_aether_skyjade/aether_skyroot
stratus/deep_aether/19, 20/deep_aether_stratus/aether_skyroot'''

tools = ["axe", "hoe", "pickaxe", "sword", "shovel"]

output = []

prevmodid = ""

for line in aetherinput.split("\n"):
    prefix, modid, versions, material, handle = line.split("/")
    if not prefix:
        continue

    if modid != prevmodid:
        output.append([])
        output.append([])
        prevmodid = modid

    for tool in tools:
        tool_id = prefix + "_" + tool
        modid = modid
        replacement_type = tool
        versions = versions
        material = material
        handle = handle

        output.append([tool_id, modid, replacement_type, versions, material, handle])
    output.append([])

for out in output:
    print("/".join(out))


