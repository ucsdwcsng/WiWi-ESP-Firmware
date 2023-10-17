import serial
import numpy as np
import matplotlib.pyplot as plt
import datetime
import csv
from os import path
import time

PORT = "/dev/ttyACM1"
SAVE_DIR = "/home/aarun/Research/data/time_sync/burst_testing_2/"
SAVE_FILE = "test2.csv"
MIN_PKTS_BURST = 4
NUM_PKTS_BURST = 5
NUM_COLS = 22

TIME_IDX = 17

print("Warning: packet id's cannot be trusted, currently mapping not happening appropriately")

def write_batch(burst_csi, burst_pkt, csv_writer):
   if MIN_PKTS_BURST < len(burst_csi) == len(burst_pkt):
      assert np.all(np.array(list(map(len, burst_csi))) == NUM_COLS), \
         f"Packet malformed, data col #: {np.array(list(map(len, burst_csi)))}"
      for csi, pkt in zip(burst_csi, burst_pkt):
         pkt = list(map(str.strip, pkt))
         toStore = csi + pkt  # ignore timestamp, not needed i think
         csv_writer.writerow(toStore)

      print(f"Writing PKT {pkt[:-1]}")
      csv_writer.writerow("")
   else:
      print(f"Too few packets in burst, skipping; length of CSI: {len(burst_csi)}, "
            f"length of PKT ID: {len(burst_pkt)}")

   return

ser = serial.Serial(port=PORT, baudrate=5000000,
                    bytesize=8, parity='N', stopbits=1)
assert ser.isOpen(), "Serial port unopened"

csv_writer = csv.writer(open(path.join(SAVE_DIR, SAVE_FILE), 'w'), delimiter=",")

burst_csi = []
burst_pkt = []
prev_time = None
while True:
   try:
      strings = str(ser.readline())
      strings = strings.lstrip('b\'').rstrip('\\r\\n\'')
      if "CSI_DATA" in strings:
         cur_time = int(strings.split(",")[TIME_IDX])
         if len(burst_csi) > 0 and prev_time is not None and (cur_time - prev_time)*1e-6 > 0.5:
            write_batch(burst_csi, burst_pkt, csv_writer)
            # Clean up
            burst_pkt = []
            burst_csi = []

         burst_csi.append(strings.split(",")[1:])
         prev_time = cur_time

      if "PKT_ID" in strings:
         burst_pkt.append(strings.split(",")[1:])
         # if len(burst_pkt) == NUM_PKTS_BURST:
         #    write_batch(burst_csi, burst_pkt, csv_writer)
         #    # Clean up
         #    burst_pkt = []
         #    burst_csi = []

      # time.sleep(0.01)
   except KeyboardInterrupt:
      ser.close()
      break
