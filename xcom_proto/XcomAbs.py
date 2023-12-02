#! /usr/bin/env python3

##
# Abstract base class used by various implementations of the Xcom protocol
##

import logging

from abc import ABC, abstractmethod

from .parameters import *
from .protocol import Package

MSG_MAX_LENGTH = 256 # from Xcom Proto Documentation

class XcomAbs(ABC):

    def __init__(self):
        self.log = logging.getLogger("XcomAbs")

    def getValueByID(self, id: int, type: str, dstAddr=100, propertyID=QSP_UNSAVED_VALUE):
        return self.getValue(Datapoint(id, "", type), dstAddr, propertyID)

    def getValue(self, parameter: Datapoint, dstAddr=100, propertyID=QSP_UNSAVED_VALUE):
        self.log.debug(f"requesting value {parameter}")

        objectType = TYPE_PARAMETER

        if 3000 <= parameter.id <= 3168:
            objectType = TYPE_INFO
        elif parameter.id >= 7000:
            objectType = TYPE_INFO
        
        request: Package = Package.genPackage(
            service_id=PROPERTY_READ,
            object_id=parameter.id,
            object_type=objectType,
            property_id=propertyID,
            property_data=b'',
            dst_addr=dstAddr
        )

        response: Package = self.sendPackage(request)

        return parameter.unpackValue(response.frame_data.service_data.property_data)        

    def setValue(self, parameter: Datapoint, value, dstAddr=100, propertyID=QSP_UNSAVED_VALUE):
        self.log.debug(f"setting value {parameter}")

        request: Package = Package.genPackage(
            service_id=PROPERTY_WRITE,
            object_id=parameter.id,
            object_type=TYPE_PARAMETER,
            property_id=propertyID,
            property_data=parameter.packValue(value),
            dst_addr=dstAddr
        )

        self.sendPackage(request)

    ## TODO
    #def setProperty():
    #    raise NotImplementedError
    

    @abstractmethod
    def sendPackage(self, package: Package)  -> Package:
        raise NotImplementedError