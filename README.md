# MCF-ITB-insurance-forecasting-TeamAFTers

Project is contributed by:
- Alvin Wijaya
- Tokesi Lukynawa
- Felicio Balamitta Putra

Full findings documentation is [documented here](https://drive.google.com/file/d/1-7a0JepA1TmkJLKAD3YcUg8rdDoq0VRr/view?usp=sharing)

## 1. Overview

Proyek ini mengembangkan pipeline analisis dan pemodelan untuk memprediksi karakteristik klaim asuransi kesehatan berdasarkan kombinasi data klaim dan data polis. Dataset yang digunakan terdiri dari dua file utama:

- `Data_Klaim.csv`
- `Data_Polis.csv`

Data klaim dan polis digabungkan berdasarkan kolom `Nomor Polis` untuk membangun fitur yang relevan seperti usia nasabah, masa aktif polis, lama perawatan, jenis layanan, diagnosis, lokasi rumah sakit, dan domisili nasabah.

---

## 2. Dataset Information

### 2.1 Data Klaim (`Data_Klaim.csv`)

- Jumlah record: 4.627 baris
- Jumlah kolom: 13
- Kolom utama:
  - `Claim ID`
  - `Nomor Polis`
  - `Reimburse/Cashless`
  - `Inpatient/Outpatient`
  - `ICD Diagnosis`
  - `ICD Description`
  - `Status Klaim`
  - `Tanggal Pembayaran Klaim`
  - `Tanggal Pasien Masuk RS`
  - `Tanggal Pasien Keluar RS`
  - `Nominal Klaim Yang Disetujui`
  - `Nominal Biaya RS Yang Terjadi`
  - `Lokasi RS`

### 2.2 Data Polis (`Data_Polis.csv`)

- Jumlah record: 4.096 baris
- Jumlah kolom: 6
- Kolom utama:
  - `Nomor Polis`
  - `Plan Code`
  - `Gender`
  - `Tanggal Lahir`
  - `Tanggal Efektif Polis`
  - `Domisili`

### 2.3 Tujuan Analisis

Tujuan utama dari proyek ini adalah untuk memahami pola klaim kesehatan dan membangun model prediksi yang dapat memperkirakan:

1. tingkat severitas klaim (`claim_severity`),
2. frekuensi klaim bulanan (`claim_frequency`),
3. total klaim bulanan (`total_claim`).

Analisis dilakukan dengan pendekatan time-series dan machine learning untuk menangani pola musiman, tren, serta variabilitas data klaim yang cenderung skewed.

---

## 3. Data Quality & Preprocessing

Beberapa masalah utama yang ditemukan pada data sebelum pemodelan adalah:

- Nilai tanggal disimpan dalam format yang tidak konsisten, terutama pada `Tanggal Lahir` dan `Tanggal Efektif Polis`.
- Distribusi nominal klaim dan biaya rumah sakit sangat miring ke kanan (heavy-tailed).
- Terdapat missing value pada beberapa kolom kategorikal.
- Tanggal pembayaran klaim tidak dipakai sebagai fitur karena bersifat leakage: informasi ini tidak tersedia saat prediksi dilakukan di masa depan.

Untuk mengatasi hal tersebut, notebook melakukan beberapa langkah berikut:

- konversi tanggal ke format datetime,
- pembuatan feature baru seperti:
  - `Usia Saat Klaim`
  - `Tenure Polis Hari`
  - `Lama Perawatan`
  - `Bulan Masuk`
  - `Is Weekend`
  - `Kuartal Masuk`
  - `Is Jabodetabek`
- imputasi missing value pada variabel kategorikal,
- normalisasi numerik menggunakan `RobustScaler`,
- log-transform pada target untuk menstabilkan distribusi skewed,
- pembuatan fitur time-series seperti lag, rolling mean, rolling median, rolling std, dan seasonal pattern.

---

## 4. Key Findings

### 4.1 Hubungan antara biaya rumah sakit dan klaim yang disetujui

Dari exploratory data analysis, terdapat hubungan linear yang cukup kuat antara `Nominal Biaya RS Yang Terjadi` dan `Nominal Klaim Yang Disetujui`. Namun, ditemukan beberapa outlier signifikan di mana biaya rumah sakit sangat tinggi, tetapi klaim yang disetujui tetap berada di bawah nilai yang diharapkan.

Interpretasi bisnis:

- terdapat kemungkinan adanya mekanisme kendali biaya atau plafon manfaat,
- beberapa kasus kritis membesar biaya rumah sakit, tetapi tidak sepenuhnya dibayar oleh perusahaan asuransi.

### 4.2 Distribusi klaim sangat tidak seimbang

Nilai klaim cenderung mengikuti pola right-skewed, sehingga model yang sensitif terhadap distribusi data dapat menghasilkan prediksi yang kurang stabil. Karena itu, notebook memprioritaskan model tree-based dan transformasi target yang lebih robust.

### 4.3 Variabel klinis dan demografis berpengaruh penting

Fitur seperti:

- `Inpatient/Outpatient`
- `ICD Description`
- `Lokasi RS`
- `Domisili`
- `Usia Saat Klaim`
- `Lama Perawatan`

menunjukkan potensi pengaruh terhadap besar klaim. Hal ini menandakan bahwa faktor klinis dan perawatan pasien berperan penting dalam membentuk severity klaim.

### 4.4 Time-series features memiliki nilai prediktif

Fitur lag dan rolling statistics seperti `lag_1`, `lag_3`, `rolling_mean_2`, `rolling_mean_3`, serta variabel musiman (`month_sin`, `month_cos`) terbukti membantu dalam menangkap tren dan pola siklus bulanan dari data klaim.

---

## 5. Modelling Approach

Notebook membandingkan beberapa model machine learning untuk memprediksi claim severity, frequency, dan total claim. Model yang dipertimbangkan antara lain:

- Random Forest Regressor (RFR)
- XGBoost Regressor
- GLM (Generalized Linear Model)
- LightGBM Regressor
- CatBoost Regressor

### 5.1 Evaluasi model

Metode evaluasi yang dipakai adalah:

- time series split untuk menjaga integritas urutan waktu,
- MAPE (Mean Absolute Percentage Error) sebagai metrik utama,
- RMSE, MAE, dan R2 juga dipakai sebagai pendukung evaluasi.

### 5.2 Strategi yang digunakan

- Train/test split berdasarkan timeline agar tidak terjadi data leakage.
- Robust scaling untuk fitur numerik.
- Transformasi target (log1p/expm1) untuk menanggulangi skewness.
- Hyperparameter tuning dengan GridSearchCV.
- Feature engineering berbasis time-series agar model menangkap tren dan musim.

---

## 6. Results & Model Comparison

Dari hasil notebook, model berbasis gradient boosting (XGBoost, LightGBM, CatBoost) menunjukkan performa yang paling kompetitif untuk prediksi severity dan frequency dibandingkan model lain. Random Forest juga cukup baik, tetapi cenderung kurang optimal dibandingkan model boosting yang lebih adaptif terhadap pola temporal dan non-linear.

GLM digunakan sebagai baseline interpretatif, tetapi hasilnya cenderung lebih rapuh pada data dengan skewness tinggi dan varian yang besar. Pada kondisi data asuransi kesehatan yang sangat fluktuatif, tree-based ensemble model lebih stabil dan lebih cocok untuk menangkap pola kompleks.

Secara umum, model terbaik untuk prediksi severitas dan frekuensi adalah model yang menggunakan fitur time-series dan tuning parameter. Prediksi total klaim dilakukan dengan mengombinasikan severitas dan frekuensi, meskipun secara bawaan error dapat bertumpuk karena komposisi dua prediksi yang independent.

---

## 7. Limitations

Beberapa keterbatasan yang perlu disadari dari proyek ini:

1. Dataset relatif kecil untuk analisis time-series, sehingga validasi model dapat sensitif terhadap fluktuasi bulanan.
2. Ada kemungkinan data leakage yang tidak sepenuhnya terhindarkan jika feature temporal atau pembayaran klaim diintegrasikan tanpa kehati-hatian.
3. Distribusi klaim yang sangat skewed membuat metrik MAPE mudah terdampak oleh beberapa kasus ekstrem.
4. Data yang tersedia tidak mencakup banyak variabel bisnis tambahan seperti riwayat penyakit kronis, premi, atau kebijakan underwriting, yang bisa meningkatkan akurasi prediksi.
5. Prediksi total klaim yang dihitung dari perkalian severitas dan frekuensi dapat menimbulkan compounded error, sehingga hasilnya mungkin kurang presisi dibandingkan model total direktori.

---

## 8. Conclusion

Project ini berhasil menunjukkan bahwa analisis klaim asuransi kesehatan dapat dilakukan dengan pendekatan yang sistematis: mulai dari preprocessing, feature engineering, EDA, hingga pemodelan time-series dan machine learning.

Kesimpulan utama:

- data klaim asuransi kesehatan memiliki karakteristik skewed, non-linear, dan musiman,
- pemodelan yang baik harus memperhatikan waktu, tren, serta biaya yang ekstrem,
- model berbasis boosting seperti XGBoost, LightGBM, dan CatBoost merupakan pendekatan yang paling cocok untuk masalah ini,
- interpretasi bisnis tetap penting karena klaim perjalanan kesehatan sangat dipengaruhi oleh faktor klinis, lokasi, dan kebijakan manfaat.

Secara strategis, hasil analisis ini bisa menjadi dasar untuk pengambilan keputusan seperti:

- estimasi reserve claim,
- pengendalian biaya asuransi,
- identifikasi kasus high-cost claims,
- penyusunan strategi underwriting dan fraud monitoring.

---

## 9. Final Note

Notebook ini bukan sekadar implementasi model, tetapi juga menunjukkan proses eksplorasi data yang penting dalam industri asuransi: mengidentifikasi data quality issues, membangun fitur yang relevan, serta memilih model yang sesuai dengan karakteristik target yang bersifat time-dependent dan heavy-tailed.

Dengan demikian, proyek ini memberikan fondasi yang kuat untuk pengembangan analisis klaim kesehatan yang lebih lanjut, baik untuk kebutuhan forecasting, risk assessment, maupun operational decision support.

