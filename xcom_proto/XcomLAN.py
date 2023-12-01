#! /usr/bin/env python3

##
# Class abstracting Xcom-LAN UDP network protocol
##

import socket
import logging
from concurrent.futures import ThreadPoolExecutor
from .parameters import ERROR_CODES
from .XcomAbs import XcomAbs

class Package:
    def __init__(self, data):
        self.data = data

    def getBytes(self):
        # Convert data to bytes (replace with your actual serialization logic)
        return str(self.data).encode()

class XcomLAN(XcomAbs):

    def __init__(self, serverIP: str, dstPort=4002, srcPort=4001):
        """
        Package requests are being sent to serverIP : dstPort using TCP protocol.

        Package requests are being sent to serverIP : dstPort using UDP protocol.

        The srcPort is needed, because XcomLAN will send the UDP response NOT
        to the corresponding UDP source endpoint (like every fucking server on this
        planet would do) but rather to <yourIP> : srcPort.

        So in order to make this work, we need to listen on srcPort for incoming
        data.
        """

        self.serverAddress = (serverIP, dstPort)
        self.clientPort = srcPort
        self.localPort = localPort
        self.log = logging.getLogger("XcomLAN")

        self.tcpListener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpListener.bind(("", self.localPort))
        self.tcpListener.listen(1)

    def sendPackage(self, package: Package) -> Package:
        data: bytes = package.getBytes()

        with ThreadPoolExecutor() as listener, \
                socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sender:
            self.log.debug(f" --> {data.hex()}")

            future = listener.submit(self._awaitTCPResponse, self.tcpListener)

            sender.connect(self.serverAddress)
            sender.sendall(data)

            connection, address = future.result(10)
            value = connection.recv(256)
            connection.close()

            self.log.debug(f" <-- {value}")

        if not value:
            raise ValueError("Package listener returned None")

        retPackage = Package.parseBytes(value)
        self.log.debug(retPackage)

        if err := retPackage.getError():
            errCode = ERROR_CODES.get(err, "UNKNOWN ERROR")
            raise KeyError("Error received", errCode)

        return retPackage

    def _awaitTCPResponse(self, tcpListener: socket.socket) -> tuple:
        try:
            connection, address = tcpListener.accept()
        except socket.timeout:
            self.log.error("Waiting for response from XcomLAN timed out")
            raise

        return connection, address


