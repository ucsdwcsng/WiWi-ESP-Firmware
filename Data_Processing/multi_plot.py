# %%
import numpy as np
import matplotlib.pyplot as plt
import helper


data_dir = "/Users/sureel/VS_Code/wiwi-time-sync/Data/"

csi_long = dict()
csi_long2 = dict()

file_1 = "S3_wireless_intclk_1_2.csv"
file_2 = "S3_wireless_intclk_2_2.csv"

helper.match_packets(file_1, file_2, data_dir) # Comment this out if packet matching is not required 

csi_long["l"], csi_long["h"], all_data = helper.load_csi(f"{data_dir+file_1}",
                                                         helper.legacy_list, helper.ht_list)

dc_phases_movement, slopes_movement = helper.compute_offsets(
    csi_long['h'], helper.f_sub, helper.f_c)

csi_long2["l"], csi_long2["h"], all_data2 = helper.load_csi(f"{data_dir+file_2}",
                                                            helper.legacy_list, helper.ht_list)

dc_phases_movement2, slopes_movement2 = helper.compute_offsets(
    csi_long2['h'], helper.f_sub, helper.f_c)

# Plotting using subplots
fig, axs = plt.subplots(3, 2, figsize=(10, 8))
fig.tight_layout(pad=5.0)

# Plot the phases across subcarriers for first dataset
skip_rows = 1
phases = np.unwrap(np.angle(csi_long["h"]), axis=1) * 180 / np.pi
axs[2,1].plot(helper.f_sub, phases[::skip_rows][:].T)
axs[2,1].set_title("Phases across subcarriers (Dataset 1)")
axs[2,1].set_xlabel("Sub-C Frequency")
axs[2,1].set_ylabel("Phases (deg)")

# print(len(phases[0]))

# # Plot the phases across subcarriers for second dataset
phases2 = np.unwrap(np.angle(csi_long2["h"]), axis=1) * 180 / np.pi
# axs[0, 1].plot(helper.f_sub, phases2[::skip_rows][:].T)
# # axs[0, 1].plot(helper.f_sub, phases[::skip_rows].T - phases2[::skip_rows].T)
# axs[0, 1].set_title("Phases across subcarriers (Dataset 2)")
# axs[0, 1].set_xlabel("Sub-C Frequency")
# axs[0, 1].set_ylabel("Phases (deg)")

# Plot DC phases over packets for first dataset
# axs[1, 0].scatter(np.arange(len(dc_phases_movement)),(dc_phases_movement) * 180 / np.pi, s=5)
axs[0, 0].plot(helper.f_sub, phases[0][:] - phases2[0][:])
# axs[1].plot(helper.f_sub, phases[0][:] - phases2[0][:])

axs[0, 0].set_title("Phase Difference across subcarriers for Packet 1")
axs[0, 0].set_xlabel("Sub-C Frequency")
axs[0, 0].set_ylabel("Phases (deg)")

# Plot DC phases over packets for second dataset
# axs[1, 1].scatter(np.arange(len(dc_phases_movement2)),(dc_phases_movement2) * 180 / np.pi, s=5)
axs[0, 1].plot(np.arange(len(dc_phases_movement2)), np.unwrap(
    dc_phases_movement-dc_phases_movement2) * 180 / np.pi)
# axs[2].plot(np.arange(len(dc_phases_movement2)),(dc_phases_movement-dc_phases_movement2) * 180 / np.pi)

# axs[1, 1].plot((dc_phases_movement2) * 180 / np.pi, ".-")
axs[0, 1].set_title("DC phase difference")
axs[0, 1].set_xlabel("Packets")
axs[0, 1].set_ylabel("Phases (deg)")

axs[1, 0].plot(helper.f_sub, phases[::skip_rows].T - phases2[::skip_rows].T)
axs[1, 0].set_title("Phase difference across subcarriers")
axs[1, 0].set_xlabel("Sub-C Frequency")
axs[1, 0].set_ylabel("Phases (deg)")

# axs[4].plot((np.std(phases[::].T-phases2[::].T, axis=0)), ".-")
stddev_all = np.std(np.unwrap(phases[::].T-phases2[::].T), axis=0)
axs[1, 1].hist((stddev_all), bins=20)
axs[1, 1].set_title("Std. Dev. of phase difference across all Sub-C")
axs[1, 1].set_xlabel("Degress")
axs[1, 1].set_ylabel("No. of Packets")

# print((np.std(phases[::skip_rows].T-phases2[::skip_rows].T, axis=0)))
print("Std. Dev of DC Phase", np.std(
    np.unwrap(dc_phases_movement-dc_phases_movement2)*180/np.pi))
print("No. of packets, ", (np.std(phases[::].T-phases2[::].T, axis=0)).size)
# print(np.std(np.unwrap(dc_phases_movement-dc_phases_movement2)*180/np.pi))

# print((phases[0][:])- (phases2[0][:]))
# print((phases[1][:])- (phases2[1][:]))
# print((phases[3][:])- (phases2[3][:]))
# plt.figure()
mean_all = np.unwrap(np.mean(phases[:]-phases2, axis=1))
print(np.std(np.unwrap(np.angle(
    (np.exp(1j*dc_phases_movement) / np.exp(1j*dc_phases_movement2))))*180/np.pi))
axs[2,0].plot(mean_all)
axs[2,0].set_title("Mean phase difference across Sub-C vs Packets")
# axs[5].set_ylim((-200,200))
# plt.xlim((0,50))
print("Std. dev of mean phase across Sub-C: ", np.std(mean_all))
plt.tight_layout()

plt.show()


# %%
