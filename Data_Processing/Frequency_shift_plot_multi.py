import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
import helper
import matplotlib.gridspec as gridspec
from prettytable import PrettyTable

alt_plot = False
data_dir = "/Users/sureel/VS_Code/wiwi-time-sync/Data/"

# data_1 = "CSI_1"
# data_2 = "CSI_2"

phase_1, phase_2, Time = [], [], []

packet = 1  # This is the chosen packet for analysis

num_files = 10
increments = 1

for i in range(0, num_files*increments, increments):

    data_1 = "S3_wired_sigclk_" + str(i) + "mhz_1_3"
    data_2 = "S3_wired_sigclk_" + str(i) + "mhz_2_3"

    helper.match_packets(data_1, data_2, data_dir)

    # Read tables from CSV files
    T1 = pd.read_csv(data_dir+data_1+".csv")
    T2 = pd.read_csv(data_dir+data_2+".csv")

    NumPCT = min(len(T1), len(T2))
    lengCM = T1.iloc[0, 22]  # Assuming indexing starts from 0
    RSSI = T1.iloc[packet, 3]

    try:
        Timestamp = np.array(T1.iloc[:, 27])
        Timestamp = Timestamp-Timestamp[0]
        Time.append(Timestamp)
    # print(Time)
    except:
        print("No Timestamp")
        Time.append(np.arange(0, NumPCT))

    CMatrix1 = helper.process_csi(T1)
    CMatrix2 = helper.process_csi(T2)

    SubChannel = np.arange(-64, 64)
    CSub1 = np.column_stack((CMatrix1[:, 128:192], CMatrix1[:, 64:128]))
    CSub2 = np.column_stack((CMatrix2[:, 128:192], CMatrix2[:, 64:128]))

    # CSub1 = np.column_stack((CMatrix1[:, 134:191], CMatrix1[:, 66:123]))
    # CSub2 = np.column_stack((CMatrix2[:, 134:191], CMatrix2[:, 66:123]))

    CSubShiftHigh1 = CSub1.copy()
    CSubShiftHigh2 = CSub2.copy()

    SubChannelSelect = np.hstack((np.arange(-58, -1), np.arange(2, 59)))
    CSubShiftHighSelect1 = CSubShiftHigh1[:, np.hstack(
        (np.arange(6, 63), np.arange(66, 123)))]
    CSubShiftHighSelect2 = CSubShiftHigh2[:, np.hstack(
        (np.arange(6, 63), np.arange(66, 123)))]

    nsc = CSubShiftHighSelect1.shape[1]
    CSubShiftHighSelect1[:, (nsc + 1) // 2:] = -1j * \
        CSubShiftHighSelect1[:, (nsc + 1) // 2:]
    CSubShiftHighSelect2[:, (nsc + 1) // 2:] = -1j * \
        CSubShiftHighSelect2[:, (nsc + 1) // 2:]

    PMatrix1 = (np.unwrap(np.angle(CMatrix1)))
    PMatrix2 = (np.unwrap(np.angle(CMatrix2)))

    PhaseSubShiftHighSelect1 = np.unwrap(
        np.angle(CSubShiftHighSelect1), axis=1)
    PhaseSubShiftHighSelect2 = np.unwrap(
        np.angle(CSubShiftHighSelect2), axis=1)

    phase_1.append(PhaseSubShiftHighSelect1)
    phase_2.append(PhaseSubShiftHighSelect2)

# phase_1 = np.array(phase_1)
# phase_2 = np.array(phase_2)

# Create a list of 10 colors to cycle through
colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', '#FFA500', '#800080', '#008000']


# ... [your code before plotting remains unchanged]

fig = plt.figure(figsize=(8, 8))
gs_main = gridspec.GridSpec(2, 1, height_ratios=[2, 1])

ax1 = plt.Subplot(fig, gs_main[0])
ax2 = plt.Subplot(fig, gs_main[1])
# print(len(stan))
Phase_avg, ffit, yfit, slope, freq = [], [], [], [], []

freq = np.arange(0, num_files*increments, increments)
# print(freq)
# plt.hist(stan, bins=20)
for i in range(len(phase_1)):
    # for i in range(3):

    # Phase_avg = []
    # Time.append(np.arange(0, phase_1[i].shape[0]))

    Phase_avg.append(np.unwrap(np.mean(
        phase_1[i] - phase_2[i], axis=1)))

    ffit.append(np.polyfit(Time[i], Phase_avg[i], 1))
    ffit[i][1] = 0
    slope.append(ffit[i][0])
    # print(ffit)
    yfit.append(np.polyval(ffit[i], Time[i]))

    # Phase_avg = np.array(Phase_avg)

    # Phase_avg = Phase_avg - Phase_avg[0]
    # plt.plot( Time[i], Phase_avg[i], 'r-')
    # plt.plot(Time[i], Phase_avg[i], 'k.', Time[i], yfit[i], 'r-')
    Phase_avg[i] = Phase_avg[i] - Phase_avg[i][0]
    ax1.plot(Time[i], Phase_avg[i], '.', color=colors[i % len(colors)],
             label=f'Slope: {ffit[i][0]:.5f}, ' + f'\u0394F {increments*i}mHz',)
    ax1.plot(Time[i], yfit[i], color='black',
             linestyle='-',   markersize=10)

    ax2.plot(increments*i, ffit[i][0], '*',
             markersize=10, color=colors[i % len(colors)])

# print(len(slope))
ffit2 = np.polyfit(freq, slope, 1)
yfit2 = np.polyval(ffit2, freq)

ax2.plot(freq, yfit2, label=f'Slope: {ffit2[0]: .5f}')

ax1.set_xlabel('Time [s]')
ax1.set_ylabel('mean ' + r'$\phi_2 - \phi_1$ [rad]')
ax1.set_title("mean " + r'$\phi_2 - \phi_1$ [rad]' + " vs Time [s]")
ax1.legend()

ax2.set_xlabel("\u0394Frequency (mHz)")
ax2.set_ylabel("Slope")
ax2.set_title("Slope vs \u0394Frequency (mHz)")
ax2.legend()

# fig.add_subplot(ax6)
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
ax2.grid(True, which='both', linestyle='--', linewidth=0.5)

fig.add_subplot(ax1)
fig.add_subplot(ax2)

# print(ffit)
plt.subplots_adjust(hspace=0.3)  # Adjust the spacing between subplots


# plt.tight_layout()

plt.show()
