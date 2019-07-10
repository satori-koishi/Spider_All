import os


def fun_min():
    os.system('scrapy crawl HigWayPersonSupervisor')


fun_min()
# sched.add_job(fun_min, 'interval', hours=24)
# sched.start()
