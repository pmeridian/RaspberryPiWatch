# Copyright (c) 2017 Adafruit Industries
# Author: Tony DiCola & James DeVito
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import sys
import time
import datetime
import random 
import SDL_DS3231

from w1thermsensor import W1ThermSensor
sensor = W1ThermSensor()
sensor.set_precision(12)

from Adafruit_BME280 import *
bmp_sensor = BME280(t_mode=BME280_OSAMPLE_1, p_mode=BME280_OSAMPLE_1, h_mode=BME280_OSAMPLE_1)
bmp_sensor.sleepMode()

import Adafruit_DHT

import subprocess

# Raspberry Pi pin configuration:
RST = None     # on the PiOLED this pin isnt used
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# Beaglebone Black pin configuration:
# RST = 'P9_12'
# Note the following are only used with SPI:
# DC = 'P9_15'
# SPI_PORT = 1
# SPI_DEVICE = 0

# 128x32 display with hardware I2C:
#disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

# 128x64 display with hardware I2C:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)

# Note you can change the I2C address by passing an i2c_address parameter like:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)

# Alternatively you can specify an explicit I2C bus number, for example
# with the 128x32 display you would use:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=2)

# 128x32 display with hardware SPI:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# 128x64 display with hardware SPI:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

# Alternatively you can specify a software SPI implementation by providing
# digital GPIO pin numbers for all the required display pins.  For example
# on a Raspberry Pi with the 128x32 display you might use:
# disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, dc=DC, sclk=18, din=25, cs=22)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
#font = ImageFont.truetype('Minecraft.ttf', 8)

ds3231 = SDL_DS3231.SDL_DS3231(1, 0x68, 0x57)


mongoUpload = False
mongoDB='mongodb://192.168.1.11:27017/'

while True:

    # Draw a black filled box to clear the image.
    draw.rectangle((0,0,width,height), outline=0, fill=0)

    # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    cmd = "hostname -I | cut -d\' \' -f1"
    IP = subprocess.check_output(cmd, shell = True )
    cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
    CPU = subprocess.check_output(cmd, shell = True )
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'"
    MemUsage = subprocess.check_output(cmd, shell = True )
    cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
    Disk = subprocess.check_output(cmd, shell = True )

    ds3231_date=str(ds3231.read_datetime())
    ds3231_temp=ds3231.getTemp()
    rtc_time = str(ds3231_date)
    rtc_temp = "DS3231_T:%4.1f"%ds3231_temp

    ds18b20_t=sensor.get_temperature()
    ds18b20_temp = "DS18B20_T:%5.2f"%ds18b20_t
#    ds18b20_temp = "DS18B20_T:%5.2f"%0.

    bmp_sensor.takeForcedModeMeasurement()
    bmp280_t=bmp_sensor.read_temperature()
    bmp280_p=bmp_sensor.read_pressure()/100
    bmp280_temp = "BMP280_T:%5.2f"%bmp280_t
    bmp280_pressure = "BMP280_P:%5.1f"%(bmp280_p)

    dht22_h, dht22_t = Adafruit_DHT.read_retry( Adafruit_DHT.AM2302, 22)
    dht22_temp = "DHT22_T:%5.2f"%dht22_t
    dht22_hum = "DHT22_H:%4.1f"%dht22_h

    print ds3231_date,bmp280_temp,bmp280_pressure,ds18b20_temp,dht22_temp,dht22_hum

    if (mongoUpload):
        docu = {
            "rtc_time":ds3231_date,
            "rtc_temp":ds3231_temp,
            "ds18b20_temp":ds18b20_t,
            "bmp280_temp":bmp280_t,
            "bmp280_pressure":bmp280_p,
        }
        try:
            from pymongo import MongoClient
            # client MongoDB
            client = MongoClient(mongoDB)
            # open database messages
            db = client.sensors
            # adding the data in the collection
            db.ReceivedData.insert_one(docu)
        except Exception as e:
            print("MongoDB: can not add document in MongoDB: " + str(e))
            
    draw.text((x, top),    rtc_time,  font=font, fill=255)
    draw.text((x, top+8),       "IP: " + str(IP),  font=font, fill=255)
    draw.text((x, top+16),     str(CPU), font=font, fill=255)
#    draw.text((x, top+24),    str(MemUsage),  font=font, fill=255)
#    draw.text((x, top+24),    str(Disk),  font=font, fill=255)
#    draw.text((x, top+24),    rtc_temp,  font=font, fill=255)
    draw.text((x, top+24),    dht22_temp,  font=font, fill=255)
    draw.text((x, top+32),    ds18b20_temp,  font=font, fill=255)
    draw.text((x, top+40),    bmp280_temp,  font=font, fill=255)
    draw.text((x, top+48),    bmp280_pressure,  font=font, fill=255)
    draw.text((x, top+56),    dht22_hum,  font=font, fill=255)
    
    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(30)
