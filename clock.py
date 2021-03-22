from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()


@scheduler.scheduled_job('cron', days_of_week='mon-sun', hour=11)
def update():
    pass
