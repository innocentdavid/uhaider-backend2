# import time

# expiration_time_seconds=int(time.time()) + 3600 # time in seconds < 3600 for 1hr >


import datetime

current_datetime = datetime.datetime.now()
expiration_time_seconds = current_datetime + datetime.timedelta(hours=24)
