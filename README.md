# xcom-232i

Python library to access Studer-Innotec Xcom-232i device through RS-232 over a serial port.

NOTE: This lib is still WiP, so functionality is still limited, but feel free to create a [pull request](https://github.com/studer-innotec/xcom485i/pulls) if you want to contribute ;)

DISCLAIMER: This library is NOT officially made by Studer-Innotec.

## Getting Started

### Requirements

#### Hardware

- Xcom-232i connected to your installation
- Xcom-232i connected to PC using USB to RS-232 adapter (1)
- PC with at least USB2.0 or faster (works on Raspberry Pi 3/4 as well)

(1) I personally am successfully using an adapter with the PL2303 chipset like [this one](https://www.amazon.de/dp/B00QUZY4UG)



ddd

#### Software

- any Linux based OS (x86 / ARM)
- python3 >= 3.6
- python3-pip

### Installation

```bash
pip3 install xcom-232i
```

**important**: make sure you select the USB to RS-232 adapter as the `socket_device`, usually on Linux it is `/dev/ttyUSB[0-9]`

## Examples

### Reading values

```python
from xcom_232i import XcomRS232
from xcom_232i import constants as c

IO = XcomRS232(socket_device='/dev/ttyUSB0', baudrate=115200)

lademodus = IO.get_value(c.OPERATION_MODE)
batt_phase = IO.get_value(c.BAT_CYCLE_PHASE)
solarleistung = IO.get_value(c.PV_POWER) * 1000 # convert from kW to W
sonnenstunden = IO.get_value(c.NUM_SUN_HOURS_CURR_DAY)
ladestand = IO.get_value(c.STATE_OF_CHARGE) # in %
stromprod = IO.get_value(c.PROD_ENERGY_CURR_DAY)
batt_strom = IO.get_value(c.BATT_CURRENT)
batt_spann = IO.get_value(c.BATT_VOLTAGE)

print(f"LModus: {lademodus} | Batt_Phase: {batt_phase} | Solar_P: {solarleistung} | SonnenH: {sonnenstunden} | Batt_V: {batt_spann} | SOC: {ladestand}")
```
