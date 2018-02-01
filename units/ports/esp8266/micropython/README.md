
## iot-brick port for ESP8266
### based on micropython 1.9.3 fork - https://github.com/LeftRadio/micropython

Install Dependencies
--------------------
```bash
$ sudo apt install git python3 python3-pip python3-pyqt5 python3-pyqt5.qtserialport
$ sudo pip3 install esptool pyesp
```

Clone iot-bricks repository
---------------------------
```bash
$ cd ~
$ git clone https://github.com/LeftRadio/iot-bricks
```

Then go to ESP8266 port folder, power-up ESP board in BOOT mode and erase/programm flash on board:
```bash
$ cd ~/iot-bricks/units/ports/esp8266/micropython
$ esptool.py --port PORT erase_flash
$ esptool.py --port PORT --baud 460800 write_flash --flash_size=detect 0 iot-bricks-mpy193.bin
```
Edit "/iot-bricks/units/py/defaults.py" file, set serial number as sha256 checksum, option set default WiFi AP and MQTT servers.

OK, now re-power board in NORMAL mode and write next files:
```bash
$ pyesp --platform MPY --command filewrite --files "boot.py,main.py"
$ cd ../../../py
$ pyesp -p MPY -c filewrite -f "defaults.py,uplatform.py"
```

Reset ESP, Done! You heave complite iot-brick module (::)

