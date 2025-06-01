send_telegram_message("Test mesajı: Bot çalışıyor!")

import time
from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

# Ortam değişkenlerinden Telegram token ve chat ID'sini al
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

def check_announcements():
    # Buraya duyuru kontrol mantığınızı ekleyin
    # Örneğin: Web scraping ile duyuruları çekme, Firestore'dan veri okuma, Telegram'a mesaj gönderme
    print("Duyurular kontrol ediliyor...")
    # Örnek: 
    # import requests
    # from bs4 import BeautifulSoup
    # # Web scraping kodları
    # # Telegram'a mesaj gönderme:
    # import telegram
    # bot = telegram.Bot(token=TELEGRAM_TOKEN)
    # bot.send_message(chat_id=CHAT_ID, text="Yeni duyuru var!")

def run_periodically():
    while True:
        check_announcements()
        time.sleep(180)  # 3 dakika bekle

@app.route('/')
def home():
    return "Bot çalışıyor!"

if __name__ == "__main__":
    # Periyodik görevi arka planda çalıştır
    thread = Thread(target=run_periodically)
    thread.start()
    # Flask sunucusunu başlat
    app.run(host='0.0.0.0', port=8080)
