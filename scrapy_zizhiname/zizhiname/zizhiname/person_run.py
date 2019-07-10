from scrapy import cmdline
# # from apscheduler.schedulers.blocking import BlockingScheduler
# # sched = BlockingScheduler()
#
def fun_min():
     cmdline.execute('scrapy crawl person_ok'.split())
fun_min()