import numpy as np
import pandas as pd
import math
from tqdm import tqdm
from dtaidistance import dtw, preprocessing

komoditas = [
    "Beras",
    "Bawang Merah",
    "Bawang Putih",
    "Cabai Merah",
    "Cabai Rawit",
    "Daging Sapi",
    "Telur Ayam",
    "Daging Ayam",
    "Minyak Goreng",
    "Gula Pasir",
]


def load_data():
    data = pd.read_csv(
        "https://github.com/ayalya/Harga-Bahan-Pangan/raw/main/Data/csv/HargaBahanPangan2020-2024.csv"
    )
    data = data.drop(komoditas, axis=1)

    data = data.rename(
        columns={
            "Komoditas (Rp)": "Tanggal",
            "Beras Kualitas Medium I": "Beras",
            "Bawang Merah Ukuran Sedang": "Bawang Merah",
            "Bawang Putih Ukuran Sedang": "Bawang Putih",
            "Cabai Merah Keriting": "Cabai Merah",
            "Cabai Rawit Merah": "Cabai Rawit",
            "Daging Sapi Kualitas 1": "Daging Sapi",
            "Telur Ayam Ras Segar": "Telur Ayam",
            "Daging Ayam Ras Segar": "Daging Ayam",
            "Minyak Goreng Kemasan Bermerk 1": "Minyak Goreng",
            "Gula Pasir Lokal": "Gula Pasir",
        }
    )
    data["Tanggal"] = pd.to_datetime(data["Tanggal"], format="%d/%m/%Y")
    return data


def day_to_week(data):
    """
    Mengubah bentuk data dari tanggal ke mingguan
    """
    # Urutkan berdasarkan tanggal
    data_mingguan = data.sort_values(by="Tanggal").reset_index(drop=True)

    # Membuat minggu di kolom pertama
    data_mingguan["Minggu ke"] = None
    data.loc[data["Tanggal"].between("2020-01-01", "2020-01-03"), "Minggu ke"] = 1

    # Filter hari kerja
    data_sisa = data.loc[
        data_mingguan["Minggu ke"].isna() & data["Tanggal"].dt.weekday < 5
    ].copy()

    # Hitung minggu ke berdasarkan hari kerja setelah 3 Januari 2020
    data_sisa["Minggu ke"] = (
        (data_sisa["Tanggal"] - pd.Timestamp("2020-01-06")).dt.days // 7
    ) + 2

    # gabungkan kembali data
    data_mingguan.update(data_sisa)

    # data_mingguan['Tahun'] = data['Tanggal'].dt.year

    data_mingguan["Minggu ke"] = data_mingguan["Minggu ke"].astype("Int64")

    data_mingguan = data_mingguan.drop(columns=["Tanggal"])
    # Hitung rata-rata per minggu, otomatis mengabaikan NaN
    data_mingguan = (
        data_mingguan.groupby("Minggu ke")
        .agg(lambda x: x[x > 0].mean(skipna=True))
        .reset_index()
    )

    # Mengisi nilai yang kosong dengan rata-rata sebelum dan sesudah nilai kosong
    data_mingguan[komoditas] = data_mingguan[komoditas].interpolate(method="linear")

    return data_mingguan


def z_normalization(df, col=komoditas):
    """Fungsi untuk standarisasi data pada masing-masing harga pangan
    Parameter:
    df : DataFrame yang berisi harga pangan
    col : kolom yang akan distandarisasi (list)
    """
    df_norm = df.copy()
    df_norm[col] = preprocessing.znormal(df[col])
    return df_norm


def transpose_time_series_data(data):
    """
    Method mengubah bentukdata time series menjadi value dengan dimensi mxn
    - m: data time-series
    - n: variable komoditas pangan
    """
    data_for_fcm = data.drop(columns=["Minggu ke"])
    data_for_fcm = data_for_fcm.T.values
    return data_for_fcm


