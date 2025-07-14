import sqlite3

# Bikin atau konek ke database (bikin file salon.db)
conn = sqlite3.connect('salon.db')
c = conn.cursor()

# Bikin tabel reservasi
c.execute('''
CREATE TABLE IF NOT EXISTS reservasi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_pelanggan TEXT,
    nama_layanan TEXT,
    nama_karyawan TEXT,
    tanggal TEXT,
    harga INTEGER,
    total INTEGER,
    status TEXT
)
''')

conn.commit()
conn.close()
print("Database & tabel reservasi berhasil dibuat!")