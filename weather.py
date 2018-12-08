import config
import json
import schedule
import threading
import time
import logging
import requests
from datetime import datetime

log = logging.getLogger(config.logname)
lock = threading.Lock()

'''
https://darksky.net/dev/account

86694a53b9db9c37a58ca1ceecfd8c20

http://darkskyapp.github.io/skycons/

https://api.darksky.net/forecast/86694a53b9db9c37a58ca1ceecfd8c20/37.3472892,-121.9840828?exclude=minutely,hourly,alerts,flags

'''

URL="https://api.darksky.net/forecast/86694a53b9db9c37a58ca1ceecfd8c20/37.3472892,-121.9840828?exclude=minutely,hourly,alerts,flags"

g_stop = False
g_thread = None

def get_weather_info(d):
    lock.acquire()
    log.debug("get weather info")

    try:
        log.debug("read lock")
        with open(".weather.json", "r") as f:
            info = json.load(f)
            d["weather"] = info
    finally:
        lock.release()

def get_localtime(s):
    ts = int(s)
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def update_weather_info():
    try_count = 0
    log.info("=======================   start updating weather")

    while True:
        try:
            res = requests.get(URL)
            log.info("Access " + URL)

            if res.status_code != 200:
                log.error("fail to get weather result. res=%s", res.status_code)
            else:
               # print res.json()
                break
        except Exception as e:
            log.error(e.message)

        try_count += 1
        if try_count > MAX_TRY:
            log.error("Finally give up getting weather update. ")
            return
    
    log.info("Get weather update successfully")

    s = res.json()
    info = {
            "latitude" : s["latitude"],
            "longitude" : s["longitude"],
            "timezone": s["timezone"],
            "cur_time" : get_localtime(s["currently"]["time"]),
            "cur_temperature": int(s["currently"]["temperature"]),
#            "icon": s["currently"]["icon"],
#            "icon": s["daily"]["data"][0]["icon"],
			"icon": s["daily"]["icon"],
            "daily_max": int(s["daily"]["data"][0]["temperatureHigh"]),
            "daily_min": int(s["daily"]["data"][0]["temperatureLow"]),
            "daily_summary" : s["daily"]["data"][0]["summary"]

        }

 #   out =  json.dumps(info)

    lock.acquire()

    try:
        log.debug("write lock")
        with open(".weather.json", "w") as f:
            json.dump(info, f, indent=4, sort_keys=True)
    finally:
        lock.release()

def run():
    while not g_stop:
        schedule.run_pending()
        time.sleep(1)


def start(min=15):
    if min < 10 or min > 60:
        min = 15
    
    g_stop = False
    update_weather_info()
    log.info("start weather update scheduler")
    schedule.every(min).minutes.do(update_weather_info)
    g_thread = threading.Thread(target=run)
    g_thread.start()

    return 


def stop():
    if not g_thread:
        return

    g_stop = True
    g_thread.join()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s.%(funcName)s %(levelname)s %(message)s')
    start(1)
    d = {}
    while True:
        get_weather_info(d)
        print "\n\n"
        print d
        time.sleep(10)
