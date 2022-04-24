import numpy as np
import cv2
import time

from PIL import ImageGrab as ig
from PIL import Image

import common.led_controller as LED

from .screenshot import screenshot

def show_screen(screen):
    cv2.imshow("test", np.array(screen))

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        return True

def capture_loop(do_show_screen=False, monitor=1, brightness=1.0, change_threshold=20, verbose=0):
    """
    Capture screen and send updates to the LED controller.

    do_show_screen: whether to show a preview of the screen
    monitor: monitor id to capture
    brightenss: float between 0 and 1 that determines the brightness
    change_threshold: do not update color if the difference between the old and new color is below this value
    """

    prev_color = np.array([0, 0, 0])

    while(LED.is_connected()):
        screen = screenshot(mon=monitor)

        if not screen:
            if verbose:
                print('No such monitor.')
            
            break
        
        resized = screen.resize((1, 1), Image.ANTIALIAS)
        
        color = np.array(resized.getpixel((0, 0)))
        color = (color * brightness)
        color = color.astype(int)

        diff = abs(sum(color - prev_color))
        
        if diff >= change_threshold:
            LED.set_color(color)
            prev_color = color
        
        if do_show_screen:
            if show_screen(screen):
                break