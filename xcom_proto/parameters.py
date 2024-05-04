#! /usr/bin/env python3

##
# Definition of all parameters / constants used in the Xcom protocol
##

import struct
from dataclasses import dataclass


class UnknownDatapointException(Exception):
    pass

@dataclass
class ValueTuple:
    id: int
    value: str

    def __eq__(self, __o: object) -> bool:
        if __o.__class__ is self.__class__:
            return __o.id == self.id
        return __o == self.id

    def __ne__(self, __o: object) -> bool:
        if __o.__class__ is self.__class__:
            return __o.id != self.id
        return __o != self.id

    def __str__(self) -> str:
        return self.value

@dataclass
class Datapoint:
    id: int
    name: str
    type: str
    unit: str = ""

    def __eq__(self, __o: object) -> bool:
        if __o.__class__ is self.__class__:
            return __o.id == self.id
        return __o == self.id

    def __ne__(self, __o: object) -> bool:
        if __o.__class__ is self.__class__:
            return __o.id != self.id
        return __o != self.id

    def unpackValue(self, value: bytes):
        if self.type is TYPE_FLOAT:
            return struct.unpack("<f", value)[0]
        if self.type is TYPE_SINT:
            return struct.unpack("<i", value)[0]
        if self.type is TYPE_BOOL:
            return struct.unpack("<?", value)[0]
        if self.type is TYPE_SHORT_ENUM:
            return struct.unpack("<h", value)[0]

        raise TypeError("Unknown datatype", self)

    def packValue(self, value) -> bytes:
        if self.type is TYPE_FLOAT:
            return struct.pack("<f", value)
        if self.type is TYPE_SINT:
            return struct.pack("<i", value)
        if self.type is TYPE_BOOL:
            return struct.pack("<?", value)
        if self.type is TYPE_SHORT_ENUM:
            return struct.pack("<H", value)

        raise TypeError("Unknown datatype", self)

    @staticmethod
    def unpackValueByID(id: int, value: bytes):
        dataPoint = Dataset.getParamByID(id)
        return dataPoint.unpackValue(value)


### data types
TYPE_BOOL       = "BOOL"
TYPE_SINT       = "INTEGER"
TYPE_FLOAT      = "FLOAT"
TYPE_SHORT_ENUM = "ENUM_SHORT"
TYPE_LONG_ENUM  = "ENUM_LONG"
TYPE_STRING     = "STRING"
TYPE_BYTES      = "BYTES"

### service_id
PROPERTY_READ   = b'\x01'
PROPERTY_WRITE  = b'\x02'

### object_type
TYPE_INFO       = b'\x01\x00'
TYPE_PARAMETER  = b'\x02\x00'
TYPE_MESSAGE    = b'\x03\x00'
TYPE_GUID       = b'\x04\x00'
TYPE_DATALOG    = b'\x05\x00'

### property_id
QSP_VALUE           = b'\x05\x00'
QSP_MIN             = b'\x06\x00'
QSP_MAX             = b'\x07\x00'
QSP_LEVEL           = b'\x08\x00'
QSP_UNSAVED_VALUE   = b'\x0D\x00'

## values for QSP_LEVEL
QSP_LEVEL_VIEW_ONLY     = b'\x00\x00'
QSP_LEVEL_BASIC         = b'\x10\x00'
QSP_LEVEL_EXPERT        = b'\x20\x00'
QSP_LEVEL_INSTALLER     = b'\x30\x00'
QSP_LEVEL_QSP           = b'\x40\x00'


### operating modes (11016)
MODE_NIGHT      = ValueTuple(0, "MODE_NIGHT")
MODE_STARTUP    = ValueTuple(1, "MODE_STARTUP")
MODE_CHARGER    = ValueTuple(3, "MODE_CHARGER")
MODE_SECURITY   = ValueTuple(5, "MODE_SECURITY")
MODE_OFF        = ValueTuple(6, "MODE_OFF")
MODE_CHARGE     = ValueTuple(8, "MODE_CHARGE")
MODE_CHARGE_V   = ValueTuple(9, "MODE_CHARGE_V")
MODE_CHARGE_I   = ValueTuple(10, "MODE_CHARGE_I")
MODE_CHARGE_T   = ValueTuple(11, "MODE_CHARGE_T")

MODE_CHARGING = (
    MODE_CHARGE,
    MODE_CHARGE_V,
    MODE_CHARGE_I,
    MODE_CHARGE_T
)

