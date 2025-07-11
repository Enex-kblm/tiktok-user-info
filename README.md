# TikTok Info Lookup

🔍 **TikTok Info Lookup** adalah aplikasi web yang memungkinkan Anda untuk mendapatkan informasi lengkap dari akun TikTok dengan mudah dan cepat.

## ✨ Fitur

- 🎯 **Pencarian Username**: Cari informasi akun TikTok dengan username
- 📊 **Statistik Lengkap**: Followers, Following, Likes, dan jumlah Video
- 👤 **Info Profil**: Nama, Bio, Region, dan status verifikasi
- 📱 **Responsive Design**: Tampilan yang optimal di semua perangkat
- ⚡ **Fast & Reliable**: Performa cepat dengan error handling yang baik

## 🚀 Demo

Website ini di-deploy di Vercel dan dapat diakses secara langsung.

## 🛠️ Teknologi

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Vercel
- **Styling**: Custom CSS dengan Font Awesome icons

## 📋 Cara Penggunaan

1. Buka website
2. Masukkan username TikTok (dengan atau tanpa @)
3. Klik "Cari Profil"
4. Lihat informasi lengkap akun TikTok

## 🔧 Development

### Requirements
- Python 3.8+
- FastAPI
- Requests
- Uvicorn

### Local Development
```bash
pip install -r requirements.txt
uvicorn api.index:app --reload
```

## 📝 API Endpoints

- `GET /` - Homepage
- `POST /search` - Search TikTok profile
- `GET /health` - Health check

## ⚠️ Disclaimer

Tool ini dibuat untuk tujuan edukasi dan penelitian. Pastikan untuk menggunakan dengan bijak dan mematuhi terms of service TikTok.

## 📄 License

MIT License - Silakan gunakan dan modifikasi sesuai kebutuhan.