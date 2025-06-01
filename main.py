import os
import time
import schedule
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from telegram import Bot
import asyncio
import json
import random

# Ortam değişkenlerini yükle (Render'da ayarladığınız ortam değişkenleri)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# Botu başlat
bot = Bot(TELEGRAM_BOT_TOKEN)

# Fakülte ve duyuru URL'leri
FACULTIES = {
    'Ana Site': 'https://www.firat.edu.tr/tr/page/announcement',
    'Mühendislik Fakültesi': 'https://muhendislikf.firat.edu.tr/announcements-all',
    'Teknoloji Fakültesi': 'https://teknolojif.firat.edu.tr/announcements-all',
    'Diş Hekimliği Fakültesi': 'https://disf.firat.edu.tr/announcements-all',
    'Eczacılık Fakültesi': 'https://eczacilikf.firat.edu.tr/tr/announcements-all',
    'Eğitim Fakültesi': 'https://egitimf.firat.edu.tr/tr/announcements-all',
    'Fen Fakültesi': 'https://fenf.firat.edu.tr/tr/announcements-all',
    'İktisadi ve İdari Bilimler Fakültesi': 'https://iibf.firat.edu.tr/announcements-all',
    'İlahiyat Fakültesi': 'https://ilahiyatf.firat.edu.tr/announcements-all',
    'İletişim Fakültesi': 'https://iletisimf.firat.edu.tr/announcements-all',
    'İnsan ve Toplum Bilimleri Fakültesi': 'https://isbf.firat.edu.tr/announcements-all',
    'Mimarlık Fakültesi': 'https://mimarlikf.firat.edu.tr/tr/announcements-all',
    'Sağlık Bilimleri Fakültesi': 'https://saglikf.firat.edu.tr/announcements-all',
    'Spor Bilimleri Fakültesi': 'https://sporbilimlerif.firat.edu.tr/announcements-all',
    'Su Ürünleri Fakültesi': 'https://suuf.firat.edu.tr/announcements-all',
    'Teknik Eğitim Fakültesi': 'https://tef.firat.edu.tr/announcements-all',
    'Tıp Fakültesi': 'https://tip.firat.edu.tr/announcements-all',
    'Veteriner Fakültesi': 'https://veterinerf.firat.edu.tr/announcements-all',
    'Öğrenci İşleri Daire Başkanlığı': 'https://ogrencidb.firat.edu.tr/announcements-all',
    'Yaz Okulu': 'https://yazokuluyeni.firat.edu.tr/announcements-all',
    'Kütüphane ve Dokümantasyon Daire Başkanlığı': 'https://kutuphanedb.firat.edu.tr/announcements-all',
    'Sağlık Kültür ve Spor Daire Başkanlığı': 'https://sksdab.firat.edu.tr/announcements-all',
    'Erasmus+ Kurum Koordinatörlüğü': 'https://disiliskilerkoord.firat.edu.tr/tr/announcements-all',
    'Öğrenci Koordinatörlüğü': 'https://ogrencidekanligi.firat.edu.tr/announcements-all',
    'Eğitim Bilimleri Enstitüsü': 'https://egitim.firat.edu.tr/tr/announcements-all',
    'Fen Bilimleri Enstitüsü': 'https://fen.firat.edu.tr/tr/announcements-all',
    'Sağlık Bilimleri Enstitüsü': 'https://saglik.firat.edu.tr/tr/announcements-all',
    'Sosyal Bilimler Enstitüsü': 'https://sosyal.firat.edu.tr/tr/announcements-all',
    'Yabancı Diller Yüksekokulu': 'https://yabancidiller.firat.edu.tr/tr/announcements-all',
    'Devರೀಕರಣಗೊಂಗು:Devlet Konservatuvarı': 'https://kyo.firat.edu.tr/tr/announcements-all',
    'Sivil Havacılık Yüksekokulu': 'https://sivilhavacilik.firat.edu.tr/tr/announcements-all',
    'Sosyal Tesisler İktisadi İşletmesi': 'https://sosyaltesisler.firat.edu.tr/announcements-all'
}

