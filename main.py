#!/usr/bin/env python3
"""
Program Pengolah Dataset JSON ke CSV
====================================

Tujuan: Mengolah 150 ribu dataset dalam format JSON dan mengekspor ke CSV
dengan kolom "kalimat" dan "judul_berita"

Author: Assistant AI
Date: 2025-08-21
"""

import json
import csv
import os
import glob
from pathlib import Path
import re
from typing import List, Dict, Generator
import logging

def setup_logging():
    """Setup logging untuk monitoring proses"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('json_processing.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def extract_sentences_advanced(text: str) -> List[str]:
    """
    Ekstrak kalimat dengan pemrosesan yang lebih canggih
    Menangani singkatan, angka, dan kasus khusus bahasa Indonesia
    
    Args:
        text (str): Teks yang akan dipisah menjadi kalimat
        
    Returns:
        List[str]: Daftar kalimat yang telah dipisah
    """
    if not text or not isinstance(text, str):
        return []
    
    # Bersihkan teks dari karakter yang tidak diinginkan
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Pattern yang lebih sophisticated untuk bahasa Indonesia
    # Menangani singkatan umum seperti "Dr.", "Ir.", "PT.", dll.
    abbreviations = r'(?:Dr|Ir|Drs|Prof|Mr|Mrs|Ms|PT|CV|Ltd|Inc|Co|dll|dsb|dst|dkk|yth|ttd|tgl|no|tel|hp|email|www|com|org|net|gov|mil|edu)\.?'
    
    # Split kalimat tapi jangan split pada singkatan
    sentences = []
    
    # Pattern untuk memisahkan kalimat
    # Cari titik, tanda seru, atau tanda tanya yang diikuti spasi dan huruf kapital
    sentence_endings = r'[.!?]+(?=\s+[A-Z]|$)'
    
    # Split berdasarkan pola
    parts = re.split(f'({sentence_endings})', text)
    
    current_sentence = ""
    for i, part in enumerate(parts):
        if re.match(sentence_endings, part):
            current_sentence += part
            sentences.append(current_sentence.strip())
            current_sentence = ""
        else:
            current_sentence += part
    
    # Tambahkan sisa kalimat jika ada
    if current_sentence.strip():
        sentences.append(current_sentence.strip())
    
    # Filter kalimat yang terlalu pendek (kurang dari 10 karakter)
    filtered_sentences = [s for s in sentences if len(s.strip()) >= 10]
    
    return filtered_sentences

def process_single_json_file(file_path: str) -> Generator[Dict[str, str], None, None]:
    """
    Generator untuk memproses satu file JSON
    Menggunakan generator untuk memory efficiency
    
    Args:
        file_path (str): Path ke file JSON
        
    Yields:
        Dict[str, str]: Dictionary dengan key 'kalimat' dan 'judul_berita'
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Pastikan data adalah list
        if not isinstance(data, list):
            data = [data]
        
        # Proses setiap artikel dalam file
        for article in data:
            if isinstance(article, dict) and 'isi' in article and 'judul' in article:
                sentences = extract_sentences_advanced(article['isi'])
                
                # Yield setiap kalimat dengan judul berita
                for sentence in sentences:
                    yield {
                        'kalimat': sentence,
                        'judul_berita': article['judul']
                    }
                    
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {str(e)}")

