#! /usr/bin/env python3

import os
import struct
import sys
import time
import serial

from . import constants as constants
from .controller import Requestpackage

class RS232_IO:
    def __init__(self, socket_device: str, baudrate: int, timeout=2):        
        self.socket_device = socket_device
        self.baudrate = baudrate
        self.timeout = timeout

    def get_value(self, parameter, property_id=constants.UNSAVED_VALUE_QSP):
        parameter = parameter.id

        print("PARAM:", parameter)

        if parameter >= 7000:
            object_type = constants.TYPE_INFO
        else:
            object_type = constants.TYPE_PARAMETER

        parameter = struct.pack("<I", parameter)
        package = Requestpackage(
            data_length=b'\x0A\x00',
            service_id=constants.READ_PROPERTY,
            object_id=parameter,
            property_id=property_id,
            property_data=b'',
            object_type=object_type
        )

        with serial.Serial(self.socket_device, self.baudrate, timeout=self.timeout) as ser:
            ser.write(package.get_binary())

            print("request:", package.get_binary().hex())

            #################### TODO: implement proper package reading ####################
            response = ser.read_until(expected=constants.RS232_TERM, size=100)

            if len(response) == 0:
                raise ConnectionError("ERROR: Response was empty")

            #response = ser.read_all()
            # remove terminator (2 bytes 0D 0A)
            response = response[:-2]

        # dirty bugfix, TODO: proper solution
        if response[:1] == b'\xff':
            response = response[1:]

        print("response:", response.hex())

        return_code = response[14:15]

        print("return code:", return_code)

        if return_code == b'\x02':
            pass # everything is fine
        elif return_code == b'\x03':
            error_code = response[24:26]
            raise KeyError( "Error recieved as answer: %s" % constants.ERROR_CODES[error_code] )

        datatype = constants.DATASET[ self._unpack_int( response[18:22] ) ]

        if datatype is constants.FLOAT_TYPE:
            value = response[-6:-2]
            value = self._unpack_float(value)
        elif datatype is constants.INT_TYPE:
            value = response[-6:-2]
            value = self._unpack_int(value)
        elif datatype is constants.BOOL_TYPE:
            value = response[-3:-2]
            value = self._unpack_bool(value)
        elif datatype is constants.SHORT_ENUM_TYPE:
            value = response[-4:-2]
            value = self._unpack_int_short(value)
        else:
            raise TypeError("Datatype unknown!")

        return value
        
    def set_value(self, parameter, value: int, property_id = constants.UNSAVED_VALUE_QSP):
        parameter = parameter.id
        parameter_type = constants.DATASET[parameter]
        parameter = struct.pack("<I", parameter)

        if parameter_type is constants.FLOAT_TYPE:
            parameter_value = struct.pack("<f", value)
        elif parameter_type is constants.INT_TYPE:
            parameter_value = struct.pack("<I", value)
        elif parameter_type is constants.BOOL_TYPE:
            parameter_value = struct.pack("<?", value)
        else:
            raise TypeError("Unknown data type!")

        data_length = 10 + len(parameter_value)
        data_length = struct.pack("<H", data_length)

        package = Requestpackage(
            data_length=data_length,
            service_id=constants.WRITE_PROPERTY,
            object_id=parameter,
            property_id=property_id,
            property_data=parameter_value
        )

        with serial.Serial(self.socket_device, self.baudrate, timeout=self.timeout) as ser:
            ser.write(package.get_binary())

            response: bytes = ser.read_until(expected=constants.RS232_TERM, size=100)
            #response = ser.read_all()
            # remove terminator (2 bytes 0D 0A)
            #response = response[:-2]

        return response.hex()

    def set_property(self, property_id, property_data):
        data_length = 10 + len(property_data)
        data_length = struct.pack("<H", data_length)

        package = Requestpackage(
            data_length=data_length,
            service_id=constants.WRITE_PROPERTY,
            object_id=b'\x00\x00\x00\x00',
            property_id=property_id,
            property_data=property_data
        )

        with serial.Serial(self.socket_device, self.baudrate, timeout=self.timeout) as ser:
            ser.write(package.get_binary())

            response: bytes = ser.read_until(expected=constants.RS232_TERM, size=100)
            #response = ser.read_all()
            # remove terminator (2 bytes 0D 0A)
            #response = response[:-2]

        return response.hex()

    ###
    def _unpack_float(self, value) -> float:
        return struct.unpack("<f", value)[0]

    def _unpack_int(self, value) -> int:
        return struct.unpack("<I", value)[0]
    
    def _unpack_int_short(self, value) -> int:
        return struct.unpack("<H", value)[0]

    def _unpack_bool(self, value) -> bool:
        return struct.unpack("<?", value)[0]