package syric.tetranomotron;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import syric.tetranomotron.Objects.Material16;
import syric.tetranomotron.Objects.Material18;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Objects;

public class Tetranomotron {

    public static void main(String[] args) {

        ObjectMapper indentMapper = new ObjectMapper().enable(SerializationFeature.INDENT_OUTPUT).setSerializationInclusion(JsonInclude.Include.NON_NULL);
        ObjectMapper mapper = new ObjectMapper();

        mapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
        try {
//            MaterialRaw16 gold16 = mapper.readValue(new File("src/main/java/syric/tetranomotron/example16.json"), MaterialRaw16.class);

            ArrayList<String> langLines = new ArrayList<>();
            String timeStamp = new SimpleDateFormat("yyyy.MM.dd.HH.mm.ss").format(new java.util.Date());

            File inputFolder = new File("src/main/resources/input");
            for (File file : Objects.requireNonNull(inputFolder.listFiles())) {
                Material16 mat = mapper.readValue(file, Material16.class);
                Material18 updated = new Material18(mat);
//                System.out.println(mapper.writeValueAsString(updated));
                Util.confirm(updated);
                Util.print(indentMapper, updated, timeStamp);
                langLines.add(Util.getLangLines(updated));
            }

            FileWriter langFile = new FileWriter("src/main/resources/generated/" + timeStamp + "/langfile.json");
            langFile.write(Util.getLangString(langLines));
            langFile.close();



        } catch (IOException e) {
            e.printStackTrace();
        }

    }


}
