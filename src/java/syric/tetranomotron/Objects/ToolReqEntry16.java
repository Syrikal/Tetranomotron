package syric.tetranomotron.Objects;

public class ToolReqEntry16 {

    public Integer hammer;
    public Integer axe;
    public Integer cut;

    public void clean() {
        if (hammer == 0) {
            hammer = null;
        }
        if (axe == 0) {
            axe = null;
        }
        if (cut == 0) {
            cut = null;
        }
    }


}