### battey cycle phase (11038)
PHASE_BULK      = ValueTuple(0, "PHASE_BULK")
PHASE_ABSORPT   = ValueTuple(1, "PHASE_ABSORPT")
PHASE_EQUALIZE  = ValueTuple(2, "PHASE_EQUALIZE")
PHASE_FLOATING  = ValueTuple(3, "PHASE_FLOATING")
PHASE_R_FLOAT   = ValueTuple(6, "PHASE_R_FLOAT")
PHASE_PER_ABS   = ValueTuple(7, "PHASE_PER_ABS")


### error codes
ERROR_CODES = {
    b'\x01\x00': "INVALID_FRAME",
    b'\x02\x00': "DEVICE_NOT_FOUND",
    b'\x03\x00': "RESPONSE_TIMEOUT",
    b'\x11\x00': "SERVICE_NOT_SUPPORTED",
    b'\x12\x00': "INVALID_SERVICE_ARGUMENT",
    b'\x13\x00': "SCOM_ERROR_GATEWAY_BUSY",
    b'\x21\x00': "TYPE_NOT_SUPPORTED",
    b'\x22\x00': "OBJECT_ID_NOT_FOUND",
    b'\x23\x00': "PROPERTY_NOT_SUPPORTED",
    b'\x24\x00': "INVALID_DATA_LENGTH",
    b'\x25\x00': "PROPERTY_IS_READ_ONLY",
    b'\x26\x00': "INVALID_DATA",
    b'\x27\x00': "DATA_TOO_SMALL",
    b'\x28\x00': "DATA_TOO_BIG",
    b'\x29\x00': "WRITE_PROPERTY_FAILED",
    b'\x2A\x00': "READ_PROPERTY_FAILED",
    b'\x2B\x00': "ACCESS_DENIED",
    b'\x2C\x00': "SCOM_ERROR_OBJECT_NOT_SUPPORTED",
    b'\x2D\x00': "SCOM_ERROR_MULTICAST_READ_NOT_SUPPORTED",
    b'\x2E\x00': "OBJECT_PROPERTY_INVALID",
    b'\x2F\x00': "FILE_OR_DIR_NOT_PRESENT",
    b'\x30\x00': "FILE_CORRUPTED",
    b'\x81\x00': "INVALID_SHELL_ARG",
}

### main parameters

