#!/usr/bin/python3

import os
import sys
import json
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from dateutil import parser
from datetime import datetime
from urllib.request import urlopen

if len(sys.argv) != 2:
	print("Just one argument is needed, the configuration file")
	sys.exit()

class PowerControl:
	config_file_name = ""
	config = {}
	prices = {}
	sched = BlockingScheduler()

	def __init__(self, filename):
		self.config_file_name = filename
		self.get_config()

		# Before starting, always fetch the spot prices once
		self.fetch_spot_job()

		# Schedule the powercontrol job to run once each minute
		self.sched.add_job(self.powercontrol_job, 'cron', minute='0-59')

		# Schedule the fetch_spot job to run once per day
		self.sched.add_job(self.fetch_spot_job, 'cron', hour='17', minute='17')

		# Schedule the logger job to run once per hour
		self.sched.add_job(self.logger_job, 'cron', hour='0-23', minute='1')

		# Start the cronjobs
		self.sched.start()

	def get_config(self):
		config_file = open(self.config_file_name)
		self.config = json.load(config_file)
		config_file.close()

	def get_prices(self):
		price_file = open(self.config["statepath"] + "/spot_prices.json")
		self.prices = json.load(price_file)
		price_file.close()

	def get_seasonal_price(self, now):
		if self.config["pricing"]["seasonal_pricing"]:
			if now.month > 10 or now.month < 4:
				if now.hour > 6 and now.hour < 22:
					return self.config["pricing"]["winter_day"]
			return self.config["pricing"]["other"]
		return 0.0

	def get_current_price(self):
		now = datetime.now()
		for n in self.prices:
			item = parser.parse(n["DateTime"])
			if item.day == now.day and item.hour == now.hour:
				return n["PriceWithTax"] * 100 + self.get_seasonal_price(now)
			# If the hourly price is not found, return quite high price just in case
		return 100.0

	def check_current_override(self):
		now = datetime.now()
		min_a = 100
		min_b = 100
		min_c = 100
		min_d = 100
		hour_a = 0
		hour_b = 0
		hour_c = 0
		hour_d = 0
		for n in self.prices:
			date = parser.parse(n["DateTime"])
			current_price = n["PriceWithTax"]
			if date.day == now.day and date.hour >= 0 and date.hour <= 5:
				if min_a > current_price:
					min_a = current_price
					hour_a = date.hour
			if date.day == now.day and date.hour >= 6 and date.hour <= 11:
				if min_b > current_price:
					min_b = current_price
					hour_b = date.hour
			if date.day == now.day and date.hour >= 12 and date.hour <= 17:
				if min_c > current_price:
					min_c = current_price
					hour_c = date.hour
			if date.day == now.day and date.hour >= 18 and date.hour <= 23:
				if min_d > current_price:
					min_d = current_price
					hour_d = date.hour
		if now.hour == hour_a or now.hour == hour_b or now.hour == hour_c or now.hour == hour_d:
			return True
		return False

	def powercontrol_job(self):
		self.get_config()
		self.get_prices()
		current_price = self.get_current_price()
		now = datetime.now()
		print(now, end ="   ")
		print("%.2f c/kWh   " % self.get_current_price(), end ="")
		if current_price < self.config['limits']['heat']:
			print(" [Heat --> ON]  ", end ="")
			os.system(self.config["binpath"] + "/fighter_on.sh")
		else:
			if self.check_current_override():
				print(" [Heat --> OVERRIDE]  ", end ="")
				os.system(self.config["binpath"] + "/fighter_on.sh")
			else:
				print(" [Heat --> OFF] ", end ="")
				os.system(self.config["binpath"] + "/fighter_off.sh")
		if current_price < self.config['limits']['floor']:
			print(" [Floor --> ON]  ", end ="")
			os.system(self.config["binpath"] + "/floor_on.sh")
		else:
			if self.check_current_override():
				print(" [Floor --> OVERRIDE]  ", end ="")
				os.system(self.config["binpath"] + "/floor_on.sh")
			else:
				print(" [Floor --> OFF] ", end ="")
				os.system(self.config["binpath"] + "/floor_off.sh")
		if current_price < self.config['limits']['charging']:
			print(" [Charging --> ON]")
			os.system(self.config["binpath"] + "/charging_on.sh")
		else:
			print(" [Charging --> OFF]")
			os.system(self.config["binpath"] + "/charging_off.sh")

	def fetch_spot_job(self):
		self.get_config()
		log_file = open(self.config["statepath"] + "/logfile", "a")
		log_file.write(str(datetime.now()))
		log_file.write(" [Fetching spotfile]\n")
		log_file.close()
		spot_prices_url = urlopen(self.config["url"])
		data = json.loads(spot_prices_url.read())
		if len(data) > 10:
			with open(self.config["statepath"] + "/spot_prices.json", "w") as outfile:
				json.dump(data, outfile)
				outfile.close()

	def logger_job(self):
		self.get_config()
		self.get_prices()
		log_file = open(self.config["statepath"] + "/logfile", "a")
		log_file.write(str(datetime.now()))
		log_file.write("  %.2f c/kWh " % self.get_current_price())
		if os.path.exists(self.config["statepath"] + "/fighter_on"):
			log_file.write(" [Heat --> ON]  ")
		else:
			log_file.write(" [Heat --> OFF] ")
		if os.path.exists(self.config["statepath"] + "/floor_on"):
			log_file.write(" [Floor --> ON]  ")
		else:
			log_file.write(" [Floor --> OFF] ")
		if os.path.exists(self.config["statepath"] + "/charging_on"):
			log_file.write(" [Charging --> ON]\n")
		else:
			log_file.write(" [Charging --> OFF]\n")
		log_file.close()


# initialize object and start service
my_powercontrol = PowerControl(sys.argv[1])
my_powercontrol()
