## _Project Overview_

<!-- Pakai tabel biar bagus -->
Judul: Pengelompokan Data _Time-Series_ Harga Bahan Pangan Provinsi Banten menggunakan _Fuzzy C-Means_

### Abstract
Kondisi ketahanan pangan di Provinsi Banten yang kian menurun dan menyebabkan lonjakan harga bahan pangan dari waktu ke waktu. Pada tahun 2023, laju pengeluaran untuk kategori makanan di Provinsi Banten menjadi paling tinggi ke dua di Indonesia setelah Provinsi Bangka Belitung. Padahal, Provinsi Banten termasuk daerah sentra beras nasional menurut Kementrian Pertahanan. Oleh karena itu, penelitian ini bertujuan untuk mengeksplorasi dan memahami pola pergerakan harga pangan dengan memanfaatkan data time-series melalui algoritma Fuzzy C-Means Clustering dan memanfaatkan kesamaan Dynamic Time Warping untuk pengukuran jarak. Jumlah klaster optimal adalah 3 klaster dengan evaluasi validasi yang didapatkan MPC sebesar 0,957755, PEI adalah 0,0321, dan nilai XBI adalah 0,090437. Hasil pengelompokan mampu memberikan gambaran kondisi harga bahan pangan di Provinsi Banten.

<img src="https://raw.githubusercontent.com/ayalya/analisis-sentimen-sbms/main/asset/alur_penelitian(skripsi).jpg" align="center"><a></a>

Gambar 1. Alur Penelitian

## _Modeling_

Proses pemodelan menggunakan algoritma _Fuzzy C-Means Clustering_ menggunakan parameter fuzziness $m=1.5$, iterasi maksimum $l=100$, dan nilai ambang 0,0001, dengan jumlah klaster optimal 3.

## Evaluasi
Evaluasi matriks yang digunakan pada penelitian ini menggunakan evaluasi internal dari Fuzzy C-Means Clustering, yaitu:

1. **Modified Partition Coefficient (MPC)**, merupakan evaluasi matriks lanjutan dan normalisasi dari PC untuk menghilangkan ketergantungan terhadap nilai c sehingga nilainya berada diantara 0-1. Semakin dekat nilainya maka semakin jelas data terkelompokan. Adapun rumusnya, sebagai berikut:

<div align="center">
    <img src="https://latex.codecogs.com/png.image?\dpi{150}&space;MPC={1}- \frac{c}{c-1}(1-PC)" alt="PC">
</div>

2. **Partition Entropy Index (PE)**, merupakan evaluasi matriks untuk mengukur ketidakpastian (entropy) partisi pada model. Semakin mendekati 0 nilainya, maka semakin baik cluster yang dihasilkan. Perhitungannya dilakukan menggunakan rumus:

<div align="center">
    <img src="https://latex.codecogs.com/png.image?\dpi{150}&space;PEI=-\frac{1}{n} \sum_{i=1}^{n} \sum_{j=1}^{c} {u}_{i,k} log(u_{i,j})" alt="PEI">
</div>

3. **Xie Beni Index (XBI)**, digunakan untuk menghitung rasio total variasi antara kekompakan (dalam klaster) dan separasi atau pemisahan (antar klaster). Semakin kecil nilai, semakin baik klaster yang dihasilkan.

<div align="center">
    <img src="https://latex.codecogs.com/png.image?\dpi{150}&space;XBI=\frac{\sum_{i=1}^{n} \sum_{j=1}^{c} {u}_{i,k}^{m} {||{x}_{i}-{v}_{k}||}^{2}}{{N} . {min}_{k\not= i}{||{x}_{i}-{v}_{k}||}^{2}} \" alt="PEI">
</div>

di mana

$m$ = derajat fuzziness (bernilai 1.5)

$u_{i,j}$ : nilai keanggotaan $i$ terhadap cluster $j$

$x_{i}$ : data ke $i$

$v_{j}$ : centroid dari cluster ke $j$

