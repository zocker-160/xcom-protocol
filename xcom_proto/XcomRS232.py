#! /usr/bin/env python3

##
# Class abstracting Xcom-RS232i serial protocol (bare Xcom-232i, raw RS-232).
#
# The scom serial protocol is self-delimiting: every frame carries a
# data_length field in its header and contains NO line terminator. A bare
# Xcom-232i on raw RS-232 emits exactly these self-delimited frames and
# requires 8E1 (8 data bits, EVEN parity, 1 stop bit).
#
# NOTE: The CR/LF terminator used by the previous implementation is NOT a
# property of the Xcom-232i. It belongs to the Moxa NPort "Data Packing"
# feature of an Xcom-LAN setup -- and that path is handled separately by the
# XcomLAN classes over TCP/UDP, not here. A Moxa is never in front of this
# serial transport, so there is no CR/LF on this path.
##

import serial
import logging

from .protocol import Package
from .XcomAbs import XcomAbs, MSG_MAX_LENGTH


class XcomRS232(XcomAbs):

    def __init__(self, serialDevice: str, baudrate: int, timeout: int = 2,
                 parity=serial.PARITY_EVEN):
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

        with serial.Serial(self.serialDevice,
                           self.baudrate,
                           bytesize=serial.EIGHTBITS,
                           parity=self.parity,        # EVEN -> 8E1
                           stopbits=serial.STOPBITS_ONE,
                           timeout=self.timeout) as ser:
            ser.reset_input_buffer()
            self.log.debug(f" --> {data.hex()}")
            ser.write(data)
            ser.flush()

            # Package.parse() reads one self-delimited scom frame straight from
            # the serial stream: it scans for the 0xAA start byte, reads the
            # 11-byte header + 2 header-checksum bytes, then data_length body
            # bytes + 2 data-checksum bytes, validating both checksums.
            retPackage = Package.parse(ser)
            self.log.debug(retPackage)

        if err := retPackage.getError():
            raise KeyError("Error received", err)

        return retPackage
