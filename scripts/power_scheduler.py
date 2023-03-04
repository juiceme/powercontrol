#!/usr/bin/python3

from apscheduler.schedulers.blocking import BlockingScheduler

# Start the scheduler
sched = BlockingScheduler()

def scheduler_job():
	print("Job executed")

# Schedule the job to run once each minute
sched.add_job(scheduler_job, 'cron', minute='0-59')
sched.start()

