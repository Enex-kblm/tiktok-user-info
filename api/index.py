from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
import requests
import re
from urllib.parse import quote
import json

app = FastAPI()

def format_number(num_str):
    """Format angka menjadi format yang lebih mudah dibaca"""
    try:
        num = int(num_str)
        if num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        return str(num)
    except:
        return num_str

def get_user_data(identifier):
    try:
        # Bersihkan identifier
        if identifier.startswith('@'):
            identifier = identifier[1:]
        
        # Encode username untuk URL
        encoded_username = quote(identifier)
        url = f"https://www.tiktok.com/@{encoded_username}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            return {"error": "Akun tidak ditemukan. Pastikan username benar."}
        elif response.status_code != 200:
            return {"error": f"Gagal mengakses profil (Status: {response.status_code})"}

        html = response.text
        
        # Pattern untuk mencari data
        patterns = {
            'unique_id': r'"uniqueId":"([^"]*)"',
            'nickname': r'"nickname":"([^"]*)"',
            'followers': r'"followerCount":(\d+)',
            'following': r'"followingCount":(\d+)',
            'likes': r'"heartCount":(\d+)',
            'videos': r'"videoCount":(\d+)',
            'signature': r'"signature":"([^"]*)"',
            'region': r'"region":"([^"]*)"',
            'verified': r'"verified":(true|false)',
        }

        info = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, html)
            if match:
                value = match.group(1)
                # Format angka untuk statistik
                if key in ['followers', 'following', 'likes', 'videos']:
                    info[key] = format_number(value)
                    info[f'{key}_raw'] = value
                else:
                    info[key] = value
            else:
                info[key] = 'N/A'

        # Jika tidak ada data ditemukan, kemungkinan akun private atau tidak ada
        if info.get('unique_id') == 'N/A' and info.get('nickname') == 'N/A':
            return {"error": "Data profil tidak dapat diakses. Akun mungkin private atau tidak ditemukan."}

        # Bersihkan signature dari karakter escape
        if info.get('signature') and info['signature'] != 'N/A':
            info['signature'] = info['signature'].replace('\\n', ' ').replace('\\', '')

        return info

    except requests.exceptions.Timeout:
        return {"error": "Timeout: Koneksi ke TikTok terlalu lama"}
    except requests.exceptions.ConnectionError:
        return {"error": "Error: Tidak dapat terhubung ke TikTok"}
    except Exception as e:
        return {"error": f"Terjadi kesalahan: {str(e)}"}

