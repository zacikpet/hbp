import os
import time
import schedule


def update():
    os.system('flask update --trigger=auto')


schedule.every().day.at("10:30").do(update)


# Check every 5 minutes if update should be ran
while True:
    schedule.run_pending()
    time.sleep(300)
