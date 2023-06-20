#! /usr/bin/env python3

import struct
from . import constants

class Requestpackage:
    def __init__(self, 
        data_length: bytes,        
        service_id: bytes,          
        object_id: bytes,
        property_id: bytes,
        property_data: bytes,
        service_flags = b'\x00',
        src_addr = b'\x01\x00\x00\x00',
        dst_addr = b'\x64\x00\x00\x00', # broadcast address; TODO: make this editable
        object_type = constants.TYPE_PARAMETER
        ):

        #####################
        # defines structure of a request package
        #####################

        self.start_byte = b'\xAA' # NOTE: start_byte is not part of the header for the checksum!
        self.frame_flags = b'\x00'
        self.src_addr = src_addr
        self.dst_addr = dst_addr
        self.data_length = data_length        
        self.service_flags = service_flags
        self.service_id = service_id
        self.object_type = object_type
        self.object_id = object_id
        self.property_id = property_id
        self.property_data = property_data

        self.header = self.frame_flags + self.src_addr + self.dst_addr + self.data_length
        self.header_checksum = self.checksum(self.header)

        self.frame_data = self.service_flags + self.service_id + self.object_type + self.object_id + self.property_id + self.property_data
        self.data_checksum = self.checksum(self.frame_data)


        self.package = self.start_byte + self.header + self.header_checksum + self.frame_data + self.data_checksum

        # add terminator for RS232 package
        self.package += constants.RS232_TERM

    def checksum(self, input_data: bytes) -> bytes:
        """Function to calculate the checksum needed for the header and the data"""
        A = 0xFF
        B = 0x00

        for data in input_data:
            A = (A + data) % 0x100
            B = (B + A) % 0x100

        A = struct.pack("<B", A)
        B = struct.pack("<B", B)

        return A + B

    def get_binary(self) -> bytes:
        return self.package
