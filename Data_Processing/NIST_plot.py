import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data_dir = "/Users/sureel/VS_Code/wiwi-time-sync/Data/"

data_1 = "S3_wireless_intclk_1_2"
data_2 = "S3_wireless_intclk_2_2"

# Read tables from CSV files
T1 = pd.read_csv(data_dir+data_1+".csv")
T2 = pd.read_csv(data_dir+data_2+".csv")

lengCM = T1.iloc[0, 22]  # assuming the indices in MATLAB start from 1

CMatrix1 = []
PMatrix1 = []
CMatrix2 = []
PMatrix2 = []

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

PMatrix1 = np.array(PMatrix1)
PMatrix2 = np.array(PMatrix2)

PDiff = PMatrix2 - PMatrix1

plt.figure(figsize=(8, 10))

# Plot
plt.subplot(4, 1, 1)
plt.plot(np.unwrap(PMatrix1[0, :] * 180 / np.pi))
plt.xlabel('subcarrier')
plt.ylabel('Phase #1 [rad]')

plt.subplot(4, 1, 2)
plt.plot(np.unwrap(PDiff[0, :] * 180 / np.pi))
plt.xlabel('subcarrier')
plt.ylabel('\Delta phase #2-#1 [deg]')

# PDiffSel = np.delete(PDiff, 32, axis=1)  # delete 33rd column
PDiffSel = PDiff[:, list(range(6, 32)) + list(range(33, 59))]
# PDiffSel = PDiff
PDiffSelUW = np.unwrap(PDiffSel)
PhopAve = np.mean(PDiffSelUW, axis=1)

plt.subplot(4, 1, 3)
plt.plot((np.transpose(PDiffSelUW) * 180 / np.pi))
plt.xlabel('Selected Subcarrier(7~59, skip 33)')
plt.ylabel('\Delta phase [deg]')

plt.subplot(4, 1, 4)
plt.plot(np.unwrap(PhopAve) * 180 / np.pi)
plt.xlabel('Packet Number')
plt.ylabel('\Delta phase [deg]')

plt.tight_layout()
plt.show()

print(np.std(np.unwrap(PhopAve) * 180 / np.pi))