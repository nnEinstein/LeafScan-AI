"""
app_demo.py — VERSI KHUSUS UNTUK MENGECEK UI SAJA.

Tidak butuh TensorFlow, model .h5, atau nama_kelas.pkl sama sekali —
cocok dipakai di laptop yang CPU-nya tidak mendukung AVX (yang bikin
`import tensorflow` biasanya crash duluan). Hasil prediksi di sini
di-random / bisa dipaksa lewat query string, HANYA untuk melihat
tampilan tiap state. Jangan dipakai untuk deploy asli — pakai app.py.

Cara pakai:
  python app_demo.py
  buka http://127.0.0.1:5000

Trik: tambahkan ?demo=kosong / ?demo=gagal / ?demo=sehat / ?demo=penyakit
di address bar untuk langsung memaksa state tertentu tanpa upload apa pun,
misalnya http://127.0.0.1:5000/?demo=penyakit
"""

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import random
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB, sesuai teks di UI

EKSTENSI_DIIZINKAN = {'jpg', 'jpeg', 'png'}
AMBANG_KEYAKINAN = 60.0  # di bawah ini dianggap "Belum Dapat Dideteksi"

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ---------------------------------------------------------------------------
# Metadata tiap kelas hasil prediksi (dataset PlantVillage subset: Tomat,
# Kentang, Paprika). Dipakai untuk mengisi kartu Hasil Prediksi di UI.
# ---------------------------------------------------------------------------
INFO_KELAS = {
    'Pepper__bell___Bacterial_spot': {
        'tanaman': 'Paprika', 'penyakit': 'Bercak Bakteri (Bacterial Spot)',
        'sehat': False, 'keparahan': 'Sedang',
        'deskripsi': 'Disebabkan oleh bakteri Xanthomonas campestris yang menyerang daun dan buah, ditandai bercak kecil kehitaman dengan tepi kekuningan.',
        'saran': ['Buang dan musnahkan bagian tanaman yang terinfeksi', 'Semprotkan bakterisida berbahan tembaga',
                   'Hindari penyiraman dari atas daun', 'Jaga jarak tanam agar sirkulasi udara baik'],
        'gambar': 'Pepper__bell___Bacterial_spot.JPG'
    },
    'Pepper__bell___healthy': {
        'tanaman': 'Paprika', 'penyakit': 'Tanaman Sehat',
        'sehat': True, 'keparahan': None,
        'deskripsi': 'Daun paprika tidak menunjukkan tanda-tanda penyakit. Warna dan tekstur daun terlihat normal.',
        'saran': ['Lanjutkan penyiraman secara teratur', 'Pastikan tanaman tetap mendapat sinar matahari cukup',
                   'Lakukan pemupukan berkala', 'Periksa daun secara rutin untuk deteksi dini'],
        'gambar': 'Pepper__bell___healthy.JPG'
    },
    'Potato___Early_blight': {
        'tanaman': 'Kentang', 'penyakit': 'Bercak Awal (Early Blight)',
        'sehat': False, 'keparahan': 'Sedang',
        'deskripsi': 'Disebabkan oleh jamur Alternaria solani, muncul sebagai bercak cokelat bercincin konsentris pada daun tua terlebih dahulu.',
        'saran': ['Buang daun yang terinfeksi berat', 'Gunakan fungisida yang sesuai',
                   'Terapkan rotasi tanaman', 'Hindari kelembapan berlebih di sekitar tanaman'],
        'gambar': 'Potato___Early_blight.JPG'
    },
    'Potato___Late_blight': {
        'tanaman': 'Kentang', 'penyakit': 'Busuk Daun (Late Blight)',
        'sehat': False, 'keparahan': 'Tinggi',
        'deskripsi': 'Disebabkan oleh Phytophthora infestans, ditandai bercak basah kehitaman yang menyebar cepat dan bisa merusak seluruh tanaman.',
        'saran': ['Segera buang dan musnahkan bagian yang terinfeksi', 'Semprotkan fungisida segera setelah gejala terlihat',
                   'Perbaiki drainase dan sirkulasi udara', 'Hindari penyiraman pada sore/malam hari'],
        'gambar': 'Potato___Late_blight.JPG'
    },
    'Potato___healthy': {
        'tanaman': 'Kentang', 'penyakit': 'Tanaman Sehat',
        'sehat': True, 'keparahan': None,
        'deskripsi': 'Daun kentang tidak menunjukkan tanda-tanda penyakit. Warna dan tekstur daun terlihat normal.',
        'saran': ['Lanjutkan penyiraman secara teratur', 'Jaga kelembapan tanah tetap stabil',
                   'Lakukan pemupukan berkala', 'Periksa daun secara rutin untuk deteksi dini'],
        'gambar': 'Potato___healthy.JPG'
    },
    'Tomato_Bacterial_spot': {
        'tanaman': 'Tomat', 'penyakit': 'Bercak Bakteri (Bacterial Spot)',
        'sehat': False, 'keparahan': 'Sedang',
        'deskripsi': 'Disebabkan oleh bakteri Xanthomonas, muncul sebagai bercak kecil gelap dan berair pada daun dan buah.',
        'saran': ['Buang bagian tanaman yang terinfeksi', 'Semprotkan bakterisida berbahan tembaga',
                   'Hindari bekerja di kebun saat daun basah', 'Gunakan benih/bibit bersertifikat sehat'],
        'gambar': 'Tomato_Bacterial_spot.JPG'
    },
    'Tomato_Early_blight': {
        'tanaman': 'Tomat', 'penyakit': 'Bercak Awal (Early Blight)',
        'sehat': False, 'keparahan': 'Sedang',
        'deskripsi': 'Disebabkan oleh jamur Alternaria solani, bercak cokelat bercincin konsentris muncul lebih dulu pada daun bagian bawah.',
        'saran': ['Buang daun tua yang terinfeksi', 'Gunakan fungisida yang sesuai',
                   'Jaga sirkulasi udara di sekitar tanaman', 'Lakukan rotasi tanaman secara berkala'],
        'gambar': 'Tomato_Early_blight.JPG'
    },
    'Tomato_Late_blight': {
        'tanaman': 'Tomat', 'penyakit': 'Busuk Daun (Late Blight)',
        'sehat': False, 'keparahan': 'Tinggi',
        'deskripsi': 'Disebabkan oleh Phytophthora infestans, bercak basah kehitaman menyebar cepat dan dapat mematikan tanaman dalam beberapa hari.',
        'saran': ['Segera buang dan musnahkan bagian yang terinfeksi', 'Semprotkan fungisida secepatnya',
                   'Perbaiki drainase dan jarak tanam', 'Hindari penyiraman dari atas daun'],
        'gambar': 'Tomato_Late_blight.JPG'
    },
    'Tomato_Leaf_Mold': {
        'tanaman': 'Tomat', 'penyakit': 'Jamur Daun (Leaf Mold)',
        'sehat': False, 'keparahan': 'Sedang',
        'deskripsi': 'Disebabkan oleh jamur Passalora fulva, ditandai bercak kuning di permukaan atas daun dan lapisan jamur di bagian bawah.',
        'saran': ['Kurangi kelembapan di area tanam', 'Tingkatkan sirkulasi udara/ventilasi',
                   'Gunakan fungisida bila diperlukan', 'Hindari penyiraman langsung ke daun'],
        'gambar': 'Tomato_Leaf_Mold.JPG'
    },
    'Tomato_Septoria_leaf_spot': {
        'tanaman': 'Tomat', 'penyakit': 'Bercak Daun (Cercospora/Septoria)',
        'sehat': False, 'keparahan': 'Sedang',
        'deskripsi': 'Disebabkan oleh jamur Septoria yang menyerang daun tanaman, gejalanya berupa bercak cokelat keabu-abuan dengan tepi yang jelas.',
        'saran': ['Buang daun yang terinfeksi berat', 'Gunakan fungisida yang sesuai',
                   'Jaga sirkulasi udara dan kelembapan', 'Lakukan rotasi tanaman secara berkala'],
        'gambar': 'Tomato_Septoria_leaf_spot.JPG'
    },
    'Tomato_Spider_mites_Two_spotted_spider_mite': {
        'tanaman': 'Tomat', 'penyakit': 'Tungau Laba-laba (Spider Mites)',
        'sehat': False, 'keparahan': 'Sedang',
        'deskripsi': 'Serangan hama tungau kecil yang membuat daun berbintik kuning dan muncul jaring halus di permukaan daun.',
        'saran': ['Semprotkan air bertekanan untuk merontokkan tungau', 'Gunakan akarisida/miticide bila serangan berat',
                   'Jaga kelembapan udara di sekitar tanaman', 'Periksa daun secara rutin, terutama bagian bawah'],
        'gambar': 'Tomato_Spider_mites_Two_spotted_spider_mite.JPG'
    },
    'Tomato__Target_Spot': {
        'tanaman': 'Tomat', 'penyakit': 'Bercak Target (Target Spot)',
        'sehat': False, 'keparahan': 'Sedang',
        'deskripsi': 'Disebabkan oleh jamur Corynespora cassiicola, bercak cokelat bercincin menyerupai sasaran tembak pada daun dan buah.',
        'saran': ['Buang daun yang terinfeksi', 'Gunakan fungisida yang sesuai',
                   'Jaga jarak tanam untuk sirkulasi udara', 'Hindari kelembapan berlebih pada malam hari'],
        'gambar': 'Tomato__Target_Spot.JPG'
    },
    'Tomato__Tomato_YellowLeaf__Curl_Virus': {
        'tanaman': 'Tomat', 'penyakit': 'Virus Kuning Keriting (Yellow Leaf Curl Virus)',
        'sehat': False, 'keparahan': 'Tinggi',
        'deskripsi': 'Disebabkan oleh virus yang ditularkan kutu kebul (whitefly), menyebabkan daun menguning, mengeriting, dan pertumbuhan terhambat.',
        'saran': ['Cabut dan musnahkan tanaman yang terinfeksi berat', 'Kendalikan populasi kutu kebul sebagai vektor',
                   'Gunakan mulsa reflektif untuk mengusir vektor', 'Tanam varietas yang tahan virus bila memungkinkan'],
        'gambar': 'Tomato__Tomato_YellowLeaf__Curl_Virus.JPG'
    },
    'Tomato__Tomato_mosaic_virus': {
        'tanaman': 'Tomat', 'penyakit': 'Virus Mosaik (Mosaic Virus)',
        'sehat': False, 'keparahan': 'Tinggi',
        'deskripsi': 'Virus yang menyebabkan pola belang hijau muda-tua pada daun serta pertumbuhan tanaman yang terhambat.',
        'saran': ['Cabut dan musnahkan tanaman yang terinfeksi', 'Cuci tangan dan alat sebelum menyentuh tanaman lain',
                   'Kendalikan serangga vektor di sekitar lahan', 'Gunakan benih bebas virus untuk penanaman berikutnya'],
        'gambar': 'Tomato__Tomato_mosaic_virus.JPG'
    },
    'Tomato_healthy': {
        'tanaman': 'Tomat', 'penyakit': 'Tanaman Sehat',
        'sehat': True, 'keparahan': None,
        'deskripsi': 'Daun tomat tidak menunjukkan tanda-tanda penyakit. Warna dan tekstur daun terlihat normal.',
        'saran': ['Lanjutkan penyiraman secara teratur', 'Pastikan tanaman mendapat sinar matahari cukup',
                   'Lakukan pemupukan berkala', 'Periksa daun secara rutin untuk deteksi dini'],
        'gambar': 'Tomato_healthy.JPG'
    },
}

