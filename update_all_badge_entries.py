import os
import json

for entry in os.listdir("userdata/"):
    with open(f"userdata/{entry}", "r") as file:
        data: dict = json.load(file)
        keys: list = []
        for key, _ in data["badges"].items():
            keys.append(key)
        data.pop("badges")
        data["badges"] = keys
        print(data)

    with open(f"userdata/{entry}", "w") as file:
        json.dump(data, file, indent=4)