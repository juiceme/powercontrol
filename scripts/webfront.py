#!/usr/bin/python3

# -*- coding: utf-8 -*-

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
from dateutil import parser
from datetime import datetime
import os
import sys

hostName = "0.0.0.0"
serverPort = 8080

if len(sys.argv) != 2:
	print("Just one argument is needed, the configuration file")
	sys.exit()

def get_price():
	config_file = open(sys.argv[1])
	config = json.load(config_file)
	config_file.close()
	file = open(config["statepath"] + "/spot_prices.json")
	data = json.load(file)
	now = datetime.now()
	price = 0
	winter_day = False
	if config["pricing"]["seasonal_pricing"]:
		if now.month > 10 or now.month < 4:
			if now.weekday() < 5:
				if now.hour > 6 and now.hour < 22:
					price = config["pricing"]["winter_day"]
					winter_day = True
			price = config["pricing"]["other"]
	for n in data:
		dayline = parser.parse(n["DateTime"])
		if dayline.day == now.day and dayline.hour == now.hour:
			price = price + n["PriceWithTax"] * 100
	return price, winter_day

class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):
		price, winter_day = get_price()
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		if winter_day:
			season = "Talviaika"
		else:
			season = "Muu aika"
		self.wfile.write(bytes("<html><head><title>HOMECONTROL</title></head>", "utf-8"))
		self.wfile.write(bytes("<p><p>Hinta nyt: %.2f cent/kWh " % price, "utf-8"))
		self.wfile.write(bytes("(%s)<p><p>" % season, "utf-8"))
		if os.path.exists("/home/juice/.local/state/fighter_on"):
			self.wfile.write(bytes("<p>Boileri: ON<p>", "utf-8"))
		else:
			self.wfile.write(bytes("<p>Boileri: OFF<p>", "utf-8"))
		if os.path.exists("/home/juice/.local/state/floor_on"):
			self.wfile.write(bytes("<p>Lattia: ON<p>", "utf-8"))
		else:
			self.wfile.write(bytes("<p>Lattia: OFF<p>", "utf-8"))
		if os.path.exists("/home/juice/.local/state/charging_on"):
			self.wfile.write(bytes("<p>Lataus: ON<p>", "utf-8"))
		else:
			self.wfile.write(bytes("<p>Lataus: OFF<p>", "utf-8"))
		self.wfile.write(bytes("</body></html>", "utf-8"))

if __name__ == "__main__":        
	webServer = HTTPServer((hostName, serverPort), MyServer)
	print("Server started http://%s:%s" % (hostName, serverPort))

	try:
		webServer.serve_forever()
	except KeyboardInterrupt:
		pass

	webServer.server_close()
	print("Server stopped.")

