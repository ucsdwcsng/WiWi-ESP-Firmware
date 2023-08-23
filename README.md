# WiWi-ESP-Firmware

cd esp-csi/examples/get-started/csi_send
idf.py set-target esp32c3
idf.py flash -b 115200 -p /dev/cu.usbmodem14101 monitor
idf.py flash -b 115200 -p /dev/cu.usbmodem13301 monitor

idf.py flash -b 115200 -p /dev/cu.usbmodem1201 monitor


idf.py flash -b 115200 -p /dev/cu.usbmodem14401 monitor

idf.py -b 921600 -p /dev/cu.usbmodem14401 monitor