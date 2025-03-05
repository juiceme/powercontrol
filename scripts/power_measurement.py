#!/usr/bin/python3

import paho.mqtt.subscribe as subscribe
import json
import os
import sys

if len(sys.argv) != 2:
        print("Just one argument is needed, the configuration file")
        sys.exit()

config_file = open(sys.argv[1])
config = json.load(config_file)
config_file.close()

if not config["measurements"]["enabled"]:
        print("Power measurement is disabled")
        sys.exit()

first = True
prev_power = 0.0

def on_message_save_delta_power(client, userdata, message):
        global first
        global prev_power
        curr_power = 0.0
        avg_power = 0.0
        payload = json.loads(message.payload)
        if "emdata:0" in payload["params"]:
                if first == True:
                        first = False
                        prev_power = payload["params"]["emdata:0"]["total_act"]
                else:
                        curr_power = payload["params"]["emdata:0"]["total_act"]
                        avg_power = curr_power - prev_power
                        prev_power = curr_power
                        power_file = open(config["statepath"] + "/avg_power.tmp", "w")
                        power_file.write(str(avg_power))
                        power_file.close()
                        os.replace(config["statepath"] + "/avg_power.tmp", config["statepath"] + "/avg_power")

subscribe.callback(on_message_save_delta_power, config["measurements"]["topic"], hostname=config["measurements"]["publisher"], userdata={})

