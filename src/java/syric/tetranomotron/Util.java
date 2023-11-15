package syric.tetranomotron;

import com.fasterxml.jackson.databind.ObjectMapper;
import syric.tetranomotron.Objects.*;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Scanner;

public class Util {

    public static String getModID(ItemEntry16 entry) {
        String[] split = entry.item.split(":");
        return split[0];
    }
    public static String getModID(ItemEntry18 entry) {
        String[] split = entry.items[0].split(":");
        return split[0];
    }

    public static void setKey(Material material) {
        if (material instanceof Material18 mat) {
            String oldKey = mat.key;
            String modID = getModID(mat.material);

            String tentativeKey = modID + "_" + oldKey;
            Scanner reader = new Scanner(System.in);  // Reading from System.in
            System.out.println("Key candidate: " + tentativeKey + ".\nEnter 'y' to confirm or enter replacement key.");
            String n = reader.next();
            System.out.println("Input received: " + n);

            mat.key = n.equals("y") ? tentativeKey : modID + "_" + n;

            System.out.println("Set key to " + mat.key);

            reader.close();

        } else if (material instanceof Material16 mat) {
            String oldKey = mat.key;
            String modID = getModID(mat.material);

            String tentativeKey = modID + "_" + oldKey;
            Scanner reader = new Scanner(System.in);  // Reading from System.in
            System.out.println("Key candidate: " + tentativeKey + ".\nEnter 'y' to confirm or enter replacement key.");
            String n = reader.next();
            System.out.println("Input received: " + n);

            mat.key = n.equals("y") ? tentativeKey : modID + n;

            System.out.println("Set key to " + mat.key);

            reader.close();
        }
    }

    public static String getNewFilepath(Material material, String timeStamp, boolean directory) {
        String category = null;
        String key = null;
        if (material instanceof Material16 mat) {
            category = mat.category;
            key = mat.key;
        } else if (material instanceof Material18 mat) {
            category = mat.category;
            key = mat.key;
        }

        if (directory) {
            return "src/main/resources/generated/" + timeStamp + "/materials/" + category;
        } else {
            return "src/main/resources/generated/" + timeStamp + "/materials/" + category + "/" + key + ".json";
        }
    }

    public static void   print(ObjectMapper mapper, Material material, String timestamp) throws IOException {

        Files.createDirectories(Paths.get(getNewFilepath(material, timestamp, true)));

//        Scanner reader = new Scanner(System.in);  // Reading from System.in
//        System.out.println("Key candidate: " + tentativeKey + ".\nEnter 'y' to confirm or enter replacement key.");
//        String n = reader.next();
//        System.out.println("Input received: " + n);
//
//        mat.key = n.equals("y") ? tentativeKey : modID + n;
//
//        System.out.println("Set key to " + mat.key);

        mapper.writeValue(new File(getNewFilepath(material, timestamp, false)), material);

    }

    public static void confirm(Material18 mat) {
        String tentativeKey = mat.key;
        String modID = mat.getModID();
        String item = mat.material.items[0];

        Scanner reader = new Scanner(System.in);  // Reading from System.in
        System.out.println("Key candidate: " + tentativeKey + ". Item: " + item + "\nEnter 'y' to confirm or enter replacement key.");
        String n = reader.next();
        System.out.println("Input received: " + n);

        mat.key = n.equals("y") ? modID + "_" + tentativeKey : modID + "_" + n;

        System.out.println("Set key to " + mat.key + ".\n\n");
    }


    public static String getLangLines(Material material) {

        String key = "blank";
        if (material instanceof Material16 mat) {
            key = mat.key;
        } else if (material instanceof Material18 mat) {
            key = mat.key;
        }

        String name = key.split("_", 2)[1];

        name = name.replace("_", " ");
        name = name.substring(0, 1).toUpperCase() + name.substring(1);

        return "\"tetra.material." + key + "\": \"" + name + "\",\n" + "\"tetra.material." + key + ".prefix\": \"" + name + "\",\n";

    }


    public static String getLangString(ArrayList<String> langLines) {
        Collections.sort(langLines);
        StringBuilder sb = new StringBuilder();
        for (String line : langLines) {
            sb.append(line);
        }
        return sb.toString();
    }
}