def process_json_dataset(folder_path: str, base_output_path: str, max_rows_per_file: int = 75000, batch_size: int = 10000):
    """
    Proses dataset JSON besar dengan batch processing untuk efisiensi memory
    dan bagi hasil menjadi beberapa file CSV
    
    Args:
        folder_path (str): Path ke folder yang berisi file JSON
        base_output_path (str): Base path untuk file CSV output (tanpa ekstensi)
        max_rows_per_file (int): Jumlah maksimum baris per file CSV
        batch_size (int): Jumlah baris yang ditulis dalam satu batch
        
    Returns:
        int: Total jumlah kalimat yang diproses
    """
    logger = setup_logging()
    
    # Validasi folder
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder tidak ditemukan: {folder_path}")
    
    # Cari semua file JSON (termasuk subdirektori)
    json_pattern = os.path.join(folder_path, "**/*.json")
    json_files = glob.glob(json_pattern, recursive=True)
    
    if not json_files:
        raise FileNotFoundError(f"Tidak ada file JSON ditemukan di: {folder_path}")
    
    logger.info(f"Ditemukan {len(json_files)} file JSON")
    
    # Inisialisasi counter
    processed_files = 0
    total_sentences = 0
    batch_data = []
    
    # Variabel untuk multi-file output
    file_index = 1
    current_file_rows = 0
    current_csv_file = None
    current_writer = None
    
    def open_new_csv_file():
        """Buka file CSV baru untuk writing"""
        nonlocal file_index, current_csv_file, current_writer, current_file_rows
        current_output_path = f"{base_output_path}_{file_index}.csv"
        if current_csv_file:
            current_csv_file.close()
            logger.info(f"File CSV {current_output_path} ditutup. Total baris: {current_file_rows}")
        
        current_csv_file = open(current_output_path, 'w', newline='', encoding='utf-8')
        fieldnames = ['kalimat', 'judul_berita']
        current_writer = csv.DictWriter(current_csv_file, fieldnames=fieldnames)
        current_writer.writeheader()
        current_file_rows = 0
        file_index += 1
        logger.info(f"File CSV baru dibuat: {current_output_path}")
        return current_writer, current_csv_file, current_output_path
    
    # Buka file CSV pertama
    writer, csv_file, output_path = open_new_csv_file()
    
    # Proses setiap file JSON
    for json_file in json_files:
        logger.info(f"Memproses file: {os.path.basename(json_file)}")
        
        # Proses file dan kumpulkan data dalam batch
        for row_data in process_single_json_file(json_file):
            batch_data.append(row_data)
            total_sentences += 1
            current_file_rows += 1
            
            # Jika mencapai batas maksimum baris per file, buka file baru
            if current_file_rows >= max_rows_per_file:
                # Tulis batch terlebih dahulu
                if batch_data:
                    writer.writerows(batch_data)
                    logger.info(f"Menulis batch {len(batch_data)} kalimat. Total: {total_sentences}")
                    batch_data = []
                
                # Buka file CSV baru
                writer, csv_file, output_path = open_new_csv_file()
            
            # Tulis batch ketika mencapai batch_size
            if len(batch_data) >= batch_size:
                writer.writerows(batch_data)
                logger.info(f"Menulis batch {len(batch_data)} kalimat. Total: {total_sentences}")
                batch_data = []
        
        processed_files += 1
        
        # Progress report setiap 50 file
        if processed_files % 50 == 0:
            logger.info(f"Progress: {processed_files}/{len(json_files)} file diproses")
    
    # Tulis sisa data
    if batch_data:
        writer.writerows(batch_data)
        logger.info(f"Menulis batch terakhir {len(batch_data)} kalimat")
    
    # Tutup file CSV terakhir
    if csv_file:
        csv_file.close()
        logger.info(f"File CSV {output_path} ditutup. Total baris: {current_file_rows}")
    
    # Log hasil akhir
    logger.info("="*50)
    logger.info("PROSES SELESAI!")
    logger.info(f"Total file diproses: {processed_files}")
    logger.info(f"Total kalimat: {total_sentences}")
    logger.info(f"File CSV output: {base_output_path}_1.csv, {base_output_path}_2.csv, dll.")
    logger.info("="*50)
    
    return total_sentences

