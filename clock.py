from rq import Queue

from service import update
from worker import connection
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()
q = Queue(connection=connection)


@scheduler.scheduled_job('cron', days_of_week='mon-sun', hour=11)
def schedule_update():
    q.enqueue(update)
