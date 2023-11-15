package syric.tetranomotron.Objects;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;
import syric.tetranomotron.Util;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class Material18 extends Material {

    public String key;
    public String category;
    public double primary;
    public double secondary;
    public double tertiary;
    public int durability;
    public int integrityCost;
    public int integrityGain;
    public int magicCapacity;
    public String toolLevel;
    public double toolEfficiency;
    public TintEntry tints;
    public String[] textures;
    public ItemEntry18 material;
    public Object effects;
    public Object improvements;
    public ToolReqEntry18 requiredTools;

    public Material18(Material16 material16) {
        this.key = material16.key;
        this.category = material16.category;
        this.primary = Double.parseDouble(material16.primary);
        this.secondary = Double.parseDouble(material16.secondary);
        this.tertiary = Double.parseDouble(material16.tertiary);
        this.durability = Integer.parseInt(material16.durability);
        this.integrityCost = Integer.parseInt(material16.integrityCost);
        this.integrityGain = Integer.parseInt(material16.integrityGain);
        this.magicCapacity = Integer.parseInt(material16.magicCapacity);
        this.toolLevel = ToolReqEntry18.convertInt(Integer.parseInt(material16.toolLevel));
        this.toolEfficiency = Double.parseDouble(material16.toolEfficiency);
        this.tints = material16.tints;
        this.textures = material16.textures;
        this.material = new ItemEntry18(material16.material);
        this.effects = material16.effects;
        this.improvements = material16.improvements;
        this.requiredTools = new ToolReqEntry18(material16.requiredTools);
    }

    @JsonIgnore
    public String getModID() {
        return Util.getModID(material);
    }
}
