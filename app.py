
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///salon.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ----------------------------
# MODELS
# ----------------------------
class Pelanggan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    telepon = db.Column(db.String(20))
    foto = db.Column(db.String(200))

class Layanan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    harga = db.Column(db.Integer)
    foto = db.Column(db.String(200))

class Karyawan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    telepon = db.Column(db.String(20))
    jabatan = db.Column(db.String(100))
    foto = db.Column(db.String(200))

class Reservasi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pelanggan_id = db.Column(db.Integer, db.ForeignKey('pelanggan.id'))
    layanan_id = db.Column(db.Integer, db.ForeignKey('layanan.id'))
    karyawan_id = db.Column(db.Integer, db.ForeignKey('karyawan.id'))
    tanggal = db.Column(db.String(20))
    total_harga = db.Column(db.Integer)

# ----------------------------
# ROUTES
# ----------------------------

@app.route('/')
def index():
    return render_template('index.html')


# ----------------------------
# LAYANAN
# ----------------------------
@app.route('/layanan', methods=['GET', 'POST'])
def layanan():
    if request.method == 'POST':
        nama = request.form['nama']
        harga = request.form['harga']
        foto = request.files['foto']

        filename = ''
        if foto and foto.filename:
            filename = secure_filename(foto.filename)
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        layanan = Layanan(nama=nama, harga=harga, foto=filename)
        db.session.add(layanan)
        db.session.commit()
        return redirect(url_for('layanan'))

    layanan_list = Layanan.query.all()
    return render_template('layanan.html', layanan=layanan_list)


# ----------------------------
# PELANGGAN
# ----------------------------

@app.route('/pelanggan', methods=['GET', 'POST'])
def pelanggan():
    if request.method == 'POST':
        nama = request.form['nama']
        telepon = request.form['telepon']
        foto = request.files['foto']

        filename = None
        if foto and foto.filename != '':
            filename = secure_filename(foto.filename)
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_pelanggan = Pelanggan(
            nama=nama,
            telepon=telepon,
            foto=filename
        )
        db.session.add(new_pelanggan)
        db.session.commit()

        return redirect(url_for('pelanggan'))

    data_pelanggan = Pelanggan.query.all()
    return render_template('pelanggan.html', data_pelanggan=data_pelanggan)

@app.route('/hapus_pelanggan/<int:id>')
def hapus_pelanggan(id):
    pelanggan = Pelanggan.query.get_or_404(id)

    if pelanggan.foto:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], pelanggan.foto))
        except:
            pass

    db.session.delete(pelanggan)
    db.session.commit()
    return redirect(url_for('pelanggan'))
    
# ----------------------------
# KARYAWAN
# ----------------------------

@app.route('/karyawan', methods=['GET', 'POST'])
def karyawan():
    if request.method == 'POST':
        nama = request.form['nama']
        telepon = request.form['telepon']
        jabatan = request.form['jabatan']
        foto = request.files['foto']

        filename = None
        if foto and foto.filename != '':
            filename = secure_filename(foto.filename)
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_karyawan = Karyawan(
            nama=nama,
            telepon=telepon,
            jabatan=jabatan,
            foto=filename
        )
        db.session.add(new_karyawan)
        db.session.commit()

        return redirect(url_for('karyawan'))

    data_karyawan = Karyawan.query.all()
    return render_template('karyawan.html', data_karyawan=data_karyawan)

@app.route('/hapus_karyawan/<int:id>')
def hapus_karyawan(id):
    karyawan = Karyawan.query.get_or_404(id)
    
    # Hapus file foto dari folder kalau ada
    if karyawan.foto:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], karyawan.foto))
        except:
            pass

    db.session.delete(karyawan)
    db.session.commit()
    return redirect(url_for('karyawan'))


# ----------------------------
# RESERVASI
# ----------------------------
@app.route('/reservasi', methods=['GET', 'POST'])
def reservasi():
    pelanggan_list = Pelanggan.query.all()
    layanan_list = Layanan.query.all()
    karyawan_list = Karyawan.query.all()

    if request.method == 'POST':
        pelanggan_id = request.form['pelanggan']
        layanan_id = request.form['layanan']
        karyawan_id = request.form['karyawan']
        tanggal = request.form['tanggal']

        layanan = Layanan.query.get(layanan_id)
        total_harga = layanan.harga if layanan else 0

        reservasi_baru = Reservasi(
            pelanggan_id=pelanggan_id,
            layanan_id=layanan_id,
            karyawan_id=karyawan_id,
            tanggal=tanggal,
            total_harga=total_harga
        )
        db.session.add(reservasi_baru)
        db.session.commit()

        return redirect(url_for('reservasi'))

    # Ambil semua data reservasi dan relasi
    reservasi_list = db.session.query(Reservasi, Pelanggan, Layanan, Karyawan)\
        .join(Pelanggan, Reservasi.pelanggan_id == Pelanggan.id)\
        .join(Layanan, Reservasi.layanan_id == Layanan.id)\
        .join(Karyawan, Reservasi.karyawan_id == Karyawan.id).all()

    return render_template('reservasi.html',
                           pelanggan_list=pelanggan_list,
                           layanan_list=layanan_list,
                           karyawan_list=karyawan_list,
                           reservasi_list=reservasi_list)

        
@app.route('/reservasi/hapus/<int:id>')
def hapus_reservasi(id):
    reservasi = Reservasi.query.get(id)
    if reservasi:
        db.session.delete(reservasi)
        db.session.commit()
    return redirect(url_for('reservasi'))


# ----------------------------
# JALANKAN APP
# ----------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)