# ===================== MODEL =========================
def initialize_membership(n_sampels, c):
    """
    Fungsi inisiasi membership (langkah 1). Dipilih secara acak.
    Parameter:
    - n_sampels: jumlah data
    - c: jumlah cluster
    Output:
    u: matriks keanggotaan
    """
    u = np.random.rand(c, n_sampels)
    u = u / np.sum(u, axis=0, keepdims=True)
    return u


def compute_centroids(data, u, m):
    """
    Fungsi menghitung setiap data ke centroid
    Parameter:
    - data: data time-series yang akan dihitung
    - u: keanggotaan matriks
    - m: derajat (fuzziness)
    Output:
    centorids: pusat cluster (v_k)
    """
    c = u.shape[0]
    centroids = []
    for j in range(c):
        weights = u[j] ** m
        weighted_sum = np.zeros_like(data[0])
        denominator = np.sum(weights)
        for i in range(len(data)):
            weighted_sum += weights[i] * data[i]
        centroid = weighted_sum / denominator
        centroids.append(centroid)
    return centroids


def update_membership_dtw(data, centroids, m):
    """
    Fungsi update membership menggunakan kesamaan jarak DTW (langkah 5).
    Parameter:
    - data: data time-series yang akan dihitung
    - centroids: pusat cluster
    - m: derajat fuzziness
    Output:
    - u_new: centroid baru yang sudah diperbarui
    """
    c = len(centroids)
    n = len(data)
    u_new = np.zeros((c, n))

    for i in range(n):
        for j in range(c):
            denom = sum(
                [
                    (
                        (
                            dtw.distance_fast(data[i], centroids[j], use_pruning=True)
                            + 1e-6
                        )
                        / (
                            dtw.distance_fast(data[i], centroids[k], use_pruning=True)
                            + 1e-6
                        )
                    )
                    ** (2 / (m - 1))
                    for k in range(c)
                ]
            )
            u_new[j, i] = 1 / denom
    return u_new


def compute_objective_function(u, centroids, data, m):
    """
    Fungsi objektif Fuzzy C-Means dengan DTW sebagai metrik jarak (langkah 3)

    Parameter:
    - u: matriks keanggotaan (c x n)
    - centroids: array (c x t)
    - data: array (n x t)
    - m: derajat fuzziness
    Return:
    - jm: nilai fungsi objektif
    """
    c, n = u.shape
    jm = 0.0
    for i in range(c):
        for k in range(n):
            dist = dtw.distance_fast(data[k], centroids[i])
            jm += (u[i][k] ** m) * (dist**2)
    return jm


def fcm_with_dtw_model(data, c, m, error, maxiter):
    n_sampels = len(data)

    #  2) Inisiasi matriks acak U
    u = initialize_membership(n_sampels, c)

    jm_old = np.inf
    for iteration in tqdm(range(maxiter)):

        # 3) Menghitung jarak ke centroid
        centroids = compute_centroids(data, u, m)

        # 4) Memperbarui elemen matriks
        u = update_membership_dtw(data, centroids, m)

        # 5) Menghitung dan memperbarui fungsi objektif
        jm = compute_objective_function(u, centroids, data, m)

        # Eary Stopping
        # if np.linalg.norm(u - u_old) < error:
        #     break
        if abs(jm-jm_old)<error:
            break

        jm_old=jm

    return centroids, u


# ===================== EVALUASI KLASTER =========================


def compute_mpc(u):
    """
    Modified Partition Coefficient (MPC)
    Nilai ideal: mendekati 1, maksimal = 1
    """
    n = u.shape[1]  # jumlah data
    c = u.shape[0]  # jumlah cluster
    MPC = 1 - (c / (c - 1)) * (1 - (np.sum(u**2) / n))
    return MPC


def compute_pc(u):
    """
    Partition Coefficient (PC) atau Fuzzy Partition Coefficient (FPC)
    Nilai ideal: mendekati 1
    """
    n = u.shape[1]  # jumlah data
    PC = np.sum(u**2) / n
    return PC


