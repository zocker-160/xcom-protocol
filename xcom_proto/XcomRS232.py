#! /usr/bin/env python3

##
# Class abstracting Xcom-RS232i serial protocol
##

import serial
import logging

from .protocol import Package
from .XcomAbs import XcomAbs


class XcomRS232(XcomAbs):

    def __init__(self,
            serialDevice: str, baudrate: int,
            timeout: int = 2, parity=serial.PARITY_EVEN):
        """
        :param serialDevice: e.g. "/dev/ttyUSB0"
        :param baudrate:     e.g. 38400 (default Xcom-232i) or 115200 if reconfigured
        :param timeout:      serial read timeout in seconds
        :param parity:       serial parity; Xcom-232i requires EVEN (8E1)
        """
        self.serialDevice = serialDevice
        self.baudrate = baudrate
        self.timeout = timeout
        self.parity = parity
        self.log = logging.getLogger("XcomRS232")

    def sendPackage(self, package: Package) -> Package:
        data: bytes = package.getBytes()

        with serial.Serial(
                self.serialDevice,
                self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=self.parity,
                stopbits=serial.STOPBITS_ONE,
                timeout=self.timeout) as ser:

            ser.reset_input_buffer()
            self.log.debug(f" --> {data.hex()}")
            ser.write(data)
            ser.flush()

            retPackage = Package.parse(ser)
            self.log.debug(retPackage)

        if err := retPackage.getError():
            raise KeyError("Error received", err)

        return retPackage
