#!/usr/bin/env python
import json

with open("static/myjson.json", "r") as jsonFile:
    data = json.load(jsonFile)

tmp = data["location"]
data["location"] = "tonoton"

with open("static/myjson.json", "w") as jsonFile:
    json.dump(data, jsonFile)