BULAN_ID = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
            'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']


def format_tanggal_indonesia(dt):
    return f"{dt.day} {BULAN_ID[dt.month]} {dt.year}, {dt.strftime('%H:%M')}"


def ekstensi_diizinkan(nama_file):
    return '.' in nama_file and nama_file.rsplit('.', 1)[1].lower() in EKSTENSI_DIIZINKAN


def prediksi_gambar_palsu():
    """Ganti model.predict() asli — asal pilih 1 kelas + confidence acak."""
    kelas_terpilih = random.choice(list(INFO_KELAS.keys()))
    # sesekali confidence sengaja dibuat rendah biar state "gagal" ikut kelihatan
    if random.random() < 0.2:
        confidence = random.uniform(20, AMBANG_KEYAKINAN - 1)
    else:
        confidence = random.uniform(AMBANG_KEYAKINAN, 99.5)
    return kelas_terpilih, confidence


def bangun_hasil_dari_kelas(kelas_prediksi, confidence, gambar_path):
    """Susun dict `hasil` + status dari 1 kelas terpilih — dipakai baik oleh
    upload sungguhan (dengan kelas acak) maupun trik ?demo=..."""
    if confidence < AMBANG_KEYAKINAN:
        return 'gagal', {'confidence': round(confidence, 2)}

    info = INFO_KELAS.get(kelas_prediksi)
    if info is None:
        return 'gagal', {'confidence': round(confidence, 2)}

    status = 'sehat' if info['sehat'] else 'penyakit'
    hasil = {
        'tanaman': info['tanaman'],
        'penyakit': info['penyakit'],
        'deskripsi': info['deskripsi'],
        'saran': info['saran'],
        'keparahan': info['keparahan'],
        'confidence': round(confidence, 2),
        'tanggal': format_tanggal_indonesia(datetime.now()),
    }
    return status, hasil


