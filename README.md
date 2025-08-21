Sip, biar makin lengkap saya update README-nya dengan sumber dataset dari Mendeley 👍

```markdown
# Program Pengolah Dataset JSON ke CSV

## 📌 Deskripsi
Program ini digunakan untuk mengolah dataset berita dalam format **JSON** menjadi file **CSV**.  
Setiap artikel akan dipecah menjadi **kalimat-kalimat**, lalu diekspor ke CSV dengan dua kolom utama:

- `kalimat`
- `judul_berita`

Program ini dirancang agar **efisien dalam penggunaan memori**, mampu menangani dataset besar (hingga ratusan ribu file JSON).

---

## 📂 Dataset
Dataset yang digunakan berasal dari Mendeley Data:  
👉 [Indonesian News Article Dataset](https://data.mendeley.com/datasets/2zpbjs22k3/1)

Dataset ini berisi artikel berita dalam bahasa Indonesia dalam format JSON.  
Sebelum menjalankan program, pastikan dataset sudah diunduh dan diekstrak ke folder `json/`.

---

## ⚙️ Fitur Utama
- Ekstraksi kalimat dengan pemrosesan lanjutan (menangani singkatan, angka, dsb).
- **Batch processing** untuk efisiensi memory.
- Hasil CSV otomatis **di-split** jika melebihi jumlah baris tertentu.
- Logging proses ke `json_processing.log`.
- Validasi hasil CSV dengan menampilkan sampel data.
- Statistik dataset JSON sebelum diproses.

---

## 📂 Struktur Output
Jika dataset besar, program akan otomatis membagi hasil menjadi beberapa file:

```

dataset\_kalimat\_150k\_1.csv
dataset\_kalimat\_150k\_2.csv
dataset\_kalimat\_150k\_3.csv
...

````

---

## 🚀 Cara Penggunaan

### 1. Clone / Salin Project
```bash
git clone <repo-anda>
cd DatasetProcessing
````

### 2. Download Dataset

Unduh dataset dari Mendeley dan ekstrak ke folder `json/`:

```
json/
 ├── export-json-2015-07-01.json
 ├── export-json-2015-07-02.json
 ├── ...
```

### 3. Jalankan Program

```bash
python main.py
```

Program akan menampilkan informasi dataset, lalu menanyakan konfirmasi:

```
Lanjutkan proses? (y/n):
```

Ketik `y` untuk melanjutkan.

---

## ⚡ Konfigurasi

Atur konfigurasi di fungsi `main()` pada `main.py`:

```python
folder_path = "json"                 # Folder berisi file JSON
base_output_path = "dataset_output"  # Nama dasar file output CSV
max_rows_per_file = 300000           # Maksimum baris per file CSV
batch_size = 10000                   # Jumlah baris ditulis per batch
```

### Contoh:

* Jika `max_rows_per_file = 300000` → satu file CSV bisa menampung **300 ribu kalimat**.
* Jika total kalimat lebih dari 300 ribu, maka hasil akan di-split ke beberapa file.

---

## 📊 Validasi Output

Setelah proses selesai, program akan menampilkan sampel isi CSV:

```
Validasi file: dataset_output_1.csv
Total baris dalam CSV: 150000
Sample 3 baris pertama:
--------------------------------------------------------
1. Judul: Pemerintah umumkan kebijakan baru...
   Kalimat: Pemerintah hari ini mengumumkan kebijakan baru dalam sektor ekonomi...

2. Judul: Harga minyak dunia naik...
   Kalimat: Harga minyak mentah dunia mengalami kenaikan signifikan pada minggu ini...

3. Judul: Teknologi AI semakin berkembang...
   Kalimat: Perkembangan teknologi kecerdasan buatan semakin pesat di berbagai sektor...
```

---

## 📝 Log

Selama pemrosesan, semua informasi akan dicatat ke file:

```
json_processing.log
```

---

## 🔧 Requirement

* Python 3.7+
* Tidak ada dependency eksternal tambahan, hanya modul bawaan Python:

  * `json`
  * `csv`
  * `glob`
  * `logging`
  * `re`

---

## 👨‍💻 Author

Dibuat dengan ❤️ oleh **AI & Gratia**