# HTML Templates sebagai string
INDEX_HTML = """<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TikTok Info Lookup - Cari Info Akun TikTok</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 500px;
            width: 100%;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #ff0050, #ff4081, #ff6ec7);
        }

        .logo {
            font-size: 3rem;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #ff0050, #ff4081);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2rem;
            font-weight: 700;
        }

        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1rem;
        }

        .form-group {
            margin-bottom: 30px;
            position: relative;
        }

        .input-container {
            position: relative;
            display: flex;
            align-items: center;
            background: #f8f9fa;
            border-radius: 15px;
            padding: 5px;
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }

        .input-container:focus-within {
            border-color: #ff4081;
            box-shadow: 0 0 0 3px rgba(255, 64, 129, 0.1);
        }

        .input-icon {
            padding: 15px;
            color: #666;
            font-size: 1.2rem;
        }

        input[type="text"] {
            flex: 1;
            border: none;
            background: transparent;
            padding: 15px 10px;
            font-size: 1.1rem;
            outline: none;
            color: #333;
        }

        input[type="text"]::placeholder {
            color: #999;
        }

        .search-btn {
            background: linear-gradient(45deg, #ff0050, #ff4081);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 10px;
            justify-content: center;
            width: 100%;
            margin-top: 20px;
        }

        .search-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(255, 64, 129, 0.3);
        }

        .search-btn:active {
            transform: translateY(0);
        }

        .features {
            margin-top: 30px;
            padding-top: 30px;
            border-top: 1px solid #eee;
        }

        .feature-list {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 20px;
        }

        .feature-item {
            display: flex;
            align-items: center;
            gap: 10px;
            color: #666;
            font-size: 0.9rem;
        }

        .feature-icon {
            color: #ff4081;
            font-size: 1rem;
        }

        .loading {
            display: none;
            align-items: center;
            gap: 10px;
        }

        .spinner {
            width: 20px;
            height: 20px;
            border: 2px solid #ffffff40;
            border-top: 2px solid #ffffff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @media (max-width: 600px) {
            .container {
                padding: 30px 20px;
                margin: 10px;
            }

            h1 {
                font-size: 1.5rem;
            }

            .feature-list {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <i class="fab fa-tiktok"></i>
        </div>
        <h1>TikTok Info Lookup</h1>
        <p class="subtitle">Dapatkan informasi lengkap akun TikTok dengan mudah</p>
        
        <form method="post" id="searchForm" action="/search">
            <div class="form-group">
                <div class="input-container">
                    <div class="input-icon">
                        <i class="fas fa-at"></i>
                    </div>
                    <input 
                        type="text" 
                        name="username" 
                        placeholder="Masukkan username TikTok (contoh: @username)" 
                        required
                        autocomplete="off"
                        id="usernameInput"
                    >
                </div>
            </div>
            
            <button type="submit" class="search-btn" id="searchBtn">
                <span class="btn-text">
                    <i class="fas fa-search"></i>
                    Cari Profil
                </span>
                <span class="loading">
                    <div class="spinner"></div>
                    Mencari...
                </span>
            </button>
        </form>

        <div class="features">
            <h3 style="color: #333; margin-bottom: 15px;">Informasi yang Didapat:</h3>
            <div class="feature-list">
                <div class="feature-item">
                    <i class="fas fa-user feature-icon"></i>
                    <span>Nama & Username</span>
                </div>
                <div class="feature-item">
                    <i class="fas fa-users feature-icon"></i>
                    <span>Jumlah Followers</span>
                </div>
                <div class="feature-item">
                    <i class="fas fa-heart feature-icon"></i>
                    <span>Total Likes</span>
                </div>
                <div class="feature-item">
                    <i class="fas fa-video feature-icon"></i>
                    <span>Jumlah Video</span>
                </div>
                <div class="feature-item">
                    <i class="fas fa-map-marker-alt feature-icon"></i>
                    <span>Lokasi/Region</span>
                </div>
                <div class="feature-item">
                    <i class="fas fa-quote-left feature-icon"></i>
                    <span>Bio/Signature</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('searchForm').addEventListener('submit', function(e) {
            const btn = document.getElementById('searchBtn');
            const btnText = btn.querySelector('.btn-text');
            const loading = btn.querySelector('.loading');
            
            btnText.style.display = 'none';
            loading.style.display = 'flex';
            btn.disabled = true;
        });

        // Auto-add @ if not present
        document.getElementById('usernameInput').addEventListener('input', function(e) {
            let value = e.target.value;
            if (value && !value.startsWith('@')) {
                e.target.value = '@' + value;
            }
        });
    </script>
</body>
</html>"""

