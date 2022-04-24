import os
import sys
import time

from .magic_home import MagicHomeApi, DEVICE_RGB_WW
from .colors import parse_color, random_color

IP = '10.10.123.3'

controller = None

def init_controller(verbose=0):
    global controller

    controller = MagicHomeApi(IP, DEVICE_RGB_WW, verbose=verbose)

def on():
    controller.turn_on()

def off():
    controller.turn_off()

def set_color(c):
    r, g, b = parse_color(c)

    controller.update_device(r=r, g=g, b=b, white1=255)

def is_connected():
    global controller
    
    return controller.connected

if __name__ == '__main__':
    off()
    time.sleep(1)
    on()
    time.sleep(1)

    set_color(random_color())
    
