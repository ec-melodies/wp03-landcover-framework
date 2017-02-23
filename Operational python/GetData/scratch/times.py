__author__ = 'Jane'

import datetime as dt
import pytz
import calendar
import time

now = dt.date.today()
utc = pytz.utc
central = pytz.timezone('US/Central')
print central
print type(central)

print(calendar.day_name[now.weekday()])
now = dt.datetime.now()
print 'now is  ' + str(now) + ' with daylight savings'
utcnow = dt.datetime.utcnow()
print 'UTC now is  ' + str(utcnow)
print utcnow.tzinfo
print utcnow.tzname()

print 'now localised to UTC is  ' + str(utc.localize(now, is_dst=True))
print 'now localised to central is  ' + str(central.localize(now))

print 'UTC now localised to central is  ' + str(central.localize(utcnow))
start = dt.time(hour=8)

local = time.localtime()
print (local.tm_isdst)

print ('------------------------')

now = dt.datetime.now(pytz.timezone('Europe/London'))
start = dt.time(8,0,0,0,pytz.timezone('US/Central'))

here = dt.time(now.hour, now.minute, now.second, now.microsecond,
               now.tzinfo)
print now
print now.tzinfo
print start
print start.tzinfo
print here
print here.tzname()

now_central = now.astimezone(pytz.timezone('US/Central'))
print now_central
print now_central.tzname()