Tabel Nilai Metrik Evaluasi
Jumlah Klaster |    MPC     |   PEI     |   XBI 
----------|----------|----------|----------
2   |   0.991176    |   0.011873    | 0.018001
3   |   0.957755    |   0.066321    |   0.090437
4   |   0.929324    |   0.098201    |   0.05839
5   |   0.957192    |   0.084499    |   0.206767


<img src="https://raw.githubusercontent.com/ayalya/analisis-sentimen-sbms/main/asset/nilaiMetrikEvaluasi.png" align="center"><a></a>

Gambar 2. Diagram Garis Metrik Evaluasi

Jumlah klaster 2 akan dikecualikan karena nilai MPC mendekati 1, berpotensi menimbulkan overfitting serta kurang representatif dalam pengelompokan data. Seperti yang ditujukkan pada gambar di atas, pemilihan jumlah klaster optimal berdasarkan nilai MPC tertinggi dan nilai PEI dan XBI terendah, yaitu pada jumlah klaster 3.

## Hasil

<img src="https://raw.githubusercontent.com/ayalya/analisis-sentimen-sbms/main/asset/diagramGarisAnggotaKlaster.png" align="center"><a></a>

Gambar 3. Diagram Garis Anggota Klaster Pemodelan FCM

Jumlah klaster optimal yang dari pengelompokan FCM dengan DTW yaitu sebanyak 3 klaster, berikut anggota dan karakteristik klaster yang dihasilkan:

-	Klaster 1 memiliki anggota bawang merah, bawang putih, cabai merah, cabai rawit, dan daging ayam. Klaster ini memiliki karakteristik dengan pola fluktuasi tinggi, nilai kombinasi jarak DTW data di dalam klaster cenderung rendah dengan nilai rata-rata 4,9753307, dan mayoritas anggotanya merupakan bahan pangan mudah rusak.
-	Klaster 2 hanya memiliki satu anggota, yaitu daging sapi yang memiliki pola sangat berbeda dengan komoditas lainnya. Jarak DTW dengan data di luar klaster sangat tinggi di atas 33, merupakan komoditas mudah rusak, dan berada di rentang harga tinggi.
-	Klaster 3 memiliki anggota beras, telur ayam, gula pasir, dan minyak goreng. Klaster ini memiliki karakteristik pola fluktuasi yang rendah, jarak DTW antar data di dalam klaster yang rendah dengan rata-rata 2,354463, dan mayoritas anggotanya merupakan bahan tidak mudah rusak hasil pertanian dan industri.

Algoritma FCM dengan kesamaan jarak DTW mampu mengelompokan data time-series berdasarkan pola dan pergerakan data. Performa terbaik didapatkan pada jumlah klaster 3 dengan nilai MPC adalah 0,957755, nilai PEI 0,066321, dan nilai XBI mencapai 0,090437. Angka tersebut dapat memberikan gambaran bahwa kinerja model menegaskan bahwa kualitas klaster yang dihasilkan sangat baik, dengan kejelasan partisi tinggi dan pemisahan klaster yang optimal.


## Bagaimana Cara Menggunakan Kode?
### Menginstall Virtual Environment
```
python -m venv skripsi
````

### Mengaktifkan Virtual Environment
```
skripsi\scripts\activate
```

### Install library
```
pip install -r requirements.txt
```

### Mendaftarken environment sebagai kernel di Jupyter
```
python -m ipykernel install --user --name=skripsi --display-name "Python (skripsi)"
```

### Membuka file jupyter notebook Analisis Harga Bahan Pangan
```
jupyter notebook
```

### Menjalankan model FCM dengan kedekatan jarak DTW
```
python Python\model.py
```

### Menjalankan dashboard streamlit di lokal
```
streamlit run dashboard\dashboard.py
```

### Link dashboard streamlit yang sudah dideploy

<img src="https://raw.githubusercontent.com/ayalya/analisis-sentimen-sbms/main/asset/dashboardFCM.png" align="center"><a></a>

diakses [di sini](https://dashboardhargapanganprovbanten.streamlit.app/)

### Stop kernel jupyter
```
ctrl+c
```

### Menonaktifkan virtual environment
```
deactivate
```