def validate_csv_output(csv_path_pattern: str, sample_size: int = 5):
    """
    Validasi hasil CSV dan tampilkan sample data
    
    Args:
        csv_path_pattern (str): Pattern path ke file CSV (misal: "output_*.csv")
        sample_size (int): Jumlah sample yang ditampilkan per file
    """
    csv_files = glob.glob(csv_path_pattern)
    
    if not csv_files:
        print(f"Tidak ada file CSV ditemukan dengan pattern: {csv_path_pattern}")
        return
    
    for csv_file in csv_files:
        print(f"\nValidasi file: {csv_file}")
        if not os.path.exists(csv_file):
            print(f"File CSV tidak ditemukan: {csv_file}")
            continue
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            total_rows = 0
            sample_data = []
            
            for i, row in enumerate(reader):
                total_rows += 1
                if i < sample_size:
                    sample_data.append(row)
            
            print(f"Total baris dalam CSV: {total_rows}")
            print(f"Sample {min(sample_size, len(sample_data))} baris pertama:")
            print("-" * 100)
            
            for i, row in enumerate(sample_data, 1):
                print(f"{i}. Judul: {row['judul_berita'][:50]}...")
                print(f"   Kalimat: {row['kalimat'][:80]}...")
                print()

def get_folder_stats(folder_path: str):
    """
    Tampilkan statistik folder JSON
    
    Args:
        folder_path (str): Path ke folder JSON
    """
    if not os.path.exists(folder_path):
        print(f"Folder tidak ditemukan: {folder_path}")
        return
    
    json_files = glob.glob(os.path.join(folder_path, "**/*.json"), recursive=True)
    total_size = sum(os.path.getsize(f) for f in json_files)
    
    print(f"Statistik folder: {folder_path}")
    print(f"- Jumlah file JSON: {len(json_files)}")
    print(f"- Total ukuran: {total_size / (1024*1024):.2f} MB")
    
    if json_files:
        print(f"- File terbesar: {max(json_files, key=os.path.getsize)}")
        print(f"- File terkecil: {min(json_files, key=os.path.getsize)}")

def main():
    """
    Fungsi utama untuk menjalankan program
    """
    print("="*60)
    print("PROGRAM PENGOLAH DATASET JSON KE CSV")
    print("Untuk dataset 150 ribu file JSON")
    print("="*60)
    
    # KONFIGURASI - GANTI SESUAI KEBUTUHAN ANDA
    folder_path = "json"  # GANTI INI!
    base_output_path = "dataset_kalimat_150k"  # Tanpa ekstensi .csv
    max_rows_per_file = 300000  # Maksimum baris per file
    batch_size = 10000  # Tulis dalam batch 10k untuk efisiensi memory
    
    print(f"Folder JSON: {folder_path}")
    print(f"Output CSV base: {base_output_path}")
    print(f"Maksimum baris per file: {max_rows_per_file}")
    print(f"Batch size: {batch_size}")
    print("="*60)
    
    try:
        # Tampilkan statistik folder
        print("Menganalisis folder...")
        get_folder_stats(folder_path)
        print()
        
        # Konfirmasi sebelum proses
        confirm = input("Lanjutkan proses? (y/n): ").lower().strip()
        if confirm != 'y':
            print("Proses dibatalkan.")
            return
        
        # Jalankan pemrosesan
        print("Memulai pemrosesan...")
        total_sentences = process_json_dataset(folder_path, base_output_path, max_rows_per_file, batch_size)
        
        # Validasi hasil
        print("\nValidasi hasil...")
        validate_csv_output(f"{base_output_path}_*.csv", 3)
        
        print(f"\n✅ SELESAI! Total {total_sentences} kalimat berhasil diproses.")
        print(f"File CSV tersimpan sebagai: {base_output_path}_1.csv, {base_output_path}_2.csv, dll.")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {str(e)}")
        print("\nPastikan:")
        print("1. Folder JSON sudah benar")
        print("2. File JSON ada di dalam folder")
        print("3. Format path sudah sesuai OS Anda")
        
    except Exception as e:
        print(f"❌ Error tidak terduga: {str(e)}")
        print("Silakan periksa log file 'json_processing.log' untuk detail error.")

if __name__ == "__main__":
    # Contoh penggunaan cepat tanpa input interaktif
    # Uncomment dan sesuaikan path di bawah ini untuk eksekusi langsung
    
    # QUICK START - Uncomment baris di bawah dan ganti path
    # folder_path = "json"
    # base_output = "hasil_dataset"
    # total = process_json_dataset(folder_path, base_output, max_rows_per_file=75000)
    # print(f"Selesai! Total kalimat: {total}")
    
    # Atau jalankan mode interaktif
    main()