def load_last_announcements():
    """Son görülen duyuruları JSON dosyasından yükler."""
    try:
        with open('last_announcements.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_last_announcements(last_announcements):
    """Son görülen duyuruları JSON dosyasına kaydeder."""
    with open('last_announcements.json', 'w') as f:
        json.dump(last_announcements, f)

def fetch_announcement(url):
    """Belirtilen URL'den en son duyuruyu çeker (SSL doğrulamasını devre dışı bırakır)."""
    try:
        response = requests.get(url, timeout=30, verify=False)  # SSL doğrulamasını devre dışı bırak
        soup = BeautifulSoup(response.content, 'html.parser')
        if 'firat.edu.tr/tr/page/announcement' in url:
            announcements = soup.find_all('div', class_='announcement-list-item')
            if announcements:
                title = announcements[0].find('h3').text.strip()
                date = announcements[0].find('span', class_='date').text.strip()
                return {'title': title, 'date': date}
        else:
            announcements = soup.find_all('div', class_='views-row')
            if announcements:
                title_elem = announcements[0].find('span', class_='field-content')
                date_elem = announcements[0].find('div', class_='views-field-created')
                if title_elem and date_elem:
                    return {'title': title_elem.text.strip(), 'date': date_elem.text.strip()}
        return None
    except Exception as e:
        print(f"Hata: {url} adresinden duyuru çekilemedi: {e}")
        return None

async def send_telegram_message(message):
    """Telegram'a asenkron olarak mesaj gönderir."""
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')
    except Exception as e:
        print(f"Telegram mesajı gönderilemedi: {e}")

def sync_send_telegram_message(message):
    """Senkron bir wrapper ile asenkron mesaj gönderme fonksiyonunu çağırır."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_telegram_message(message))

def check_announcements():
    """Tüm fakültelerin duyurularını kontrol eder ve yeni duyuru varsa bildirir."""
    print(f"[{datetime.now()}] Duyurular kontrol ediliyor...")
    last_announcements = load_last_announcements()
    for faculty_name, url in FACULTIES.items():
        announcement = fetch_announcement(url)
        if announcement:
            current_announcement = f"{announcement['title']}_{announcement['date']}"
            if faculty_name not in last_announcements or last_announcements[faculty_name] != current_announcement:
                message = f"🔔 <b>Yeni Duyuru!</b>\n\n📍 <b>Fakülte:</b> {faculty_name}\n📢 <b>Başlık:</b> {announcement['title']}\n📅 <b>Tarih:</b> {announcement['date']}"
                sync_send_telegram_message(message)
                last_announcements[faculty_name] = current_announcement
    save_last_announcements(last_announcements)
    print(f"[{datetime.now()}] Kontrol tamamlandı.")

def send_test_message():
    """Test mesajı gönderir."""
    sync_send_telegram_message("Test mesajı: Bot çalışıyor!")

def send_latest_announcement_test():
    """Rastgele bir fakültenin son duyurusunu test amaçlı gönderir."""
    faculty_name = random.choice(list(FACULTIES.keys()))
    url = FACULTIES[faculty_name]
    announcement = fetch_announcement(url)
    if announcement:
        message = f"Test: {faculty_name} fakültesinin son duyurusu\n📢 <b>Başlık:</b> {announcement['title']}\n📅 <b>Tarih:</b> {announcement['date']}"
        sync_send_telegram_message(message)

def main():
    """Ana fonksiyon: Test mesajı, son duyuru testi ve periyodik kontrolleri başlatır."""
    print("Fırat Üniversitesi Duyuru Botu başlatıldı...")
    
    # Test mesajı gönder
    send_test_message()
    
    # Rastgele bir fakültenin son duyurusunu test amaçlı gönder
    send_latest_announcement_test()
    
    # Her 3 dakikada bir duyuruları kontrol et
    schedule.every(3).minutes.do(check_announcements)
    
    # Script'i çalışır durumda tut
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
