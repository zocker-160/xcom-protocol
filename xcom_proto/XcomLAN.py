#! /usr/bin/env python3

##
# Class abstracting Xcom-LAN UDP network protocol
##

import socket
import logging

from concurrent.futures import ThreadPoolExecutor

from .parameters import ERROR_CODES
from .protocol import Package
from .XcomAbs import XcomAbs


class XcomLAN(XcomAbs):

    def __init__(self, serverIP: str, dstPort = 4001, srcPort = 4002):
        """
        Package requests are being sent to serverIP : dstPort using UDP protocol.

        The srcPort is needed, because XcomLAN will send the UDP response NOT
        to the corresponding UDP source endpoint (like every fucking server on this
        planet would do) but rather to <yourIP> : srcPort which seems to be
        hard coded in the XcomLAN configuration (I think).

        So in order to make this work, we need to listen on srcPort for incoming
        answers.
        """

        self.serverAddress = (serverIP, dstPort)
        self.clientPort = srcPort
        self.log = logging.getLogger("XcomLAN")

        self.udpListener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpListener.bind(("", self.clientPort))
        self.udpListener.settimeout(2) # as recommended by Studer Xcom documentation

    def sendPackage(self, package: Package) -> Package:
        data: bytes = package.getBytes()
        
        with ThreadPoolExecutor() as listener, \
                socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            self.log.debug(f" --> {data.hex()}")

            future = listener.submit(self._awaitUDPResponse, self.udpListener)

            sender.sendto(data, self.serverAddress)

            value = future.result(10) 
            self.log.debug(f" <-- {value}")

        if not value:
            raise ValueError("Package listener returned None!")

        retPackage = Package.parseBytes(value)
        self.log.debug(retPackage)

        if err := retPackage.getError():
            errCode = ERROR_CODES.get(err, "UNKNOWN ERROR")
            raise KeyError("Error received", errCode)
        
        return retPackage

    def _awaitUDPResponse(self, udpSocket: socket.socket) -> bytes:
        try:
            response = udpSocket.recv(256)
        except socket.timeout:
            self.log.error("Waiting for response from XcomLAN timed out")
            raise

        return response
