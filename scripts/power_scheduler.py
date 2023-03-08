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

# Start the scheduler
sched = BlockingScheduler()

def get_config():
	config_file = open(sys.argv[1])
	config = json.load(config_file)
	config_file.close()
	return config

def get_prices(config):
	price_file = open(config["statepath"] + "/spot_price.json")
	prices = json.load(price_file)
	price_file.close()
	return prices

def get_current_price(config):
	prices = get_prices(config)
	now = datetime.now()
	for n in prices:
		price = parser.parse(n["DateTime"])
		if price.day == now.day and price.hour == now.hour:
			return n["PriceWithTax"] * 100
	# If the hourly price is not found, return quite high price just in case
	return 100.0

def check_current_override(now, config):
	min_a = 100
	min_b = 100
	min_c = 100
	min_d = 100
	hour_a = 0
	hour_b = 0
	hour_c = 0
	hour_d = 0
	prices = get_prices(config)
	for n in prices:
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

def powercontrol_job():
	config = get_config()
	current_price = get_current_price(config)
	now = datetime.now()
	print(now, end ="   ")
	print(current_price, end ="   ")
	if current_price < config['limits']['heat']:
		print(" [Heat --> ON]  ", end ="")
		os.system(config["binpath"] + "/fighter_on.sh")
	else:
		if check_current_override(now, config):
			print(" [Heat --> OVERRIDE]  ", end ="")
			os.system(config["binpath"] + "/fighter_on.sh")
		else:
			print(" [Heat --> OFF] ", end ="")
			os.system(config["binpath"] + "/fighter_off.sh")
	if current_price < config['limits']['floor']:
		print(" [Floor --> ON]  ", end ="")
		os.system(config["binpath"] + "/floor_on.sh")
	else:
		if check_current_override(now, config):
			print(" [Floor --> OVERRIDE]  ", end ="")
			os.system(config["binpath"] + "/floor_on.sh")
		else:
			print(" [Floor --> OFF] ", end ="")
			os.system(config["binpath"] + "/floor_off.sh")
	if current_price < config['limits']['charging']:
		print(" [Charging --> ON]")
		os.system(config["binpath"] + "/charging_on.sh")
	else:
		print(" [Charging --> OFF]")
		os.system(config["binpath"] + "/charging_off.sh")

def fetch_spot_job():
	config = get_config()
	log_file = open(config["statepath"] + "/logfile", "a")
	log_file.write(str(datetime.now()))
	log_file.write(" [Fetching spotfile]\n")
	log_file.close()
	spot_prices_url = urlopen(config["url"])
	data = json.loads(spot_prices_url.read())
	if len(data) > 10:
		with open(config["statepath"] + "/spot_price.json", "w") as outfile:
			json.dump(data, outfile)
		outfile.close()

def logger_job():
	config = get_config()
	log_file = open(config["statepath"] + "/logfile", "a")
	log_file.write(str(datetime.now()))
	log_file.write("  %.2f c/kWh " % get_current_price(config))
	if os.path.exists(config["statepath"] + "/fighter_on"):
		log_file.write(" [Heat --> ON]  ")
	else:
		log_file.write(" [Heat --> OFF] ")
	if os.path.exists(config["statepath"] + "/floor_on"):
		log_file.write(" [Floor --> ON]  ")
	else:
		log_file.write(" [Floor --> OFF] ")
	if os.path.exists(config["statepath"] + "/charging_on"):
		log_file.write(" [Charging --> ON]\n")
	else:
		log_file.write(" [Charging --> OFF]\n")
	log_file.close()

# Schedule the powercontrol job to run once each minute
sched.add_job(powercontrol_job, 'cron', minute='0-59')

# Schedule the fetch_spot job to run once per day
sched.add_job(fetch_spot_job, 'cron', hour='17', minute='17')

# Schedule the logger job to run once per hour
sched.add_job(logger_job, 'cron', hour='0-23', minute='1')

# Before starting, always fetch the spot prices once
fetch_spot_job()

# Start the cronjobs
sched.start()
