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
	file = open(config["spotfile"])
	data = json.load(file)
	now = datetime.now()
	price = 0
	for n in data:
		dayline = parser.parse(n["DateTime"])
		if dayline.day == now.day and dayline.hour == now.hour:
			price = n["PriceWithTax"]
	return price * 100

class MyServer(BaseHTTPRequestHandler):
	def do_GET(self):
		price = get_price()
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
		self.wfile.write(bytes("<html><head><title>HOMECONTROL</title></head>", "utf-8"))
		self.wfile.write(bytes("<p><p>Hinta nyt: %.2f cent/kWh<p><p>" % price, "utf-8"))
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

