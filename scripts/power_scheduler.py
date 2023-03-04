#!/usr/bin/python3

import sys
import json
from apscheduler.schedulers.blocking import BlockingScheduler

if len(sys.argv) != 2:
	print("Just one argument is needed, the configuration file")
	sys.exit()

config_file = open(sys.argv[1])
config = json.load(config_file)
config_file.close()

# Start the scheduler
sched = BlockingScheduler()

def scheduler_job():
	print("Job executed")

# Schedule the job to run once each minute
sched.add_job(scheduler_job, 'cron', minute='0-59')
sched.start()

