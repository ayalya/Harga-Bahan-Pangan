import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from model import transpose_time_series_data, fcm_model, day_to_week
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
import pandas as pd
import math
from dtaidistance import dtw

app = dash.Dash(__name__)

st.set_page_config(page_title="Dashboard FCM-DTW", layout="wide")

# ===================   CSS Script   ====================

st.markdown(
    """
<style>
.big-font{
font-size:30px !important;
padding-top: 2rem;
padding-bottom: 4em;
}
.subheading{
font-size:25px !important;}
.sub-subheading{
font-size=18px !important;
padding-top=0.5rem;}
.width{
padding-bottom: 1rem;}
[data-testid="stMetricValue"] {
        font-size: 30px;   /* ubah angka metric */
    }
    [data-testid="stMetricLabel"] {
        font-size: 20px;   /* ubah label metric */
    }
</style>
""",
    unsafe_allow_html=True,
)

# ===================   LOAD DATA   ====================

pangan = [
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
    data = data.drop(pangan, axis=1)

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
    data = day_to_week(data)
    return data


def load_data_norm():
    df = pd.read_csv(
        "https://github.com/ayalya/Harga-Bahan-Pangan/raw/main/Data/csv/data_mingguan_norm.csv"
    )
    df = df.drop(columns=["Tahun", "Unnamed: 0"])
    return df


data = load_data()
data_norm = load_data_norm()

# =================== FUNGSI-FUNGSI    ======================
# Visualisasi diagram garis menggunakan plotly


def diagram_garis_bapok(df):
    """
    Visualisasi semua data menggunakan Plotly
    Parameter:
    df: DataFrame yang digunakan
    output:
    visualisasi data komoditas secara keseluruhan
    """

    # Tambah tombol buat data normalisasi
    st.markdown('<h3 class="subheading">Data Time Series</h3>', unsafe_allow_html=True)

    # pilih = st.segmented_control("", opsi, selection_mode='single')
    on = st.toggle("Pakai Data Normalisasi")

    # Reshape data
    if on:  # opsi=='Normalisasi':
        df = data_norm
        y_label = "Nilai (Scale)"
        y="Nilai"
        data_log = df.melt(
            id_vars=["Minggu ke"], value_vars=pangan, var_name="Komoditas", value_name=y
        )
        # fig = px.line(data_log, x="Minggu ke", y=y, color='Komoditas')
    else:
        st.write("Harga asli")
        df = data
        y_label = "Harga (Rp)"
        y = "Harga"
        data_log = df.melt(
            id_vars=["Minggu ke"], value_vars=pangan, var_name="Komoditas", value_name=y
        )
        # fig = px.line(data_log, x='Minggu ke', y='y', color='Komoditas')

    fig = go.Figure()
    for komoditas in data_log["Komoditas"].unique():
        subset = data_log[data_log["Komoditas"] == komoditas]
        fig.add_trace(
            go.Scatter(x=subset["Minggu ke"], y=subset[y], mode="lines", name=komoditas)
        )

    fig.update_yaxes(type="linear")

    fig.update_layout(margin=dict(t=25, b=20, l=10, r=10), height=400, 
                      xaxis_title="Minggu ke",
                      yaxis_title=y_label,)
    st.plotly_chart(fig)


def alignment_and_counting_dtw():
    """
    Menghitung dan visualisasi jarak antara dua komoditas menggunakan Dynamic Time Warping.
    """
    col1, col2 = st.columns([1, 2])

    # Pilih komoditas
    with col1:
        st.markdown(
            '<h3 class="subheading">Ukur Jarak DTW</h3>', unsafe_allow_html=True
        )
        names1 = st.selectbox(
            "Time-series 1", list(pangan), index=list(pangan).index("Cabai Merah")
        )
        names2 = st.selectbox(
            "Time-series 2", list(pangan), index=list(pangan).index("Cabai Rawit")
        )

        if names1 == names2:
            st.warning("Data yang dimasukkan sama")
            return

        s1 = data_norm[names1].values
        s2 = data_norm[names2].values

        distance, path = dtw.warping_paths(s1, s2)
        best_path = dtw.best_path(path)

        # st.write(f"Jarak = {distance:.4f}")
        m1, m2, m3 = st.columns(3)
        with m2:
            # st.write(f"Jarak = {distance:.4f}")
            st.metric(label="Jarak", value=distance.round(4))

    # Buat figure Plotly
    fig = go.Figure()

    # Tambahkan kedua time-series
    fig.add_trace(go.Scatter(y=s1, mode="lines", name=names1, line=dict(color="blue")))
    fig.add_trace(
        go.Scatter(y=s2, mode="lines", name=names2, line=dict(color="orange"))
    )

    # Tambahkan garis penghubung DTW path
    for a, b in best_path[:: max(1, len(best_path) // 200)]:
        # ambil subset supaya tidak terlalu banyak garis
        fig.add_trace(
            go.Scatter(
                x=[a, b],
                y=[s1[a], s2[b]],
                mode="lines",
                line=dict(color="grey", width=1, dash="dot"),
                showlegend=False,
            )
        )

    # Layout
    fig.update_layout(
        margin=dict(t=20, l=40, r=20, b=40),
        # title=f"Jarak = {distance:.4f}",
        xaxis_title="Index (waktu/minggu)",
        yaxis_title="Nilai (scaled)",
        template="plotly_white",
        height=350,
        legend=dict(
            x=0.95,  # posisi horizontal (0=left, 1=right)
            y=0.95,  # posisi vertikal (0=bottom, 1=top)
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.6)",  # background semi-transparan
            bordercolor="black",
            borderwidth=1,
        ),
    )

    with col2:
        st.plotly_chart(fig, use_container_width=True)


# ===================   MODEL FCM   ======================


def pilih_jmlh_cluster():
    """
    Memilih parameter dan melatih model
    Output:
    df_evaluasi_cluster: DataFrame berisi metrik evaluasi klaster (MPC, PE, dan XB)
    df_derajat_keanggotaan: DataFrame berisi derajat keanggotaan dan anggota klaster
    """
    st.markdown(
        '<h6 class="sub-subheading">Parameter Klaster</h6>', unsafe_allow_html=True
    )
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        jmlh_cluster = [2, 3, 4, 5]
        c = st.selectbox(
            "Jml Klaster (c)", list(jmlh_cluster), index=list(jmlh_cluster).index(3)
        )
    with col2:
        m = st.number_input("Fuzziness (m)", value=1.5, format="%.1f")
    with col3:
        error = st.number_input("Error", value=0.001, format="%.3f")
    with col4:
        maxiter = st.number_input("Maks Iterasi", value=100)

    if c == 3 and m == 1.5 and error == 0.001 and maxiter == 100:
        st.write("*parameter terbaik untuk model")

    # Normalisasi Data
    data_for_fcm = transpose_time_series_data(data_norm)

    # Melatih model FCM
    df_evaluasi_cluster, df_derajat_keanggotaan = fcm_model(
        data_for_fcm, c=c, m=m, error=error, maxiter=maxiter
    )
    return df_evaluasi_cluster, df_derajat_keanggotaan


def visualisasi_hasil_cluster(
    df_data,
    df_cluster,
    datetime_col="Minggu ke",
    nama_bahan_col="Bahan Pangan",
    cluster_col="Anggota Cluster",
):
    """
    Visualisasi dari hasil setiap klaster
    Parameter
    df_date: DataFrame yang digunakan untuk visualisasi
    df_cluster: DataFrame dengan hasil defuzzifikasi dan komoditas
    Output:
    Visualisasi diagram garis hasil masing-masing cluaster
    """
    clusters = sorted(df_cluster[cluster_col].unique())

    for cl in clusters:
        # Ambil nama bahan pangan dalam cluster
        bahan_in_cluster = df_cluster[df_cluster[cluster_col] == cl][
            nama_bahan_col
        ].to_list()
        col_in_df = [col for col in bahan_in_cluster if col in df_data.columns]

        if not col_in_df:
            st.warning(f"Tidak ada kolom ditemukan untuk Cluster {cl}")
            continue

        # Ubah ke long format untuk mudah dipakai di plotly
        data_long = df_data.melt(
            id_vars=[datetime_col],
            value_vars=col_in_df,
            var_name="Komoditas",
            value_name="Nilai (Skala)",
        )

        # Buat line chart untuk cluster ini
        fig = px.line(
            data_long,
            x=datetime_col,
            y="Nilai (Skala)",
            color="Komoditas",
            title=f"Cluster {cl}",
        )

        # Layout styling
        fig.update_layout(
            height=250,
            margin=dict(t=25, b=20, l=10, r=10),
            title=dict(x=0.5, xanchor="center"),
            legend=dict(font=dict(size=10), orientation="v"),
        )
        fig.update_xaxes(showline=True, linewidth=1, linecolor="black", mirror=True)
        fig.update_yaxes(showline=True, linewidth=1, linecolor="black", mirror=True)

        st.plotly_chart(fig, use_container_width=True)


# =================== TAMPILAN ASLI   ======================

st.markdown(
    '<h2 class="big-font">CLUSTERING HARGA BAHAN PANGAN PROVINSI BANTEN</h2>',
    unsafe_allow_html=True,
)
# st.markdown('<p class="width">Model dibangun menggunakan algoritma Fuzzy C-Means Clustering dengan jarak kedekatan Dynamic Time Warping (DTW)</p>', unsafe_allow_html=True)

# Menampilkan Fuzzy C-Means
colhead1, colhead2 = st.columns([2.5, 1.5])
with colhead2:
    df_evaluasi, df_derajat_keanggotaan = pilih_jmlh_cluster()

    st.markdown('<p class="sub-subheading"> </p>', unsafe_allow_html=True)
    metric1, metric2, metric3 = st.columns(3)
    with metric1:
        st.metric(label="MPC", value=df_evaluasi["MPC"].round(4))
    with metric2:
        st.metric(label="PE", value=df_evaluasi["PE"].round(4))
    with metric3:
        st.metric(label="XB", value=df_evaluasi["XB"].round(4))

    st.markdown(
        '<h6 class="sub-subheading">Derajat Keanggotaan</h6>', unsafe_allow_html=True
    )
    df_derajat_keanggotaan = df_derajat_keanggotaan.reset_index(drop=True)
    st.dataframe(df_derajat_keanggotaan)

with colhead1:
    visualisasi_hasil_cluster(data_norm, df_derajat_keanggotaan)

# Menghitung jarak pada DTW
alignment_and_counting_dtw()

diagram_garis_bapok(data)
