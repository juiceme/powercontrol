#!/usr/bin/python3

import sys
import json
from urllib.request import urlopen

if len(sys.argv) != 2:
	print("Just one argument is needed, the configuration file")
	sys.exit()

config_file = open(sys.argv[1])
config = json.load(config_file)
config_file.close()

spot_prices_url = urlopen(config["url"])
data = json.loads(spot_prices_url.read())

if len(data) > 10:
	with open(config["spotfile"], "w") as outfile:
		json.dump(data, outfile)
	outfile.close()

