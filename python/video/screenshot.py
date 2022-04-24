import mss
import mss.tools

import numpy as np
import cv2

from PIL import Image


def screenshot(mon=1):
    with mss.mss() as sct:
        for num, monitor in enumerate(sct.monitors[1:], 1):
            if num == mon:
                sct_img = sct.grab(monitor)

                img = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
                
                return img