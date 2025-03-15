#!/usr/bin/python3

import os
import sys
import json
import time
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from dateutil import parser
from datetime import datetime
from datetime import timedelta
from urllib.request import urlopen

if len(sys.argv) != 2:
	print("Just one argument is needed, the configuration file")
	sys.exit()

class PowerControl:
	config_file_name = ""
	config = {}
	prices = {}
	power_per_minute = 0.0
	power_per_hour = 0.0
	sched = BlockingScheduler()

	def __init__(self, filename):
		self.config_file_name = filename
		self.get_config()

		self.write_to_log("[Starting powercontrol]")

		# Before starting, always fetch the spot prices once
		self.read_remote_url()
		self.get_prices()

		# Schedule the powercontrol job to run once each minute
		self.sched.add_job(self.powercontrol_job, 'cron', minute='0-59')

		# Schedule the fetch_spot job to run once per day
		self.sched.add_job(self.fetch_spot_job, 'cron', hour='14', minute='2')

		# Schedule the logger job to run once per hour
		self.sched.add_job(self.logger_job, 'cron', hour='0-23', minute='1')

		# All set up
		self.write_to_log("[Started]")

		# Start the cronjobs
		self.sched.start()

	def write_to_log(self, line):
		log_file = open(self.config["statepath"] + "/logfile", "a")
		log_file.write(str(datetime.now()))
		log_file.write(" " + str(line) + "\n")
		log_file.close()

	def get_config(self):
		config_file = open(self.config_file_name)
		self.config = json.load(config_file)
		config_file.close()

	def get_prices(self):
		try:
			price_file = open(self.config["statepath"] + "/spot_prices.json")
			self.prices = json.load(price_file)
			price_file.close()
		except:
			self.prices = [{"DateTime": "2000-01-01T00:00:00+02:00",
					"PriceNoTax": 0.0,
					"PriceWithTax": 0.0}]

	def get_power_consumption(self):
		try:
			power_file = open(self.config["statepath"] + "/power_per_minute")
			self.power_per_minute = float(power_file.read())
			power_file.close()
		except:
			self.power_per_minute = 0.0

	def get_seasonal_price(self, now):
		if self.config["pricing"]["seasonal_pricing"]:
			if now.month > 10 or now.month < 4:
				if now.weekday() < 6:
					if now.hour > 6 and now.hour < 22:
						return self.config["pricing"]["winter_day"], True
			return self.config["pricing"]["other"], False
		return 0.0, False

	def get_current_price(self):
		now = datetime.now()
		for n in self.prices:
			item = parser.parse(n["DateTime"])
			if item.day == now.day and item.hour == now.hour:
				price, winter_day = self.get_seasonal_price(now)
				return n["PriceWithTax"] * 100 + price, winter_day
			# If the hourly price is not found, return quite high price just in case
		return 100.0, False

	def check_current_override(self):
		if self.config['override'] == False:
			return False
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
		self.get_power_consumption()
		self.power_per_hour = self.power_per_hour + self.power_per_minute
		current_price, winter_day = self.get_current_price()
		now = datetime.now()
		print(now, end ="   ")
		print("%.2f c/kWh   " % current_price, end ="")
		print("[winter day: %s]   " % winter_day, end ="")
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
			print(" [Charging --> ON]", end ="")
			os.system(self.config["binpath"] + "/charging_on.sh")
		else:
			print(" [Charging --> OFF]", end ="")
			os.system(self.config["binpath"] + "/charging_off.sh")
		print("   %.2f Wh" % self.power_per_minute)

	def read_remote_url(self):
		self.write_to_log("[Fetching spotfile]")
		try:
			spot_prices_url = urlopen(self.config["url"])
			data = json.loads(spot_prices_url.read())
		except:
			self.write_to_log(" --> Error reading JSON data")
			return False, {}
		with open(self.config["statepath"] + "/spot_prices.json", "w") as outfile:
			json.dump(data, outfile)
			outfile.close()
		self.write_to_log(" --> Price file written")
		return True, data

	def fetch_spot_job(self):
		self.get_config()
		self.get_prices()
		success, data = self.read_remote_url()
		if not success:
			# Reschedule the fetch_spot job to run in 5 minutes
			self.write_to_log(" --> Rescheduling JSON fetching")
			retry = datetime.now(pytz.UTC) + timedelta(minutes=5)
			self.sched.add_job(self.fetch_spot_job, 'date', run_date=retry)
		else:
			if data[-1]["DateTime"] == self.prices[-1]["DateTime"]:
				# Reschedule the fetch_spot job to run in 15 minutes
				self.write_to_log(" --> No new prices, Rescheduling JSON fetching")
				retry = datetime.now(pytz.UTC) + timedelta(minutes=15)
				self.sched.add_job(self.fetch_spot_job, 'date', run_date=retry)
			else:
				self.write_to_log(" --> Taking new prices in use")

	def logger_job(self):
		self.get_config()
		self.get_prices()
		current_price, winter_day = self.get_current_price()
		log_file = open(self.config["statepath"] + "/logfile", "a")
		log_file.write(str(datetime.now()))
		log_file.write("  %.2f c/kWh " % current_price)
		log_file.write("[winter day: %s]   " % winter_day)
		if os.path.exists(self.config["statepath"] + "/fighter_on"):
			log_file.write(" [Heat --> ON]  ")
		else:
			log_file.write(" [Heat --> OFF] ")
		if os.path.exists(self.config["statepath"] + "/floor_on"):
			log_file.write(" [Floor --> ON]  ")
		else:
			log_file.write(" [Floor --> OFF] ")
		if os.path.exists(self.config["statepath"] + "/charging_on"):
			log_file.write(" [Charging --> ON] ")
		else:
			log_file.write(" [Charging --> OFF] ")
		log_file.write(" %.2f Wh\n" % self.power_per_hour)
		self.power_per_hour = 0.0
		log_file.close()


# initialize object and start service
my_powercontrol = PowerControl(sys.argv[1])
my_powercontrol()
