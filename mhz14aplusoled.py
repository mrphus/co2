#!/usr/bin/env python3

import time
import serial
from lib_oled96 import ssd1306
from smbus import SMBus
from PIL import Image, ImageDraw, ImageFont

class CO2Sensor():
  request = [0xff, 0x01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79]

  def __init__(self, port='/dev/ttyS0'):
    self.serial = serial.Serial(
        port = port,
        baudrate = 9600,
        parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE,
        bytesize = serial.EIGHTBITS,
        timeout = 1
    )

  def get(self):
    self.serial.write(bytearray(self.request))
    response = self.serial.read(9)
    if len(response) == 9:
      current_time = time.strftime('%H:%M:%S', time.localtime())
      return {"time": current_time, "ppa": (response[2] << 8) | response[3], "temp": response[4]}
    return -1

  def get_average(self, duration):
    values = []
    while duration != 0:
      values.append(self.get().get("ppa"))
      duration -= 1
      time.sleep(1)
    return sum(values) // len(values)


def main():
  sensor = CO2Sensor()
  i2cbus = SMBus(1)        # 1 = Raspberry Pi but NOT early REV1 board
  fnt = ImageFont.truetype("FreeSans.ttf", 25)
  oled = ssd1306(i2cbus)   # create oled object, nominating the correct I2C bus, default address
  while True:
    array = sensor.get()
    celsius = (array.get("temp") - 32) * 5.0/9.0
    celsiusAsStr = "{:.0f}".format(celsius)
    value = str(array.get("ppa")) + ' ppm\n' + celsiusAsStr + ' Grad'
    print(value)

    # Printing onto display
    #oled.canvas.rectangle((0, 0, oled.width-1, oled.height-1), outline=1, fill=0)
    oled.cls()
    oled.canvas.multiline_text((5, 10), value, font=fnt, fill=1);

    # now display that canvas out to the hardware
    oled.display()
    time.sleep(1)


if __name__ == '__main__':
  main()
