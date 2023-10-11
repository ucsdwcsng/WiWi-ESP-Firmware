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

data_1 = "S3_wired_sigclk_5mhz_1_3"
data_2 = "S3_wired_sigclk_5mhz_2_3"

helper.match_packets(data_1, data_2, data_dir)

packet = 50  # This is the chosen packet for analysis


# Read tables from CSV files
T1 = pd.read_csv(data_dir+data_1+".csv")
T2 = pd.read_csv(data_dir+data_2+".csv")

NumPCT = min(len(T1), len(T2))
lengCM = T1.iloc[0, 22]  # Assuming indexing starts from 0
RSSI = T1.iloc[packet, 3]

try:
    Timestamp = np.array(T1.iloc[:,27])
    Timestamp = Timestamp-Timestamp[0]
    Time = Timestamp
    # print(Time)
except:
    print("No Timestamp")
    Time = np.arange(0, NumPCT)

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


PhaseSubShiftHighSelect1 = np.unwrap(np.angle(CSubShiftHighSelect1))
PhaseSubShiftHighSelect2 = np.unwrap(np.angle(CSubShiftHighSelect2))

yy1, yy2 = [], []

for i in range(NumPCT):
    cs1 = CubicSpline(SubChannelSelect, PhaseSubShiftHighSelect1[i])
    cs2 = CubicSpline(SubChannelSelect, PhaseSubShiftHighSelect2[i])

    yy1.append(cs1(SubChannel))
    yy2.append(cs2(SubChannel))

yy1 = np.array(yy1)
yy2 = np.array(yy2)


# ... [your code before plotting remains unchanged]

fig = plt.figure(figsize=(12, 8))

# Main gridspec layout
gs_main = gridspec.GridSpec(2, 2, height_ratios=[2, 1.2])

# Nested gridspec layout for the first larger subplot
gs_nested = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs_main[0, 0])
gs_nested2 = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs_main[0, 1])
gs_nested3 = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs_main[1, 1], height_ratios=[1, 3])


# First two nested subplots
med = np.median(PMatrix1[packet])
ax1 = plt.Subplot(fig, gs_nested[0])
ax1.plot(PMatrix1[packet], linewidth=2, color='blue')
# ax1.axhline(med, color='red', linestyle='--', label='Median')
ax1.set_ylabel("Phase #1 (rad)")
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
# ax1.set_ylim([-200,200])
ax1.set_title("Phase of selected packet")
if data_1 == data_2:
    ax1.set_xlabel("subcarrier in raw order")
fig.add_subplot(ax1)

med = np.median(PMatrix2[packet])
ax2 = plt.Subplot(fig, gs_nested[1])
if data_1 == data_2:
    ax2.plot(SubChannelSelect,PhaseSubShiftHighSelect2.T)
    ax2.set_xlabel("subcarrier in sub channel order")
    ax2.set_ylabel("Phase #1 (rad)")
    # ax2.set_ylim([-200, 200])
elif alt_plot == True:
    ax2.plot(np.unwrap(np.mean(
        PhaseSubShiftHighSelect1[:, 8:120] - PhaseSubShiftHighSelect2[:, 8:120], axis=1)))
    # ax2.plot(SubChannelSelect, (PhaseSubShiftHighSelect2.T - PhaseSubShiftHighSelect1.T))

else:
    ax2.plot(PMatrix2[packet], linewidth=2, color='blue')
    ax2.set_ylabel("Phase #2 (rad)")
    ax2.set_xlabel("subcarrier in raw order")
ax2.grid(True, which='both', linestyle='--', linewidth=0.5)

# ax2.set_ylim([-200, 200])

fig.add_subplot(ax2)

# Remaining subplots
med = np.median(yy1[packet])
ax3 = plt.Subplot(fig, gs_nested2[0])
ax3.plot(SubChannel, yy1[packet], 'bx')
ax3.set_ylim([med-2, med+2])
ax3.grid(True, which='both', linestyle='--', linewidth=0.5)
ax3.set_title("Phase after Cubic Spline fitting")
fig.add_subplot(ax3)

med = np.median(yy2[packet])
ax4 = plt.Subplot(fig, gs_nested2[1])
if data_1 == data_2:
    ax4.plot(SubChannel, yy1.T)
    ax4.set_ylim([-300, 300])
else:
    ax4.plot(SubChannel, yy2[packet], 'bx')
    ax4.set_ylim([med-2, med+2])

ax4.grid(True, which='both', linestyle='--', linewidth=0.5)
ax4.set_xlabel("subcarrier in sub channel order")
fig.add_subplot(ax4)

med = np.median(yy1[packet]-yy2[packet])
ax5 = plt.Subplot(fig, gs_main[1, 0])
ax5.plot(SubChannel, yy1[packet]-yy2[packet], 'bx')
ax5.grid(True, which='both', linestyle='--', linewidth=0.5)
# ax5.set_ylim([-200, 200])
ax5.set_ylim([med-2, med+2])

ax5.set_ylabel("Phase (rad)")
ax5.set_xlabel("subcarrier in sub channel order")
ax5.set_title("\u0394Phase #1-#2 for selected packet")

fig.add_subplot(ax5)

stan = np.std((yy1[:, 8:120]*180/np.pi-yy2[:, 8:120]*180/np.pi), axis=1)
new_stan = stan[stan < 100]
# print((new_stan))

# print(len(stan))

# plt.hist(stan, bins=20)
Phase_avg = np.unwrap(np.mean(PhaseSubShiftHighSelect1[:] - PhaseSubShiftHighSelect2[:], axis=1))



ffit = np.polyfit(Time, Phase_avg, 1)
yfit = np.polyval(ffit, Time)

ax6 = plt.Subplot(fig, gs_main[1,1])
ax6.plot(Time, Phase_avg, 'k.', Time, yfit, 'r-')
ax6.set_xlabel('Time [s]')
ax6.set_ylabel('mean ' + r'$\phi_2 - \phi_1$ [rad]')
ax6.legend(['data', f'linear fit y={ffit[0]:.2f}x + {ffit[1]:.2f}'])
fig.add_subplot(ax6)

# print(ffit)


results = PrettyTable()

# Set column names
# , "Packets with \u0394Phase Std. Dev. < 5", "% Packets"]
if data_1==data_2:
    results.field_names = ["Packet No.", "RSSI", "Total Packets"]

    # Add rows
    num_sel_packets = len(new_stan[new_stan < 5])
    results.add_row([packet, 
                    RSSI, NumPCT])  # , num_sel_packets, helper.to_3_sig(num_sel_packets*100/NumPCT)])

else:
    results.field_names = ["Packet No.", "\u0394Phase Std. Dev.", "RSSI", "Total Packets",  "Slope"]

    # Add rows
    num_sel_packets = len(stan[stan < 5])
    results.add_row([packet, helper.to_3_sig(stan[packet]), RSSI, NumPCT,  helper.to_3_sig(ffit[0])])


print(results)

plt.tight_layout()

plt.show()