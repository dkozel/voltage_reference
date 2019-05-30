#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, sys

import csv
from datetime import datetime, tzinfo, timedelta
import ntplib
from yoctopuce.yocto_api import *
from yoctopuce.yocto_temperature import *
from yoctopuce.yocto_humidity import *
from yoctopuce.yocto_pressure import *

# Setup Timezone data
class simple_utc(tzinfo):
    def tzname(self, **kwargs):
        return "UTC"
    def utcoffset(self, dt):
        return timedelta(0)

# Check that system time is reasonable
ntpclient = ntplib.NTPClient()
response = ntpclient.request('europe.pool.ntp.org', version=3)
print("System time is offset from NTP by %s seconds" % response.offset)

if abs(response.offset) > 1:
    sys.exit("System time is offset from NTP by %s seconds" % response.offset)

# Setup the API to use local USB devices
errmsg = YRefParam()
if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
    sys.exit("init error" + errmsg.value)

# Connect to Maxi Thermistor and Meteo boards
thermistor_sn = "THRMSTR2-F266D"
thermistor_module = YModule.FindModule(thermistor_sn)

if not thermistor_module.isOnline():
    sys.exit('Maxi Thermistor module not connected')

meteo_sn = "METEOMK2-FFF4B"
meteo_module = YModule.FindModule(meteo_sn)

if not meteo_module.isOnline():
    sys.exit('Meteo device not connected')

# Connect to the sensors
tempSensor1 = YTemperature.FindTemperature(thermistor_sn + '.temperature1')
tempSensor2 = YTemperature.FindTemperature(thermistor_sn + '.temperature2')
tempSensor3 = YTemperature.FindTemperature(thermistor_sn + '.temperature3')

roomTempSensor     = YTemperature.FindTemperature(meteo_sn + '.temperature')
roomPressureSensor = YPressure.FindPressure(meteo_sn + '.pressure')
roomHumiditySensor = YHumidity.FindHumidity(meteo_sn + '.humidity')

# Read current values as a sanity check
print("Current sensor values:")
if thermistor_module.isOnline():
    print('%2.1f°C %2.1f°C %2.1f°C' % (
         tempSensor1.get_currentValue(),
         tempSensor2.get_currentValue(),
         tempSensor3.get_currentValue()
         ))

if meteo_module.isOnline():
    print('%2.1f°C %4.0fmB° %2.1f%%' % (
         roomTempSensor.get_currentValue(),
         roomPressureSensor.get_currentValue(),
         roomHumiditySensor.get_currentValue()
         ))


timestamp = datetime.datetime.utcnow().replace(tzinfo=simple_utc()).isoformat()
with open("%s_data.csv" % timestamp, mode='w') as data_file:
    fieldNames = ['datetime', 'humidity', 'pressure', 'roomTemp', 'temp1', 'temp2', 'temp3']
    data_writer = csv.DictWriter(data_file, fieldNames, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    data_writer.writeheader()

    timestamp = datetime.datetime.utcnow().replace(tzinfo=simple_utc()).isoformat()
    measurement = {
            'datetime': timestamp,
            'humidity': roomHumiditySensor.get_currentValue(),
            'pressure': roomPressureSensor.get_currentValue(),
            'roomTemp': roomTempSensor.get_currentValue(),
            'temp1': tempSensor1.get_currentValue(),
            'temp2': tempSensor2.get_currentValue(),
            'temp3': tempSensor3.get_currentValue()
            }
    
    data_writer.writerow(measurement)

YAPI.FreeAPI()