def compute_pe(u):
    """
    Partition Entropy (PE)
    Nilai ideal: mendekati 0 (semakin jelas)
    """
    n = u.shape[1]  # jumlah data
    PE = -np.sum(u * np.log(u + 1e-10)) / n
    return PE


def compute_xb(data, centroids, u, m):
    """
    Menghitung Xie-Beni Index menggunakan DTW.
    - data: list atau array shape (n_samples, time_steps)
    - centroids: list atau array shape (n_clusters, time_steps)
    - u: matriks keanggotaan shape (n_clusters, n_samples)
    """
    n_samples = u.shape[1]
    c = u.shape[0]

    numerator = 0.0
    for i in range(n_samples):  # data
        x_i = np.array(data[i], dtype=np.float64)  # pastikan bertipe float
        for j in range(c):  # centroid
            v_j = np.array(centroids[j], dtype=np.float64)
            dist = dtw.distance(x_i, v_j)
            numerator += (u[j, i] ** m) * (dist**2)

    # Cari jarak minimum antar centroid
    min_dist = np.inf
    for j in range(c):
        for k in range(j + 1, c):
            v_j = np.array(centroids[j], dtype=np.float64)
            v_k = np.array(centroids[k], dtype=np.float64)
            dist = dtw.distance(v_j, v_k)
            if dist < min_dist:
                min_dist = dist

    denominator = n_samples * (min_dist**2)
    xb_index = numerator / denominator
    return xb_index


# ===================== IMPLEMENTASI MODEL FCM =========================
def fcm_model(
    data,
    c,
    m,
    error,
    maxiter,
    columns_name=komoditas,
):
    """
    Implementasi dalam melatih model Fuzzy C-Means pada satu set data dan satu kali pelatihan.

    Parameters:
    - data: DataFrame atau array dengan shape(n_samples, n_features)
    - c: jumlah cluster
    - m: derajat fuzziness
    - error: toleransi error
    - maxiter: maksimal iterasi

    Return/Output:
    - df_evaluasi = DataFrame evaluasi klaster
    - df_results = DataFrame berisi keanggotaan klaster
    """

    result_eval = []

    # Training FCM
    cntr, u = fcm_with_dtw_model(data=data, c=c, m=m, error=error, maxiter=maxiter)

    mpc_value = compute_mpc(u)
    pe_value = compute_pe(u)
    xb_value = compute_xb(data, cntr, u, m=m)

    result_eval.append(
        {"Jumlah klaster": c, "MPC": mpc_value, "PE": pe_value, "XB": xb_value}
    )

    df_evaluasi_cluster = pd.DataFrame(result_eval)

    # Defuzzifikasi
    cluster_membership = np.argmax(u, axis=0) + 1

    # DataFrame hasil cluster
    df_result = pd.DataFrame(
        {
            "Bahan Pangan": columns_name,
            "Anggota Cluster": cluster_membership,
        }
    )

    # Derajat keanggotaan
    for i in range(c):
        df_result[f"Cluster {i+1}"] = np.round(u[i], 6)

    return df_evaluasi_cluster, df_result


# ==================== IMPLEMENTASI METHOD ==========
data = load_data()

# Mengubah ke data mingguan
data_mingguan = day_to_week(data)

# Normalisasi data
data_scaled = z_normalization(data_mingguan)

# Transpose data
data_for_fcm = transpose_time_series_data(data_scaled)

# Implementasi model
df_evaluasi_cluster, df_derajat_keanggotaan = fcm_model(
    data_for_fcm, c=3, m=1.5, error=0.0001, maxiter=100
)
print("Model Selesai")
print("Evaluasi klaster:")
print(df_evaluasi_cluster)
print("\nDerajat Keanggotaan dan Defuzzifikasi")
print(df_derajat_keanggotaan)
