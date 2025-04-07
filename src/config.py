import json
import os

config_monitor = {
    "remote":None,
    "storage":"res"
        }
config_gui = {
        "geometry": "375x150",
        "colors": ["red","green"]
        }

def update_config():
    path = "config.json"
    if os.path.exists(path):
        with open(path) as log:
            tmp = json.loads(log.read())
            for key in tmp:
                if key in config_monitor:
                    config_monitor[key] = tmp[key]
                if key in config_gui:
                    config_gui[key] = tmp[key]
    with open(path, "w") as log:
        tmp = config_monitor | config_gui
        json.dump(tmp, log, indent=2)

config = {
        "monitor":config_monitor,
        "gui":config_gui,
        "update": update_config
        }
