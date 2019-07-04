"""
This module runs project [app.py] with different interval and also runs bot telegram for adding users.
Main part of our application is app.py module.
This script
"""

import os
import time
import settings
import logging

logging.basicConfig(filename=settings.NAME_LOG_FILE,
                    level=logging.INFO,
                    filemode='w',
                    format='%(asctime)s - %(threadName)10s -  %(levelname)8s - %(name)30s  - %(message)s')
import contact
from threading import Thread
from datetime import datetime
from datetime import timedelta


def run():
    logger = logging.getLogger('Run')
    bot = contact.TBotNotify(settings.BOT_TOKEN)
    try:
        logger.info('Start thread RUN ------------------------')
        thread = Thread(target=bot.start)
        thread.start()
    except Exception as exc:
        print(exc)

    # every 4 hours for running app.py
    # interval = timedelta(hours=4) # timedelta(minutes=5)
    interval = timedelta(seconds=3) # timedelta(minutes=5)
    # interval = timedelta(minutes=3) # timedelta(minutes=5)
    # future_date = datetime(year=2018, month=10, day=3, hour=13, minute=59)
    curr_time = datetime.now()
    print(curr_time)
    future_date = curr_time + interval
    # future_date = future_date.replace(minute=0, second=0)
    print(future_date)
    os.system('C:/Python36/python.exe app.py')

    while (True):
        curr_time = datetime.now()
        if curr_time >= future_date:
            os.system('C:/Python36/python.exe app.py')
            future_date = curr_time + interval
            # future_date = future_date.replace(minute=0, second=0)
            print(future_date)


        time.sleep(1)


if __name__ == '__main__':
    run()