def generate_result_html(info):
    return f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hasil Pencarian - TikTok Info Lookup</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
            position: relative;
        }}

        .container::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #ff0050, #ff4081, #ff6ec7);
        }}

        .header {{
            background: linear-gradient(45deg, #ff0050, #ff4081);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 1.8rem;
            margin-bottom: 10px;
        }}

        .content {{
            padding: 30px;
        }}

        .error-container {{
            text-align: center;
            padding: 40px 20px;
        }}

        .error-icon {{
            font-size: 4rem;
            color: #ff4757;
            margin-bottom: 20px;
        }}

        .error-message {{
            font-size: 1.2rem;
            color: #333;
            margin-bottom: 30px;
            line-height: 1.5;
        }}

        .profile-container {{
            animation: fadeInUp 0.6s ease;
        }}

        .profile-header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f1f2f6;
        }}

        .profile-avatar {{
            width: 100px;
            height: 100px;
            background: linear-gradient(45deg, #ff0050, #ff4081);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            font-size: 3rem;
            color: white;
        }}

        .profile-name {{
            font-size: 1.8rem;
            font-weight: 700;
            color: #333;
            margin-bottom: 5px;
        }}

        .profile-username {{
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 15px;
        }}

        .verified-badge {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background: #1da1f2;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            transition: transform 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
        }}

        .stat-icon {{
            font-size: 2rem;
            margin-bottom: 10px;
        }}

        .stat-number {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #333;
            margin-bottom: 5px;
        }}

        .stat-label {{
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .followers {{ color: #ff4081; }}
        .following {{ color: #2ed573; }}
        .likes {{ color: #ff6b6b; }}
        .videos {{ color: #5352ed; }}

        .bio-section {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
        }}

        .bio-title {{
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .bio-text {{
            color: #666;
            line-height: 1.6;
            font-style: italic;
        }}

        .region-info {{
            display: flex;
            align-items: center;
            gap: 10px;
            color: #666;
            margin-bottom: 20px;
        }}

        .action-buttons {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}

        .btn {{
            flex: 1;
            min-width: 150px;
            padding: 15px 25px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}

        .btn-primary {{
            background: linear-gradient(45deg, #ff0050, #ff4081);
            color: white;
        }}

        .btn-secondary {{
            background: #f1f2f6;
            color: #333;
        }}

        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }}

        .btn-primary:hover {{
            box-shadow: 0 10px 25px rgba(255, 64, 129, 0.3);
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @media (max-width: 600px) {{
            .container {{
                margin: 10px;
            }}

            .header, .content {{
                padding: 20px;
            }}

            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .action-buttons {{
                flex-direction: column;
            }}

            .btn {{
                min-width: auto;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fab fa-tiktok"></i> Hasil Pencarian</h1>
        </div>
        
        <div class="content">
            {"".join([
                f'''<div class="error-container">
                    <div class="error-icon">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <div class="error-message">{info["error"]}</div>
                    <a href="/" class="btn btn-primary">
                        <i class="fas fa-arrow-left"></i>
                        Coba Lagi
                    </a>
                </div>''' if info.get("error") else f'''<div class="profile-container">
                    <div class="profile-header">
                        <div class="profile-avatar">
                            <i class="fas fa-user"></i>
                        </div>
                        <div class="profile-name">{info.get('nickname', 'Nama tidak tersedia') if info.get('nickname') != 'N/A' else 'Nama tidak tersedia'}</div>
                        <div class="profile-username">@{info.get('unique_id', 'N/A')}</div>
                        {"<div class=\"verified-badge\"><i class=\"fas fa-check-circle\"></i>Terverifikasi</div>" if info.get('verified') == 'true' else ""}
                    </div>

                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-icon followers">
                                <i class="fas fa-users"></i>
                            </div>
                            <div class="stat-number">{info.get('followers', '0') if info.get('followers') != 'N/A' else '0'}</div>
                            <div class="stat-label">Followers</div>
                        </div>
                        
                        <div class="stat-card">
                            <div class="stat-icon following">
                                <i class="fas fa-user-plus"></i>
                            </div>
                            <div class="stat-number">{info.get('following', '0') if info.get('following') != 'N/A' else '0'}</div>
                            <div class="stat-label">Following</div>
                        </div>
                        
                        <div class="stat-card">
                            <div class="stat-icon likes">
                                <i class="fas fa-heart"></i>
                            </div>
                            <div class="stat-number">{info.get('likes', '0') if info.get('likes') != 'N/A' else '0'}</div>
                            <div class="stat-label">Likes</div>
                        </div>
                        
                        <div class="stat-card">
                            <div class="stat-icon videos">
                                <i class="fas fa-video"></i>
                            </div>
                            <div class="stat-number">{info.get('videos', '0') if info.get('videos') != 'N/A' else '0'}</div>
                            <div class="stat-label">Videos</div>
                        </div>
                    </div>

                    {f'''<div class="bio-section">
                        <div class="bio-title">
                            <i class="fas fa-quote-left"></i>
                            Bio
                        </div>
                        <div class="bio-text">{info.get('signature', '')}</div>
                    </div>''' if info.get('signature') and info.get('signature') != 'N/A' and info.get('signature', '').strip() else ''}

                    {f'''<div class="region-info">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>Region: {info.get('region', '')}</span>
                    </div>''' if info.get('region') and info.get('region') != 'N/A' else ''}

                    <div class="action-buttons">
                        <a href="https://www.tiktok.com/@{info.get('unique_id', '')}" target="_blank" class="btn btn-primary">
                            <i class="fab fa-tiktok"></i>
                            Lihat di TikTok
                        </a>
                        <a href="/" class="btn btn-secondary">
                            <i class="fas fa-search"></i>
                            Cari Lagi
                        </a>
                    </div>
                </div>'''
            ])}
        </div>
    </div>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content=INDEX_HTML)

@app.post("/search", response_class=HTMLResponse)
async def search(request: Request, username: str = Form(...)):
    try:
        if not username.strip():
            info = {"error": "Username tidak boleh kosong"}
        else:
            info = get_user_data(username.strip())
        
        return HTMLResponse(content=generate_result_html(info))
    except Exception as e:
        error_info = {"error": f"Terjadi kesalahan: {str(e)}"}
        return HTMLResponse(content=generate_result_html(error_info))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "TikTok Info Lookup API is running"}

# Handler untuk Vercel
handler = app