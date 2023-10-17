import numpy as np
import matplotlib.pyplot as plt
import glob
from scipy.interpolate import CubicSpline
from sklearn.linear_model import LinearRegression
from tqdm import tqdm

PORT = "/dev/ttyACM1"
SAVE_DIR = "/home/aarun/Research/data/time_sync/burst_testing_2"
FILES = glob.glob(f"{SAVE_DIR}/*")

CSI_IDX = 21
PKT_IDX = 22
TIME_IDX = 16
NUM_COLS = 23
NUM_PKTS_BURST = 10
PKT_RATE = 1000  # Hz

ht_list = []
ht_list += list(range(67, 123))  # 56, [3, 58]
ht_list += list(range(135, 191))  # 56, [-57, -2]
ht_list = np.array(ht_list)

c = 3e8
subcarrier_width = 80e6 / 256
f_c = 2.462e9  # for channel 11
f_sub = f_c + subcarrier_width * np.sort(list(range(3, 59)) + list(range(-57, -1, 1)))


def compute_offsets(phases, freq, fc):
   """
   Computs the sampling time offset, sampling frequency offsets from the intercept and slope of the CSI phases
   :param csi: complex array, number_subcarriers x 1
   :param freq: sub-carrier frequencies
   :param fc: center frequency
   :return: dc_phases, slopes
   """
   slopes = np.zeros(len(phases))

   for ii, p in enumerate(phases):
      # cs = CubicSpline(freq, p)
      # dc_phases[ii] = cs(fc)
      lr = LinearRegression().fit(freq.reshape(-1, 1), p)
      slopes[ii] = lr.coef_

   # Can they be done together?
   cs = CubicSpline(freq, phases, axis=1)
   dc_phases = cs(fc)

   return dc_phases, slopes


def process_batch(raw_csi):
   csi_ht = raw_csi[:, ht_list * 2] + raw_csi[:, ht_list * 2 - 1] * 1j
   csi_ht = np.fft.fftshift(csi_ht, axes=1)  # center the dc freq
   nsc = csi_ht.shape[1]
   csi_ht[:, :(nsc + 1) // 2] = -1j * csi_ht[:, :(
                                                       nsc + 1) // 2]  # apply -1j constant to first half of SC, as is common with ASUS or Quantenna packets
   phase = np.unwrap(np.angle(csi_ht), axis=1)
   dc_phase, slope = compute_offsets(phase, f_sub, f_c)

   return csi_ht, phase, dc_phase, slope


data = {}

for fname in tqdm(FILES):
   key = fname.split("/")[-1].split(".")[0]
   data[key] = []  # List of batches of data
   data[key].append({"csi": [], "pkt": [], "time": []})
   with open(fname, "r") as f:
      for line in f:
         if line == "\n":
            raw_csi = np.array(data[key][-1]["csi"])
            data[key][-1]["csi"], data[key][-1]["phase"], \
            data[key][-1]["dc_phase"], data[key][-1]["slope"] = process_batch(raw_csi)

            data[key].append({"csi": [], "pkt": [], "time": []})
         else:
            pkt_id = int(line.split(",")[PKT_IDX]) + (int(line.split(",")[PKT_IDX + 1]) << 8)
            time = int(line.split(",")[TIME_IDX])
            csi = np.array(list(map(int, line.split(",")[CSI_IDX][1:-1].split(";"))))
            data[key][-1]["csi"].append(csi)
            data[key][-1]["pkt"].append(pkt_id)
            data[key][-1]["time"].append(time)

   # Do the same for the last batch of data
   raw_csi = np.array(data[key][-1]["csi"])
   data[key][-1]["csi"], data[key][-1]["phase"], \
      data[key][-1]["dc_phase"], data[key][-1]["slope"] = process_batch(raw_csi)

# %%
cfo_slopes = {}
num_skipped = 0
num_batches = 0
all_true_offset = []
all_pred_offset = []
plt.figure()
for key, value in data.items():
   all_pkts = []
   all_phases = []
   all_times = []
   all_slopes = []
   true_offset = int(key.split("_")[1])  # mhz
   batch_slopes = []
   # plt.figure()
   for batch in value:
      num_batches += 1
      cur_phases = np.unwrap(batch["dc_phase"])
      cur_slopes = batch["slope"]
      cur_pkts = batch["pkt"]
      cur_times = np.array(batch["time"]) - batch["time"][0]
      cur_times = cur_times * 1e-6
      if np.all(np.diff(cur_pkts) == 1):
         all_pkts.append(cur_pkts)
         all_phases.append(cur_phases)
         all_times.append(np.diff(cur_times))
         all_slopes.append(np.median(cur_slopes))
         batch_slopes.append(np.polyfit(cur_times, cur_phases, 1)[0])
      else:
         num_skipped += 1

   all_times = np.concatenate(all_times)
   plt.hist(all_times, len(all_times)//10)

   cfo_slopes[key] = np.array(batch_slopes)
   pred_offset = cfo_slopes[key] / 2 / np.pi / 60 * 1e3
   # plt.plot([true_offset] * len(all_slopes), all_slopes, "o")
   all_true_offset.append(true_offset)
   all_pred_offset.append(pred_offset)
   print(f"True offset = {true_offset}, Predicted offset = {np.median(pred_offset)}")
plt.grid("minor")
