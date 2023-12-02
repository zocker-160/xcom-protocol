#! /usr/bin/env python3

##
# Class implementing Xcom protocol 
##

import struct
from io import BufferedWriter, BufferedReader, BytesIO

from .parameters import ERROR_CODES

class Service:

    object_type: bytes
    object_id: int
    property_id: bytes
    property_data: bytes

    @staticmethod
    def parse(f: BufferedReader):
        return Service(
            f.read(2),
            readUInt(f),
            f.read(2),
            f.read(-1)
        )

    def __init__(self, 
            object_type: bytes, object_id: int, 
            property_id: bytes, property_data: bytes):

        assert len(object_type) == 2
        assert len(property_id) == 2

        self.object_type = object_type
        self.object_id = object_id
        self.property_id = property_id
        self.property_data = property_data

    def assemble(self, f: BufferedWriter):
        f.write(self.object_type)
        writeUInt(f, self.object_id)
        f.write(self.property_id)
        f.write(self.property_data)

    def __len__(self) -> int:
        return 2*2 + 4 + len(self.property_data)

    def __str__(self) -> str:
        return f"(obj_type={self.object_type}, obj_id={self.object_id}, property_id={self.property_id}, property_data={self.property_data})"

class Frame:

    service_flags: int
    service_id: bytes
    service_data: Service

    @staticmethod
    def parse(f: BufferedReader):
        return Frame(
            service_flags=readUChar(f),
            service_id=f.read(1),
            service_data=Service.parse(f)
        )

    @staticmethod
    def parseBytes(buf: bytes):
        return Frame.parse(BytesIO(buf))

    def __init__(self, service_id: bytes, service_data: Service, service_flags=0):
        assert service_flags >= 0, "service_flag must not be negative"
        assert len(service_id) == 1

        self.service_flags = service_flags
        self.service_id = service_id
        self.service_data = service_data

    def assemble(self, f: BufferedWriter):
        writeUChar(f, self.service_flags)
        f.write(self.service_id)
        self.service_data.assemble(f)

    def getBytes(self) -> bytes:
        buf = BytesIO()
        self.assemble(buf)
        return buf.getvalue()

    def __len__(self) -> int:
        return 2*1 + len(self.service_data)

    def __str__(self) -> str:
        return f"Frame(flags={self.service_flags}, id={self.service_id}, setr={self.service_data})"

class Header:

    frame_flags: int
    src_addr: int
    dst_addr: int
    data_length: int

    length: int = 2*4 + 2 + 1

    @staticmethod
    def parse(f: BufferedReader):
        return Header(
            frame_flags=readUChar(f),
            src_addr=readUInt(f),
            dst_addr=readUInt(f),
            data_length=readUShort(f)
        )

    @staticmethod
    def parseBytes(buf: bytes):
        return Header.parse(BytesIO(buf))

    def __init__(self, src_addr: int, dst_addr: int, data_length: int, frame_flags=0):
        assert frame_flags >= 0, "frame_flags must not be negative"

        self.frame_flags = frame_flags
        self.src_addr = src_addr
        self.dst_addr = dst_addr
        self.data_length = data_length

    def assemble(self, f: BufferedWriter):
        writeUChar(f, self.frame_flags)
        writeUInt(f, self.src_addr)
        writeUInt(f, self.dst_addr)
        writeUShort(f, self.data_length)

    def getBytes(self) -> bytes:
        buf = BytesIO()
        self.assemble(buf)
        return buf.getvalue()

    def __len__(self) -> int:
        return self.length

    def __str__(self) -> str:
        return f"Header(flags={self.frame_flags}, src={self.src_addr}, dst={self.dst_addr}, data_length={self.data_length})"

class Package:

    start_byte: bytes = b'\xAA'
    header: Header
    frame_data: Frame

    @staticmethod
    def parse(f: BufferedReader):
        # package sometimes starts with 0xff
        if (sb := f.read(1)) == b'\xff':
            assert f.read(1) == Package.start_byte
        else:
            assert sb == Package.start_byte

        h_raw = f.read(Header.length)
        assert checksum(h_raw) == f.read(2)
        header = Header.parseBytes(h_raw)

        f_raw = f.read(header.data_length)
        assert checksum(f_raw) == f.read(2)
        frame = Frame.parseBytes(f_raw)

        return Package(header, frame)

    @staticmethod
    def parseBytes(buf: bytes):
        return Package.parse(BytesIO(buf))

    @staticmethod
    def genPackage(service_id: bytes,
            object_id: int,
            object_type: bytes,
            property_id: bytes,
            property_data: bytes,
            src_addr = 1,
            dst_addr = 0):
        
        frame = Frame(
            service_id, 
            Service(object_type, object_id, property_id, property_data)
        )

        return Package(
            Header(src_addr, dst_addr, len(frame)),
            frame
        )


    def __init__(self, header: Header, frame_data: Frame):
        self.header = header
        self.frame_data = frame_data

    def assemble(self, f: BufferedWriter):
        f.write(self.start_byte)

        header = self.header.getBytes()
        f.write(header)
        f.write(checksum(header))

        data = self.frame_data.getBytes()
        f.write(data)
        f.write(checksum(data))

    def getBytes(self) -> bytes:
        buf = BytesIO()
        self.assemble(buf)
        return buf.getvalue()

    def isResponse(self) -> bool:
        return (self.frame_data.service_flags & 2) >> 1 == 1

    def isError(self) -> bool:
        return self.frame_data.service_flags & 1 == 1

    def getError(self) -> str:
        if self.isError():
            return ERROR_CODES.get(
                self.frame_data.service_data.property_data,
                "UNKNOWN ERROR"
            )
        return None
 
    def __str__(self) -> str:
        return f"Package(header={self.header}, frame_data={self.frame_data})"

##

def checksum(data: bytes) -> bytes:
    """Function to calculate the checksum needed for the header and the data"""
    A = 0xFF
    B = 0x00

    for d in data:
        A = (A + d) % 0x100
        B = (B + A) % 0x100

    A = struct.pack("<B", A)
    B = struct.pack("<B", B)

    return A + B

##

def readUInt(f: BufferedReader) -> int:
    return int.from_bytes(f.read(4), byteorder="little", signed=False)

def writeUInt(f: BufferedWriter, value: int) -> int:
    return f.write(value.to_bytes(4, byteorder="little", signed=False))

def readSInt(f: BufferedReader) -> int:
    return int.from_bytes(f.read(4), byteorder="little", signed=True)

def writeSInt(f: BufferedWriter, value: int) -> int:
    return f.write(value.to_bytes(4, byteorder="little", signed=True))


def readUShort(f: BufferedReader) -> int:
    return int.from_bytes(f.read(2), byteorder="little", signed=False)

def writeUShort(f: BufferedWriter, value: int) -> int:
    return f.write(value.to_bytes(2, byteorder="little", signed=False))


def readUChar(f: BufferedReader) -> int:
    return int.from_bytes(f.read(1), byteorder="little", signed=False)

def writeUChar(f: BufferedWriter, value: int) -> int:
    return f.write(value.to_bytes(1, byteorder="little", signed=False))