@app.route('/', methods=['GET', 'POST'])
def index():
    hasil = None
    gambar_path = None
    # status: 'kosong' (belum upload) | 'gagal' | 'sehat' | 'penyakit'
    status = 'kosong'

    # Trik dev: ?demo=kosong / gagal / sehat / penyakit → paksa state
    # tertentu langsung dari GET, tanpa perlu upload gambar apa pun.
    paksa = request.args.get('demo')
    if paksa in ('gagal', 'sehat', 'penyakit'):
        gambar_path = 'static/uploads/contoh-daun.jpg'  # placeholder, lihat catatan di README
        if paksa == 'gagal':
            status, hasil = 'gagal', {'confidence': 38.5}
        else:
            kelas_cocok = [k for k, v in INFO_KELAS.items() if (v['sehat'] == (paksa == 'sehat'))]
            kelas_prediksi = random.choice(kelas_cocok)
            status, hasil = bangun_hasil_dari_kelas(kelas_prediksi, random.uniform(80, 98), gambar_path)
        return render_template('index.html', hasil=hasil, gambar_path=gambar_path, status=status)

    if request.method == 'POST':
        file = request.files.get('gambar')

        if file and file.filename and ekstensi_diizinkan(file.filename):
            nama_file = secure_filename(file.filename)
            gambar_path = os.path.join(app.config['UPLOAD_FOLDER'], nama_file)
            file.save(gambar_path)

            kelas_prediksi, confidence = prediksi_gambar_palsu()
            status, hasil = bangun_hasil_dari_kelas(kelas_prediksi, confidence, gambar_path)
        else:
            status = 'gagal'
            hasil = {'confidence': 0}

    return render_template('index.html', hasil=hasil, gambar_path=gambar_path, status=status)

@app.route('/penyakit')
def penyakit():
    return render_template('penyakit.html', info_kelas=INFO_KELAS)


if __name__ == '__main__':
    app.run(debug=True)
