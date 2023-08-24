import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
import helper
import matplotlib.gridspec as gridspec
from prettytable import PrettyTable


data_dir = "/Users/sureel/VS_Code/wiwi-time-sync/Data/"

data_1 = "CSI_1"
data_2 = "CSI_2"

data_1 = "S3_wired_intclk_2_1"
data_2 = "S3_wired_intclk_1_1"

# helper.match_packets(data_1, data_2, data_dir)

packet = 152


# Read tables from CSV files
T1 = pd.read_csv(data_dir+data_1+".csv")
T2 = pd.read_csv(data_dir+data_2+".csv")

NumPCT = min(len(T1), len(T2))
lengCM = T1.iloc[0, 22]  # Assuming indexing starts from 0
RSSI = T1.iloc[packet, 3]

C1, C2, CMatrix1, PMatrix1, CMatrix2, PMatrix2 = [], [], [], [], [], []

for index, row in T1.iterrows():
    C1 = list(map(int, row[24].strip('[]').split(',')))
    C2 = list(map(int, T2.iloc[index, 24].strip('[]').split(',')))

    c_matrix_1_row = []
    p_matrix_1_row = []
    c_matrix_2_row = []
    p_matrix_2_row = []

    for m in range(0, lengCM, 2):
        c1_complex = complex(C1[m + 1], C1[m])
        c_matrix_1_row.append(c1_complex)
        p_matrix_1_row.append(np.angle(c1_complex))

        c2_complex = complex(C2[m + 1], C2[m])
        c_matrix_2_row.append(c2_complex)
        p_matrix_2_row.append(np.angle(c2_complex))

    CMatrix1.append(c_matrix_1_row)
    PMatrix1.append(p_matrix_1_row)
    CMatrix2.append(c_matrix_2_row)
    PMatrix2.append(p_matrix_2_row)

PMatrix1 = np.unwrap(np.array(PMatrix1))*180/np.pi
PMatrix2 = np.unwrap(np.array(PMatrix2))*180/np.pi

SubChannel = np.arange(-64, 64)
PhaseSub1 = np.column_stack((PMatrix1[:, 128:192], PMatrix1[:, 64:128]))
PhaseSub2 = np.column_stack((PMatrix2[:, 128:192], PMatrix2[:, 64:128]))

PhaseSubShiftHigh1 = PhaseSub1.copy()
PhaseSubShiftHigh2 = PhaseSub2.copy()

for i in range(PhaseSubShiftHigh1.shape[0]):
    # shift1 = PhaseSubShiftHigh1[i, 15]-PhaseSubShiftHigh1[i, 105]
    shift1 = np.min(PhaseSubShiftHigh1[i, 6: 60]) - \
        np.max(PhaseSubShiftHigh1[i, 66: 120])
    multiplier1 = shift1//90+1
    # shift2 = PhaseSubShiftHigh2[i, 15]-PhaseSubShiftHigh2[i, 105]
    shift2 = np.min(PhaseSubShiftHigh2[i, 6: 60]) - \
        np.max(PhaseSubShiftHigh2[i, 66: 120])
    multiplier2 = shift2//90+1

    if shift1 > 0:
        PhaseSubShiftHigh1[i, 66:123] -= 90*multiplier1  # np.pi/2
    else:
        PhaseSubShiftHigh1[i, 66:123] += 90*multiplier1  # np.pi/2
    if shift1 > 0:
        PhaseSubShiftHigh2[i, 66:123] -= 90*multiplier2  # np.pi/2
    else:
        PhaseSubShiftHigh2[i, 66:123] += 90*multiplier2  # np.pi/2
    # PhaseSubShiftHigh2[i, 66:123] -= 90  # np.pi/2

SubChannelSelect = np.hstack((np.arange(-58, -1), np.arange(2, 59)))
PhaseSubShiftHighSelect1 = PhaseSubShiftHigh1[:, np.hstack(
    (np.arange(6, 63), np.arange(66, 123)))]
PhaseSubShiftHighSelect2 = PhaseSubShiftHigh2[:, np.hstack(
    (np.arange(6, 63), np.arange(66, 123)))]

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



# First two nested subplots
med = np.median(PMatrix1[packet])
ax1 = plt.Subplot(fig, gs_nested[0])
ax1.plot(PMatrix1[packet])
ax1.set_ylabel("Phase #1 (deg)")
ax1.set_ylim([-200,200])
ax1.set_title("Phase of selected packet")
fig.add_subplot(ax1)

med = np.median(PMatrix2[packet])
ax2 = plt.Subplot(fig, gs_nested[1])
ax2.plot(PMatrix2[packet])
ax2.set_ylabel("Phase #2 (deg)")
ax2.set_xlabel("subcarrier in raw order")
ax2.set_ylim([-200, 200])

fig.add_subplot(ax2)

# Remaining subplots
med = np.median(yy1[packet])
ax3 = plt.Subplot(fig, gs_nested2[0])
ax3.plot(SubChannel, yy1[packet], 'kx')
ax3.set_ylim([med-50, med+50])
ax3.set_title("Phase after Cubic Spline fitting")
fig.add_subplot(ax3)

med = np.median(yy2[packet])
ax4 = plt.Subplot(fig, gs_nested2[1])
ax4.plot(SubChannel, yy2[packet], 'kx')
ax4.set_ylim([med-50, med+50])
ax4.set_xlabel("subcarrier in sub channel order")
fig.add_subplot(ax4)

med = np.median(yy1[packet]-yy2[packet])
ax5 = plt.Subplot(fig, gs_main[1, 0])
ax5.plot(SubChannel, yy1[packet]-yy2[packet], 'kx')
# ax5.set_ylim([-200, 200])
ax5.set_ylim([med-50, med+50])

ax5.set_ylabel("Phase (deg)")
ax5.set_xlabel("subcarrier in sub channel order")
ax5.set_title("\u0394Phase #1-#2 for selected packet")

fig.add_subplot(ax5)

stan = np.std((yy1[:, 8:120]-yy2[:, 8:120]), axis=1)
print(len(stan))
stan = stan[stan < 100]
print(len(stan))

# plt.hist(stan, bins=20)

ax6 = plt.Subplot(fig, gs_main[1, 1])
ax6.hist(stan, bins=20)
ax6.set_ylabel("Frequency")
ax6.set_xlabel("\u0394Phase (deg)")
ax6.set_title("Histogram of Std, Dev. of \u0394Phase #1-#2 for selected packet")
fig.add_subplot(ax6)

# plt.tight_layout()

results = PrettyTable()

# Set column names
results.field_names = ["Packet No.", "\u0394Phase Std. Dev.", "RSSI", "Total Packets", "Packets with \u0394Phase Std. Dev. < 5", "% Packets"]

# Add rows
num_sel_packets =  len(stan[stan<5])
results.add_row([packet, helper.to_3_sig(stan[packet]),
                RSSI, lengCM, num_sel_packets, helper.to_3_sig(num_sel_packets*100/lengCM)])
# results.add_row(["Bob", 22, "Los Angeles"])
# results.add_row(["Charlie", 27, "San Francisco"])
print(results)
# print(stan)
plt.tight_layout()

plt.show()