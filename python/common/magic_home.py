"""MagicHome Python API.

Based on https://github.com/adamkempenich/magichome-python

Device types:
0: RGB
1: RGB+WW
2: RGB+WW+CW
3: Bulb (v.4+)
4: Bulb (v.3-)
"""
import socket
import csv
import struct
import datetime
import traceback

MAX_FAIL_COUNT = 10

DEVICE_RGB = 0
DEVICE_RGB_WW = 1
DEVICE_RGB_WW_CW = 2
DEVICE_BULB_4X = 3
DEVICE_BULB_3X = 4

class MagicHomeApi:

    def __init__(self, device_ip, device_type, keep_alive=True, verbose=False):
        self.device_ip = device_ip
        self.device_type = device_type
        self.API_PORT = 5577
        self.latest_connection = datetime.datetime.now()
        self.keep_alive = keep_alive
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.settimeout(3)
        self.verbose = verbose
        self.fail_count = 0
        self.connected = False
        
        self.connect()
        

    def connect(self):
        try:
            if self.verbose:
                print("Establishing connection with the device.")
            
            self.s.connect((self.device_ip, self.API_PORT))
            self.connected = True

        except socket.error as exc:
            if self.verbose:
                print(f"Caught exception socket.error : {exc}")
            
            if self.s:
                self.s.close()

            self.connected = False

    def set_verbose(self, val):
        self.verbose = val
        
    def turn_on(self):
        self.send_bytes(0x71, 0x23, 0x0F, 0xA3) if self.device_type < DEVICE_BULB_3X else self.send_bytes(0xCC, 0x23, 0x33)

    def turn_off(self):
        self.send_bytes(0x71, 0x24, 0x0F, 0xA4) if self.device_type < DEVICE_BULB_3X else self.send_bytes(0xCC, 0x24, 0x33)

    def get_status(self):
        if self.device_type == DEVICE_RGB_WW_CW:
            self.send_bytes(0x81, 0x8A, 0x8B, 0x96)
            return self.s.recv(15)
        else:
            self.send_bytes(0x81, 0x8A, 0x8B, 0x96)
            return self.s.recv(14)

    def update_device(self, r=0, g=0, b=0, white1=None, white2=None):
        """Updates a device based upon what we're sending to it.

        Values are excepted as integers between 0-255.
        """
        if self.verbose > 1:
            print("update:", (r, g, b))

        if self.device_type <= DEVICE_RGB_WW:
            # Update an RGB or an RGB + WW device
            white1 = self.check_number_range(white1)
            message = [0x31, r, g, b, white1, 0x00, 0x0f]
            self.send_bytes(*(message+[self.calculate_checksum(message)]))

        elif self.device_type == DEVICE_RGB_WW_CW:
            # Update an RGB + WW + CW device
            message = [0x31,
                       self.check_number_range(r),
                       self.check_number_range(g),
                       self.check_number_range(b),
                       self.check_number_range(white1),
                       self.check_number_range(white2),
                       0x0f, 0x0f]
            self.send_bytes(*(message+[self.calculate_checksum(message)]))

        elif self.device_type == DEVICE_BULB_4X:
            # Update the white, or color, of a bulb
            if white1 is not None:
                message = [0x31, 0x00, 0x00, 0x00,
                           self.check_number_range(white1),
                           0x0f, 0x0f]
                self.send_bytes(*(message+[self.calculate_checksum(message)]))
            else:
                message = [0x31,
                           self.check_number_range(r),
                           self.check_number_range(g),
                           self.check_number_range(b),
                           0x00, 0xf0, 0x0f]
                self.send_bytes(*(message+[self.calculate_checksum(message)]))

        elif self.device_type == DEVICE_BULB_3X:
            # Update the white, or color, of a legacy bulb
            if white1 != None:
                message = [0x56, 0x00, 0x00, 0x00,
                           self.check_number_range(white1),
                           0x0f, 0xaa, 0x56, 0x00, 0x00, 0x00,
                           self.check_number_range(white1),
                           0x0f, 0xaa]
                self.send_bytes(*(message+[self.calculate_checksum(message)]))
            else:
                message = [0x56,
                           self.check_number_range(r),
                           self.check_number_range(g),
                           self.check_number_range(b),
                           0x00, 0xf0, 0xaa]
                self.send_bytes(*(message+[self.calculate_checksum(message)]))
        elif self.verbose:
            print("Incompatible device type received...")

    def check_number_range(self, number):
        """Check if the given number is in the allowed range."""
        if number < 0:
            return 0
        elif number > 255:
            return 255
        else:
            return number

    def send_preset_function(self, preset_number, speed):
        """Send a preset command to a device."""
        # Presets can range from 0x25 (int 37) to 0x38 (int 56)
        if preset_number < 37:
            preset_number = 37
        if preset_number > 56:
            preset_number = 56
        if speed < 0:
            speed = 0
        if speed > 100:
            speed = 100

        if self.device_type == DEVICE_BULB_3X:
            self.send_bytes(0xBB, preset_number, speed, 0x44)
        else:
            message = [0x61, preset_number, speed, 0x0F]
            self.send_bytes(*(message+[self.calculate_checksum(message)]))

    def calculate_checksum(self, _bytes):
        """Calculate the checksum from an array of bytes."""
        return sum(_bytes) & 0xFF

    def _send(self, *_bytes):
        try:
            self.s.send(struct.pack("B"*len(_bytes), *_bytes))
        except socket.error as e:
            if self.verbose:
                print(f"Caught exception socket.error : {e}")
                traceback.print_exc()

            self.fail_count += 1

            if self.fail_count >= MAX_FAIL_COUNT:
                print("Maximum fail count reached, exiting.")
                
                try:
                    self.c.close()
                except:
                    pass

                self.connected = False

            return False

        return True

    def send_bytes(self, *_bytes):
        """Send commands to the device.

        If the device hasn't been communicated to in 5 minutes, reestablish the
        connection.
        """
        check_connection_time = (datetime.datetime.now() - self.latest_connection).total_seconds()

        if self._send(*_bytes):
            
            if not self.keep_alive and self.s:
                self.s.close()

        else:
            if check_connection_time >= 60*5:
                if self.verbose:
                    print("Connection timed out, reestablishing.")
                
                self.connect()
                
                if not self._send(*_bytes):
                    print("Failed to communicate with LED controller.")