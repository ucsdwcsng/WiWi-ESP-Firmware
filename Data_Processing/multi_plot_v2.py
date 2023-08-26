import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
import helper
import matplotlib.gridspec as gridspec
from prettytable import PrettyTable


data_dir = "/Users/sureel/VS_Code/wiwi-time-sync/Data/"

# data_1 = "CSI_1"
# data_2 = "CSI_2"

data_1 = "S3_wired_intclk_1_2"
data_2 = "S3_wired_intclk_2_2"

helper.match_packets(data_1, data_2, data_dir)

packet = 15  # This is the chosen packet for analysis


# Read tables from CSV files
T1 = pd.read_csv(data_dir+data_1+".csv")
T2 = pd.read_csv(data_dir+data_2+".csv")

NumPCT = min(len(T1), len(T2))
lengCM = T1.iloc[0, 22]  # Assuming indexing starts from 0
RSSI = T1.iloc[packet, 3]

CMatrix1 = helper.process_csi(T1)
CMatrix2 = helper.process_csi(T2)

SubChannel = np.arange(-64, 64)
CSub1 = np.column_stack((CMatrix1[:, 128:192], CMatrix1[:, 64:128]))
CSub2 = np.column_stack((CMatrix2[:, 128:192], CMatrix2[:, 64:128]))

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

PMatrix1 = (np.unwrap(np.angle(CMatrix1)))*180/np.pi
PMatrix2 = (np.unwrap(np.angle(CMatrix2)))*180/np.pi


PhaseSubShiftHighSelect1 = np.unwrap(
    np.angle(CSubShiftHighSelect1), axis=1)*180/np.pi
PhaseSubShiftHighSelect2 = np.unwrap(
    np.angle(CSubShiftHighSelect2), axis=1)*180/np.pi

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
ax1.set_ylabel("Phase #1 (deg)")
ax1.grid(True, which='both', linestyle='--', linewidth=0.5)
# ax1.set_ylim([-200,200])
ax1.set_title("Phase of selected packet")
fig.add_subplot(ax1)

med = np.median(PMatrix2[packet])
ax2 = plt.Subplot(fig, gs_nested[1])
if data_1 == data_2:
    ax2.plot(PhaseSubShiftHighSelect2.T)
    ax2.set_ylim([-200, 200])
else:
    ax2.plot(PMatrix2[packet], linewidth=2, color='blue')
ax2.grid(True, which='both', linestyle='--', linewidth=0.5)
ax2.set_ylabel("Phase #2 (deg)")
ax2.set_xlabel("subcarrier in raw order")
# ax2.set_ylim([-200, 200])

fig.add_subplot(ax2)

# Remaining subplots
med = np.median(yy1[packet])
ax3 = plt.Subplot(fig, gs_nested2[0])
ax3.plot(SubChannel, yy1[packet], 'bx')
ax3.set_ylim([med-50, med+50])
ax3.grid(True, which='both', linestyle='--', linewidth=0.5)
ax3.set_title("Phase after Cubic Spline fitting")
fig.add_subplot(ax3)

med = np.median(yy2[packet])
ax4 = plt.Subplot(fig, gs_nested2[1])
if data_1 == data_2:
    ax4.plot(SubChannel, yy1.T)
    ax4.set_ylim([-200, 200])
else:
    ax4.plot(SubChannel, yy2[packet], 'bx')
    ax4.set_ylim([med-50, med+50])

ax4.grid(True, which='both', linestyle='--', linewidth=0.5)
ax4.set_xlabel("subcarrier in sub channel order")
fig.add_subplot(ax4)

med = np.median(yy1[packet]-yy2[packet])
ax5 = plt.Subplot(fig, gs_main[1, 0])
ax5.plot(SubChannel, yy1[packet]-yy2[packet], 'bx')
ax5.grid(True, which='both', linestyle='--', linewidth=0.5)
# ax5.set_ylim([-200, 200])
ax5.set_ylim([med-50, med+50])

ax5.set_ylabel("Phase (deg)")
ax5.set_xlabel("subcarrier in sub channel order")
ax5.set_title("\u0394Phase #1-#2 for selected packet")

fig.add_subplot(ax5)

stan = np.std((yy1[:, 8:120]-yy2[:, 8:120]), axis=1)
# print((stan))
stan = stan[stan < 100]
# print(len(stan))

# plt.hist(stan, bins=20)

ax6 = plt.Subplot(fig, gs_nested3[1])
ax6.hist(stan, bins=20, color='blue', edgecolor='black')
ax6.set_ylabel("No. of Packets (#)")
ax6.set_xlabel("\u0394Phase (deg)")

ax6.set_xlim((0, 30))
ax6.grid(axis='y', alpha=0.75)
fig.add_subplot(ax6)

ax7 = plt.Subplot(fig, gs_nested3[0])
ax7.boxplot(stan, vert=False,  widths=0.8)
ax7.set_yticks([])
ax7.set_xlim((0, 30))
ax7.set_ylabel('Boxplot', color='black')
ax7.set_title("Histogram of Std, Dev. of \u0394Phase #1-#2 across Sub-C [8-120]")
fig.add_subplot(ax7)

results = PrettyTable()

# Set column names
# , "Packets with \u0394Phase Std. Dev. < 5", "% Packets"]
results.field_names = ["Packet No.",
                       "\u0394Phase Std. Dev.", "RSSI", "Total Packets"]

# Add rows
num_sel_packets = len(stan[stan < 5])
results.add_row([packet, helper.to_3_sig(stan[packet]),
                RSSI, NumPCT])  # , num_sel_packets, helper.to_3_sig(num_sel_packets*100/NumPCT)])
print(results)

plt.tight_layout()

plt.show()