class Dataset:

    # Xtender parameters (Writable)
    MAX_CURR_AC_SOURCE = Datapoint(1107, "MAX_CURR_AC_SOURCE", TYPE_FLOAT)
    SMART_BOOST_ALLOWED = Datapoint(1126, "SMART_BOOST_ALLOWED", TYPE_BOOL)
    BATTERY_CHARGE_CURR = Datapoint(1138, "BATTERY_CHARGE_CURR", TYPE_FLOAT)
    MAX_GRID_FEEDING_CURR = Datapoint(1523, "MAX_GRID_FEEDING_CURR", TYPE_FLOAT)
    SMART_BOOST_LIMIT = Datapoint(1607, "SMART_BOOST_LIMIT", TYPE_FLOAT)

    PARAMS_SAVED_IN_FLASH = Datapoint(1550, "PARAMS_SAVED_IN_FLASH", TYPE_BOOL)

    # RCC / Xcom-232i parameters (Not SCOM accessible, do not use)
    USER_LEVEL = Datapoint(5012, "USER_LEVEL", TYPE_SHORT_ENUM)

    # Xtender infos (Read only)
    AC_ENERGY_IN_CURR_DAY = Datapoint(3081, "AC_POWER_IN_CURR_DAY", TYPE_FLOAT, "kWh")
    AC_ENERGY_IN_PREV_DAY = Datapoint(3080, "AC_POWER_IN_PREV_DAY", TYPE_FLOAT, "kWh")
    AC_ENERGY_OUT_CURR_DAY = Datapoint(3083, "AC_ENERGY_OUT_CURR_DAY", TYPE_FLOAT, "kWh")
    AC_ENERGY_OUT_PREV_DAY = Datapoint(3082, "AC_ENERGY_OUT_PREV_DAY", TYPE_FLOAT, "kWh")
    AC_FREQ_IN = Datapoint(3084, "AC_FREQ_IN", TYPE_FLOAT, "Hz")
    AC_FREQ_OUT = Datapoint(3085, "AC_FREQ_OUT", TYPE_FLOAT, "Hz")
    AC_POWER_IN = Datapoint(3137, "AC_POWER_IN", TYPE_FLOAT, "kW")
    AC_POWER_OUT = Datapoint(3136, "AC_POWER_OUT", TYPE_FLOAT, "kW")
    AC_VOLTAGE_IN = Datapoint(3011, "AC_VOLTAGE_IN", TYPE_FLOAT, "V")
    AC_VOLTAGE_OUT = Datapoint(3021, "AC_VOLTAGE_OUT", TYPE_FLOAT, "V")
    AC_CURRENT_IN = Datapoint(3012, "AC_CURRENT_IN", TYPE_FLOAT, "A")
    AC_CURRENT_OUT = Datapoint(3022, "AC_CURRENT_OUT", TYPE_FLOAT, "A")
    BATT_CYCLE_PHASE_XT = Datapoint(3010, "BATT_CYCLE_PHASE_XT", TYPE_SHORT_ENUM)

    # Xcom-CAN BMS parameters (Writable)
    SOC_LEVEL_FOR_BACKUP = Datapoint(6062, "SOC_LEVEL_FOR_BACKUP", TYPE_FLOAT)
    SOC_LEVEL_FOR_GRID_FEEDING = Datapoint(6063, "SOC_LEVEL_FOR_GRID_FEEDING", TYPE_FLOAT)

    # BSP infos (Read only)
    BATT_VOLTAGE = Datapoint(7000, "BATT_VOLTAGE", TYPE_FLOAT, "V")
    BATT_CURRENT = Datapoint(7001, "BATT_CURRENT", TYPE_FLOAT, "A")
    BATT_SOC = Datapoint(7032, "BATT_SOC", TYPE_FLOAT, "%")
    BATT_TEMP = Datapoint(7029, "BATT_TEMP", TYPE_FLOAT, "°C")
    BATT_CYCLE_PHASE = Datapoint(11038, "BATT_CYCLE_PHASE", TYPE_SHORT_ENUM)
    BATT_POWER = Datapoint(7003, "BATT_POWER", TYPE_FLOAT, "W")
    BATT_CHARGE = Datapoint(7007, "BATT_CHARGE", TYPE_FLOAT, "Ah")
    BATT_DISCHARGE = Datapoint(7008, "BATT_DISCHARGE", TYPE_FLOAT, "Ah")
    BATT_CHARGE_PREV_DAY = Datapoint(7009, "BATT_CHARGE_PREV_DAY", TYPE_FLOAT, "Ah")
    BATT_DISCHARGE_PREV_DAY = Datapoint(7010, "BATT_DISCHARGE_PREV_DAY", TYPE_FLOAT, "Ah")

    # VarioTrack infos (Read only)
    PV_VOLTAGE = Datapoint(11041 ,"PV_VOLTAGE", TYPE_FLOAT, "V")
    PV_POWER = Datapoint(11043, "PV_POWER", TYPE_FLOAT, "W")
    PV_ENERGY_CURR_DAY = Datapoint(11007, "PV_ENERGY_CURR_DAY", TYPE_FLOAT, "kWh")
    PV_ENERGY_PREV_DAY = Datapoint(11011, "PV_ENERGY_PREV_DAY", TYPE_FLOAT, "kWh")
    PV_ENERGY_TOTAL = Datapoint(11009, "PV_ENERGY_TOTAL", TYPE_FLOAT, "MWh")
    PV_SUN_HOURS_CURR_DAY = Datapoint(11025, "PV_SUN_HOURS_CURR_DAY", TYPE_FLOAT, "h")
    PV_SUN_HOURS_PREV_DAY = Datapoint(11026, "PV_SUN_HOURS_PREV_DAY", TYPE_FLOAT, "h")

    PV_OPERATION_MODE = Datapoint(11016, "PV_OPERATION_MODE", TYPE_SHORT_ENUM)
    PV_NEXT_EQUAL = Datapoint(11037, "PV_NEXT_EQUAL", TYPE_FLOAT, "d")

    # VarioTrack parameters (Writable)
    FORCE_NEW_CYCLE = Datapoint(10029, "FORCE_NEW_CYCLE", TYPE_SINT)

    # VarioString infos (Read only)
    VS_PV_POWER = Datapoint(15010, "VS_PV_POWER", TYPE_FLOAT, "kW")
    VS_PV_PROD = Datapoint(15017, "VS_PV_PROD", TYPE_FLOAT, "kWh")
    VS_PV_ENERGY_PREV_DAY = Datapoint(15027, "VS_PV_ENERGY_PREV_DAY", TYPE_FLOAT, "kWh")

    @staticmethod
    def getParamByID(id: int) -> Datapoint:
        for point in Dataset._getDatapoints():
            if point == id:
                return point

        raise UnknownDatapointException(id)

    @staticmethod
    def _getDatapoints() -> list[Datapoint]:
        points = list()
        for val in Dataset.__dict__.values():
            if type(val) is Datapoint:
                points.append(val)

        return points
