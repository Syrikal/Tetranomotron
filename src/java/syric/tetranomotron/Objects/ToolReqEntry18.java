package syric.tetranomotron.Objects;

public class ToolReqEntry18 {

    public String hammer_dig;
    public String axe_dig;
    public String cut;

    public ToolReqEntry18(ToolReqEntry16 entry16) {
        hammer_dig = entry16.hammer == null ? null : convertInt(entry16.hammer);
        axe_dig = entry16.axe == null ? null : convertInt(entry16.axe);
        cut = entry16.cut == null ? null : convertInt(entry16.cut);
    }

    public static String convertInt(int input) {
        switch (input) {
            case 1 -> { return "minecraft:wood"; }
            case 2 -> { return "minecraft:stone"; }
            case 3 -> { return "minecraft:iron"; }
            case 4 -> { return "minecraft:diamond"; }
            case 5 -> { return "minecraft:netherite"; }
            case 6 -> { return "tetranomicon:six"; }
            case 7 -> { return "tetranomicon:seven"; }
            case 8 -> { return "tetranomicon:eight"; }
        }
        return null;
    }

}
