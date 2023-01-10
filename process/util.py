# -*- coding: utf-8 -*-
import json

def getOCRConfig():
    with open("./config.json", "r", encoding="utf-8") as fp:
        return json.load(fp)