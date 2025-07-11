import requests
import re
from bs4 import BeautifulSoup

def get_user_data(identifier):
    if identifier.startswith('@'):
        identifier = identifier[1:]
    url = f"https://www.tiktok.com/@{identifier}"
    headers = {'User-Agent': 'Mozilla/5.0'}

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return {"error": "Failed to fetch user"}

    html = res.text
    patterns = {
        'unique_id': r'"uniqueId":"(.*?)"',
        'nickname': r'"nickname":"(.*?)"',
        'followers': r'"followerCount":(\d+)',
        'following': r'"followingCount":(\d+)',
        'likes': r'"heartCount":(\d+)',
        'videos': r'"videoCount":(\d+)',
        'signature': r'"signature":"(.*?)"',
        'region': r'"region":"([a-zA-Z]+)"',
    }

    info = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, html)
        info[key] = match.group(1) if match else 'N/A'

    return info
