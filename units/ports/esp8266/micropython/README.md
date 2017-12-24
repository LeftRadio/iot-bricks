# iot-brick-esp micropython port

# micropython 1.9.3 build with integrated iot-bricks modules

Install dependiens:

> sudo apt install python3 pyesp git

Get this repository:

> git clone https://github.com/LeftRadio/iot-bricks

Go to ESP8266 port folder:

> cd /iot-brick/units/ports/esp8266/micropython

Power-up ESP board in BOOT mode and execute:

> python3 ./utils/esptool.py --port PORT --baud 115200 erase_flash

RePower board in BOOT mode and write firmware:

> python3 ./utils/esptool.py --port PORT --baud 115200 write_flash --flash_size=detect 0 ./firmware/iot-bricks-mpy193.bin

#

RePower board in NORMAL mode and execute:

> pyesp --write_files -f "./src/boot.py,./src/main.py,../../../src/user_main.py,../../../src/uplatform.py"


Againe reset ESP, Done! You heave iot-brick module (::)
