import os
import json

for root, dirs, files in os.walk("../resources/Tetra 1.20"):
    for file in files:
        filename, file_extension = os.path.splitext(file)
        if file_extension == ".json":
            # print("found JSON file: " + os.path.join(root, file))
            filepath = os.path.join(root, file)
            with open(filepath) as opened_file:
                file_json = json.load(opened_file)
            with open(filepath, "w") as reopened_file:
                reopened_file.write(json.dumps(file_json, indent=4))
