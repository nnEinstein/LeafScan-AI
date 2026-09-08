# Deteksi Penyakit Tanaman dari Foto Daun

Klasifikasi citra menggunakan Transfer Learning (MobileNetV2) untuk
mendeteksi 15 kelas kondisi tanaman (penyakit/sehat) dari foto daun,
mencakup tomat, kentang, dan paprika.

## Latar Belakang
Petani sering kesulitan mendeteksi penyakit tanaman secara dini
karena keterbatasan akses ke ahli pertanian. Project ini membangun
model klasifikasi citra sebagai alat bantu deteksi dini yang bisa
diakses lebih luas.

## Dataset
- Sumber: [PlantVillage Dataset - Kaggle](https://www.kaggle.com/datasets/emmarex/plantdisease)
- 20.639 gambar, 15 kelas (10 tomat, 3 kentang, 2 paprika)
- Ketimpangan kelas signifikan (~21:1) antara kelas terbanyak dan
  tersedikit

## Metodologi
1. Audit dataset (jumlah gambar per kelas, verifikasi ukuran gambar)
2. Split data stratified 70/15/15 (train/val/test) per kelas
3. Image augmentation (flip, rotasi, zoom) pada data training
4. Baseline: CNN dari nol (3 lapis konvolusi)
5. Transfer Learning: MobileNetV2 (pretrained ImageNet, base
   dibekukan) + custom classification head
6. Eksperimen pembanding: transfer learning + class weighting

## Hasil

| Model | Akurasi | Macro F1 |
|---|---|---|
| CNN dari nol (baseline) | 81% | 0.77 |
| **Transfer Learning (final)** | **87%** | **0.85** |
| Transfer Learning + Class Weighting | 86% | 0.84 |

## Temuan Kunci
- Ketimpangan kelas (21:1) adalah akar penyebab performa lemah
  baseline pada kelas minoritas (Potato_healthy, Potato_Late_blight)
- Transfer learning terbukti jauh lebih stabil dan akurat dibanding
  CNN dari nol, khususnya untuk kelas berdata sangat terbatas
- Class weighting BUKAN perbaikan universal — memperbaiki sebagian
  kelas namun mengorbankan kelas lain (trade-off nyata, bukan
  perbaikan bersih), dibuktikan lewat eksperimen pembanding langsung
- [Tambahkan insight lain yang menurutmu menarik untuk diceritakan]

## Keterbatasan & Pengembangan Selanjutnya
- Model belum diuji pada foto dengan kondisi pengambilan gambar di
  luar dataset (background bervariasi, pencahayaan berbeda)
- Tomato_Early_blight (recall 0.53) dan Tomato_mosaic_virus (recall
  0.50) tetap menjadi titik lemah pada model final
- Fine-tuning base_model (bukan hanya membekukan) berpotensi
  meningkatkan performa lebih lanjut dengan data yang lebih banyak
- Cakupan dataset terbatas pada 3 jenis tanaman
