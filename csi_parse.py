import serial
import numpy as np
import matplotlib.pyplot as plt
import datetime
import csv
from os import path

PORT = "/dev/ttyACM1"
SAVE_DIR = "/home/aarun/Research/data/time_sync/burst_testing/"
SAVE_FILE = "test1.csv"
NUM_PKTS_BURST = 10
NUM_COLS = 23

ser = serial.Serial(port=PORT, baudrate=5000000,
                    bytesize=8, parity='N', stopbits=1)
assert ser.isOpen(), "Serial port unopened"

csv_writer = csv.writer(open(path.join(SAVE_DIR, SAVE_FILE), 'w'), delimiter=",")

burst_csi = []
burst_pkt = []
while True:
   strings = str(ser.readline())
   strings = strings.lstrip('b\'').rstrip('\\r\\n\'')
   if "CSI_DATA" in strings:
      timestamp = datetime.datetime.now().timestamp()
      string_w_time = strings.split(",")[1:]
      string_w_time.append(str(timestamp))
      burst_csi.append(string_w_time)
      for ii in range(NUM_PKTS_BURST - 1):
         strings = str(ser.readline())
         strings = strings.lstrip('b\'').rstrip('\\r\\n\'')

         if "CSI_DATA" not in strings:
            burst_pkt = []
            burst_csi = []
            break
         timestamp = datetime.datetime.now().timestamp()
         string_w_time = strings.split(",")[1:]
         string_w_time.append(str(timestamp))
         burst_csi.append(string_w_time)
      for ii in range(NUM_PKTS_BURST):
         strings = str(ser.readline())
         strings = strings.lstrip('b\'').rstrip('\\r\\n\'')

         if "PKT_ID" not in strings:
            burst_pkt = []
            burst_csi = []
            break
         timestamp = datetime.datetime.now().timestamp()
         string_w_time = strings.split(",")[1:]
         string_w_time.append(str(timestamp))
         burst_pkt.append(string_w_time)

      assert len(burst_csi) == NUM_PKTS_BURST and len(burst_pkt) == NUM_PKTS_BURST, \
         f"Packet missing error, length of CSI: {burst_csi}, length of PKT ID: {burst_pkt}"
      assert np.all(np.array(list(map(len, burst_csi))) == NUM_COLS), \
         f"Packet malformed, data col #: {np.array(list(map(len, burst_csi)))}"

      for csi, pkt in zip(burst_csi, burst_pkt):
         pkt = list(map(str.strip, pkt))
         toStore = csi[:-1] + pkt[:-1] # ignore timestamp, not needed i think
         csv_writer.writerow(toStore)

      csv_writer.writerow("")

      # Clean up
      burst_pkt = []
      burst_csi = []