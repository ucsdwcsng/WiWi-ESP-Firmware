import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm
from scipy.interpolate import CubicSpline
from sklearn.linear_model import LinearRegression

c=3e8
subcarrier_width = 80e6/256
expected_channel = 11
expected_csi_size = 384

# sc_idx = list(np.arange(64)) + list(np.arange(-64, 0, 1))
# HT40 no STBC,   384 Byte, from: https://github.com/espressif/esp-csi/issues/45
legacy_list = []
# LLTF ==> 52
legacy_list += [i for i in range(6,32)]     # 26
legacy_list += [i for i in range(33,59)]    # 26
legacy_list = np.array(legacy_list)

# HT-LTF  ==> 56 + 56
ht_list = []
ht_list += [i for i in range(67,123)]    # 56, [3, 58]
ht_list += [i for i in range(135,191)]  # 56, [-57, -2]
ht_list = np.array(ht_list)

f_c = 2.462e9 # for channel 11
f_sub = f_c + subcarrier_width * np.sort(list(range(3, 59)) + list(range(-57, -1, 1)))
f_sub_l = f_c + subcarrier_width * np.sort(list(range(6, 32)) + list(range(33,59)))


def read_csv_file(filename):
    """Read a CSV file and return the data as a Pandas DataFrame."""
    return pd.read_csv(filename,  sep=',')

def create_packet_id(row):
    """Concatenate the 'packet' and 'id' columns to create a complete Packet ID."""
    return str(row['packet']) + str(row['idx'])

def match_packets(file1,file2,dir):
   file1 = file1+".csv"
   file2 = file2+".csv"

   file1_data = read_csv_file(dir+file1)
   file2_data = read_csv_file(dir+file2)

   try:
      # Step 2: Create a new column 'PacketID' in each DataFrame by concatenating the two parts of the Packet ID
      file1_data['PacketID'] = file1_data.apply(create_packet_id, axis=1)
      file2_data['PacketID'] = file2_data.apply(create_packet_id, axis=1)

      matched_packets = pd.merge(file1_data, file2_data, on='PacketID', how='inner')

      matched_from_file1 = matched_packets.iloc[:, :(file1_data).shape[1]-1]
      matched_from_file2 = matched_packets.iloc[:, (file1_data).shape[1]:2*(file1_data).shape[1]-1]

      matched_from_file1.columns = ["type", "id", "mac", "rssi", "rate", "sig_mode", "mcs", "bandwidth", "smoothing", "not_sounding", "aggregation", "stbc", "fec_coding",
                        "sgi", "noise_floor", "ampdu_cnt", "channel", "secondary_channel", "local_timestamp", "ant", "sig_len", "rx_state", "len", "first_word", "data", "packet", "idx"]

      matched_from_file2.columns = ["type", "id", "mac", "rssi", "rate", "sig_mode", "mcs", "bandwidth", "smoothing", "not_sounding", "aggregation", "stbc", "fec_coding",
                        "sgi", "noise_floor", "ampdu_cnt", "channel", "secondary_channel", "local_timestamp", "ant", "sig_len", "rx_state", "len", "first_word", "data", "packet", "idx"]

      # Step 5: Save the DataFrames to new CSV files
      matched_from_file1.to_csv(dir+file1, index=False)
      matched_from_file2.to_csv(dir+file2, index=False)
   except:
      return
      

def to_3_sig(num):
   return float("{:.2e}".format(num))

def load_csi(fname, legacy_list, ht_list):
   """
   Reads data from CSV file, extract both legacy and high-throughput CSI. Returns the raw data from CSV file as well
   :param fname: CSV file name
   :param legacy_list: list of indices in the CSI array which corresponds to legacy CSI
   :param ht_list: list of indices in the CSI array which corresponds to high-throughput CSI
   :return: csi_l, csi_ht, all_data
   """
   all_data = pd.read_csv(fname)
   if not np.all(all_data['channel'] == expected_channel):
      bad_idx = np.where(all_data["channel"] != expected_channel)[0]
      print(f"Received channel not 11 for {len(bad_idx)} packets")
   else:
      bad_idx = []
   raw_csi = list(map(eval, all_data['data'].values))
   raw_csi = np.delete(raw_csi, bad_idx, axis=0)
   bad_idx = np.where(np.array(list(map(len, raw_csi))) != expected_csi_size)[0]
   raw_csi = np.delete(raw_csi, bad_idx, axis=0)
   raw_csi = np.vstack(raw_csi)
   csi_l = raw_csi[:, legacy_list * 2] + raw_csi[:, legacy_list * 2 - 1] * 1j
   csi_l = np.fft.fftshift(csi_l, axes=1)  # center the dc freq

   csi_ht = (raw_csi[:, ht_list * 2] + raw_csi[:, ht_list * 2 - 1] * 1j )
   csi_ht = np.fft.fftshift(csi_ht, axes=1)  # center the dc freq
   nsc = csi_ht.shape[1]
   csi_ht[:, :(nsc + 1) // 2] = -1j * csi_ht[:, :(nsc + 1) // 2]  # apply -1j constant to first half of SC, as is common with ASUS or Quantenna packets

   return csi_l, csi_ht, all_data

def process_csi (data):
   
   NumPCT = (len(data))
   lengCM = data.iloc[0, 22]  # Assuming indexing starts from 0


   C1, C2, CMatrix1, PMatrix1, CMatrix2, PMatrix2 = [], [], [], [], [], []


   for index, row in data.iterrows():
      C1 = list(map(int, row[24].strip('[]').split(',')))

      c_matrix_1_row = []

      for m in range(0, lengCM, 2):
        c1_complex = complex(C1[m + 1], C1[m])
        c_matrix_1_row.append(c1_complex)


      CMatrix1.append(c_matrix_1_row)


   CMatrix1 = np.array(CMatrix1)

   return CMatrix1

def compute_offsets(csi, freq, fc):
   """
   Computs the sampling time offset, sampling frequency offsets from the intercept and slope of the CSI phases
   :param csi: complex array, number_subcarriers x 1
   :param freq: sub-carrier frequencies
   :param fc: center frequency
   :return: dc_phases, slopes
   """
   phases = np.unwrap(np.angle(csi), axis=1)
   # dc_phases = np.zeros(len(phases))
   slopes = np.zeros(len(phases))

   for ii, p in tqdm(enumerate(phases)):
      # cs = CubicSpline(freq, p)
      # dc_phases[ii] = cs(fc)
      lr = LinearRegression().fit(freq.reshape(-1, 1), p)
      slopes[ii] = lr.coef_

   # Can they be done together?
   cs = CubicSpline(freq, phases, axis=1)
   dc_phases = cs(fc)

   return dc_phases, slopes