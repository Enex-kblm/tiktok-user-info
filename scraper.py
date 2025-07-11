import requests
import re
from bs4 import BeautifulSoup
import json
from urllib.parse import quote

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