package syric.tetranomotron.Objects;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonInclude;

public class ItemEntry18 {

    public String[] items;

    @JsonIgnore
    public ItemEntry18(ItemEntry16 entry16) {
        items = new String[]{ entry16.item };
    }

}
