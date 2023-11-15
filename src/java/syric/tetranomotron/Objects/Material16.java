package syric.tetranomotron.Objects;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;
import syric.tetranomotron.Util;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class Material16 extends Material {

    public String key;
    public String category;
    public String primary;
    public String secondary;
    public String tertiary;
    public String durability;
    public String integrityCost;
    public String integrityGain;
    public String magicCapacity;
    public String toolLevel;
    public String toolEfficiency;
    public TintEntry tints;
    public String[] textures;
    public ItemEntry16 material;
    public Object effects;
    public Object improvements;
    public ToolReqEntry16 requiredTools;


    @JsonIgnore
    public String getModID() {
        return Util.getModID(material);
    }

    @JsonIgnore
    public void clean() {
        requiredTools.clean();
    }

}
