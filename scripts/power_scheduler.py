#!/usr/bin/python3

import os
import sys
import json
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from dateutil import parser
from datetime import datetime

if len(sys.argv) != 2:
	print("Just one argument is needed, the configuration file")
	sys.exit()

# Start the scheduler
sched = BlockingScheduler()

def scheduler_job():
	config_file = open(sys.argv[1])
	config = json.load(config_file)
	config_file.close()
	price_file = open(config["spotfile"])
	prices = json.load(price_file)
	price_file.close()
	now = datetime.now()
	for n in prices:
		price = parser.parse(n["DateTime"])
		if price.day == now.day and price.hour == now.hour:
			current_price = n["PriceWithTax"] * 100
			print(now, end ="   ")
			print(current_price, end ="   ")
			if current_price < config['limits']['heat']:
				print(" [Heat --> ON]  ", end ="")
				os.system("/home/juice/.local/bin/fighter_on.sh")
			else:
				print(" [Heat --> OFF] ", end ="")
				os.system("/home/juice/.local/bin/fighter_off.sh")
			if current_price < config['limits']['floor']:
				print(" [Floor --> ON]  ", end ="")
				os.system("/home/juice/.local/bin/floor_on.sh")
			else:
				print(" [Floor --> OFF] ", end ="")
				os.system("/home/juice/.local/bin/floor_off.sh")
			if current_price < config['limits']['charging']:
				print(" [Charging --> ON]")
				os.system("/home/juice/.local/bin/charging_on.sh")
			else:
				print(" [Charging --> OFF]")
				os.system("/home/juice/.local/bin/charging_off.sh")

# Schedule the job to run once each minute
sched.add_job(scheduler_job, 'cron', minute='0-59')
sched.start()

