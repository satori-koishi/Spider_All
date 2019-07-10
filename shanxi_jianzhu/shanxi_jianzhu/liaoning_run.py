import os

from apscheduler.schedulers.blocking import BlockingScheduler
sched = BlockingScheduler()

def fun_min():
    os.system('scrapy crawl Liaoning')
fun_min()
sched.add_job(fun_min, 'interval', hours=24)
sched.start()