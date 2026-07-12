#!/usr/bin/env python3
"""
KSIB TOOLS - WhatsApp Mass Reporter v4.0
KITA BAZLI ÜLKE SEÇİMİ | ŞİFRE KORUMALI
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

KONTROL = "c4e5a7f8d9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"

# KITA BAZLI ÜLKELER
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
            "261": "Madagaskar 🇲🇬", "262": "Reunion 🇷🇪", "263": "Zimbabve 🇿🇼",
            "264": "Namibya 🇳🇦", "265": "Malavi 🇲🇼", "266": "Lesoto 🇱🇸",
            "267": "Botsvana 🇧🇼", "268": "Esvatini 🇸🇿", "269": "Komorlar 🇰🇲",
            "27": "Güney Afrika 🇿🇦", "290": "Saint Helena 🇸🇭", "291": "Eritre 🇪🇷",
        }
    },
    "2": {
        "isim": "🌍 AVRUPA",
        "ulkeler": {
            "30": "Yunanistan 🇬🇷", "31": "Hollanda 🇳🇱", "32": "Belçika 🇧🇪",
            "33": "Fransa 🇫🇷", "34": "İspanya 🇪🇸", "350": "Cebelitarık 🇬🇮",
            "351": "Portekiz 🇵🇹", "352": "Lüksemburg 🇱🇺", "353": "İrlanda 🇮🇪",
            "354": "İzlanda 🇮🇸", "355": "Arnavutluk 🇦🇱", "356": "Malta 🇲🇹",
            "357": "Kıbrıs 🇨🇾", "358": "Finlandiya 🇫🇮", "359": "Bulgaristan 🇧🇬",
            "36": "Macaristan 🇭🇺", "370": "Litvanya 🇱🇹", "371": "Letonya 🇱🇻",
            "372": "Estonya 🇪🇪", "373": "Moldova 🇲🇩", "374": "Ermenistan 🇦🇲",
            "375": "Belarus 🇧🇾", "376": "Andorra 🇦🇩", "377": "Monako 🇲🇨",
            "378": "San Marino 🇸🇲", "380": "Ukrayna 🇺🇦", "381": "Sırbistan 🇷🇸",
            "382": "Karadağ 🇲🇪", "383": "Kosova 🇽🇰", "385": "Hırvatistan 🇭🇷",
            "386": "Slovenya 🇸🇮", "387": "Bosna Hersek 🇧🇦", "389": "Kuzey Makedonya 🇲🇰",
            "39": "İtalya 🇮🇹", "40": "Romanya 🇷🇴", "41": "İsviçre 🇨🇭",
            "420": "Çekya 🇨🇿", "421": "Slovakya 🇸🇰", "423": "Lihtenştayn 🇱🇮",
            "43": "Avusturya 🇦🇹", "44": "İngiltere 🇬🇧", "45": "Danimarka 🇩🇰",
            "46": "İsveç 🇸🇪", "47": "Norveç 🇳🇴", "48": "Polonya 🇵🇱",
            "49": "Almanya 🇩🇪",
        }
    },
    "3": {
        "isim": "🌏 ASYA & ORTA DOĞU",
        "ulkeler": {
            "1": "ABD/Kanada (NANP) 🇺🇸🇨🇦", "7": "Rusya/Kazakistan 🇷🇺🇰🇿",
            "81": "Japonya 🇯🇵", "82": "Güney Kore 🇰🇷", "84": "Vietnam 🇻🇳",
            "850": "Kuzey Kore 🇰🇵", "852": "Hong Kong 🇭🇰", "853": "Makao 🇲🇴",
            "855": "Kamboçya 🇰🇭", "856": "Laos 🇱🇦", "86": "Çin 🇨🇳",
            "880": "Bangladeş 🇧🇩", "886": "Tayvan 🇹🇼", "90": "Türkiye 🇹🇷",
            "91": "Hindistan 🇮🇳", "92": "Pakistan 🇵🇰", "93": "Afganistan 🇦🇫",
            "94": "Sri Lanka 🇱🇰", "95": "Myanmar 🇲🇲", "960": "Maldivler 🇲🇻",
            "961": "Lübnan 🇱🇧", "962": "Ürdün 🇯🇴", "963": "Suriye 🇸🇾",
            "964": "Irak 🇮🇶", "965": "Kuveyt 🇰🇼", "966": "Suudi Arabistan 🇸🇦",
            "967": "Yemen 🇾🇪", "968": "Umman 🇴🇲", "970": "Filistin 🇵🇸",
            "971": "BAE 🇦🇪", "972": "İsrail 🇮🇱", "973": "Bahreyn 🇧🇭",
            "974": "Katar 🇶🇦", "975": "Butan 🇧🇹", "976": "Moğolistan 🇲🇳",
            "977": "Nepal 🇳🇵", "98": "İran 🇮🇷", "992": "Tacikistan 🇹🇯",
            "993": "Türkmenistan 🇹🇲", "994": "Azerbaycan 🇦🇿", "995": "Gürcistan 🇬🇪",
            "996": "Kırgızistan 🇰🇬", "998": "Özbekistan 🇺🇿",
        }
    },
    "4": {
        "isim": "🌎 AMERİKA",
        "ulkeler": {
            "1": "ABD/Kanada/Karayipler 🇺🇸🇨🇦", "52": "Meksika 🇲🇽",
            "53": "Küba 🇨🇺", "54": "Arjantin 🇦🇷", "55": "Brezilya 🇧🇷",
            "56": "Şili 🇨🇱", "57": "Kolombiya 🇨🇴", "58": "Venezuela 🇻🇪",
            "500": "Falkland Adaları 🇫🇰", "501": "Belize 🇧🇿", "502": "Guatemala 🇬🇹",
            "503": "El Salvador 🇸🇻", "504": "Honduras 🇭🇳", "505": "Nikaragua 🇳🇮",
            "506": "Kosta Rika 🇨🇷", "507": "Panama 🇵🇦", "508": "Saint Pierre 🇵🇲",
            "509": "Haiti 🇭🇹", "51": "Peru 🇵🇪", "591": "Bolivya 🇧🇴",
            "592": "Guyana 🇬🇾", "593": "Ekvador 🇪🇨", "594": "Fransız Guyanası 🇬🇫",
            "595": "Paraguay 🇵🇾", "596": "Martinik 🇲🇶", "597": "Surinam 🇸🇷",
            "598": "Uruguay 🇺🇾", "599": "Hollanda Antilleri 🇳🇱",
        }
    },
    "5": {
        "isim": "🌏 OKYANUSYA",
        "ulkeler": {
            "61": "Avustralya 🇦🇺", "64": "Yeni Zelanda 🇳🇿",
            "672": "Antarktika 🇦🇶", "673": "Brunei 🇧🇳", "674": "Nauru 🇳🇷",
            "675": "Papua Yeni Gine 🇵🇬", "676": "Tonga 🇹🇴", "677": "Solomon Adaları 🇸🇧",
            "678": "Vanuatu 🇻🇺", "679": "Fiji 🇫🇯", "680": "Palau 🇵🇼",
            "681": "Wallis Futuna 🇼🇫", "682": "Cook Adaları 🇨🇰", "683": "Niue 🇳🇺",
            "685": "Samoa 🇼🇸", "686": "Kiribati 🇰🇮", "687": "Yeni Kaledonya 🇳🇨",
            "688": "Tuvalu 🇹🇻", "689": "Fransız Polinezyası 🇵🇫", "690": "Tokelau 🇹🇰",
            "691": "Mikronezya 🇫🇲", "692": "Marshall Adaları 🇲🇭",
        }
    }
}

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
            print(Fore.GREEN + "\n✅ Başarılı!\n")
            time.sleep(0.5)
            return True
        print(Fore.RED + f"❌ Hatalı! ({2-i} hakkın kaldı)\n")
    sys.exit(0)

def ulke_sec():
    """Kıta bazlı ülke seçimi"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + Style.BRIGHT + """
    ╔══════════════════════════════════════╗
    ║        🌍 KITA SEÇİMİ              ║
    ╚══════════════════════════════════════╝
    """ + Style.RESET_ALL)
    
    # Kıtaları listele
    for kod, kita in KITALAR.items():
        print(Fore.YELLOW + f"[{kod}] {kita['isim']} ({len(kita['ulkeler'])} ülke)")
    
    print(Fore.CYAN + "\n[0] ✨ Özel ülke kodu gir")
    
    kita_secim = input(Fore.GREEN + "\n🌍 Kıta seçin: ")
    
    if kita_secim == "0":
        # Direkt ülke kodu
        kod = input(Fore.GREEN + "🔢 Ülke kodu girin (+ olmadan): ")
        return kod
    
    if kita_secim not in KITALAR:
        print(Fore.RED + "❌ Geçersiz seçim!")
        time.sleep(1)
        return ulke_sec()
    
    # Seçilen kıtadaki ülkeleri listele
    os.system('cls' if os.name == 'nt' else 'clear')
    kita = KITALAR[kita_secim]
    
    print(Fore.CYAN + Style.BRIGHT + f"""
    ╔══════════════════════════════════════╗
    ║     {kita['isim']} ÜLKELERİ      ║
    ╚══════════════════════════════════════╝
    """ + Style.RESET_ALL)
    
    # Ülkeleri 3 sütun halinde listele
    ulkeler = list(kita['ulkeler'].items())
    
    for i, (kod, isim) in enumerate(ulkeler, 1):
        print(Fore.WHITE + f"[{i:3d}] {isim:<30s} (+{kod})")
    
    print(Fore.YELLOW + f"\n[0] 🔙 Ana menüye dön")
    
    try:
        secim = int(input(Fore.GREEN + f"\n🌍 Ülke seçin (1-{len(ulkeler)}): "))
        
        if secim == 0:
            return ulke_sec()
        
        if 1 <= secim <= len(ulkeler):
            kod, isim = ulkeler[secim-1]
            print(Fore.GREEN + f"\n✅ Seçilen: {isim} (+{kod})")
            time.sleep(0.5)
            return kod
        else:
            print(Fore.RED + "❌ Geçersiz seçim!")
            time.sleep(1)
            return ulke_sec()
    
    except ValueError:
        print(Fore.RED + "❌ Sayı girin!")
        time.sleep(1)
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
        self.ulke_kodu = "TR"
        
        self.r = [
            "spam", "spam_messages", "spam_commercial",
            "harassment", "harassment_sexual", "harassment_threatening",
            "inappropriate_content", "adult_content", "violent_content",
            "hate_speech", "illegal_content",
            "fake_account", "impersonation", "scam", "fraud",
            "other", "violence", "terrorism",
            "child_exploitation", "drugs", "weapons", "suicide_self_harm",
        ]
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.GREEN + Style.BRIGHT + """
        ╔══════════════════════════════════════╗
        ║  WHATSAPP MASS REPORTER v4.0       ║
        ║  💬 Kıta Bazlı | 200+ Ülke        ║
        ╚══════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def oturum(self):
        s = requests.Session()
        s.headers.update({
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
        return s
    
    def rr(self):
        return random.choice(self.r)
    
    def rpt1(self, p, r, s):
        try:
            u = "https://www.whatsapp.com/contact/nocontact"
            h = {
                "User-Agent": self.ua.random,
                "Referer": "https://www.whatsapp.com/contact/",
                "Origin": "https://www.whatsapp.com",
                "Content-Type": "application/x-www-form-urlencoded",
            }
            d = {
                "phone_number": p, "violation": r,
                "description": f"Report for {r}",
                "email": f"r{random.randint(1000,9999)}@gmail.com",
                "language": "en", "country": self.ulke_kodu,
            }
            resp = s.post(u, data=d, headers=h, timeout=15)
            return resp.status_code in [200, 201, 202, 302]
        except: return False
    
    def rpt2(self, p, r, s):
        try:
            u = "https://www.whatsapp.com/contact/violation"
            h = {
                "User-Agent": self.ua.random,
                "Referer": "https://www.whatsapp.com/",
                "Origin": "https://www.whatsapp.com",
                "Content-Type": "application/json",
            }
            d = {
                "report_type": "user", "reported_number": p,
                "violation_type": r, "message": f"Reporting user for {r}",
                "report_country": self.ulke_kodu,
                "platform": random.choice(["android", "ios", "web"]),
            }
            resp = s.post(u, json=d, headers=h, timeout=15)
            return resp.status_code in [200, 201, 202]
        except: return False
    
    def rpt3(self, g, r, s):
        try:
            u = "https://www.whatsapp.com/contact/violation"
            h = {
                "User-Agent": self.ua.random,
                "Referer": "https://www.whatsapp.com/",
                "Origin": "https://www.whatsapp.com",
                "Content-Type": "application/json",
            }
            d = {
                "report_type": "group", "group_invite_link": g,
                "violation_type": r, "message": f"Reporting group for {r}",
                "report_country": self.ulke_kodu,
                "platform": random.choice(["android", "ios", "web"]),
            }
            resp = s.post(u, json=d, headers=h, timeout=15)
            return resp.status_code in [200, 201, 202]
        except: return False
    
    def rpt4(self, p, r, s):
        try:
            u = "https://www.whatsapp.com/contact/nocontact"
            h = {
                "User-Agent": self.ua.random,
                "Referer": "https://www.whatsapp.com/business/",
                "Origin": "https://www.whatsapp.com",
                "Content-Type": "application/json",
            }
            d = {
                "report_type": "business", "phone_number": p,
                "violation_type": r, "business_violation": "true",
                "description": f"Business violation: {r}",
                "email": f"b{random.randint(1000,9999)}@gmail.com",
                "report_country": self.ulke_kodu,
            }
            resp = s.post(u, json=d, headers=h, timeout=15)
            return resp.status_code in [200, 201, 202]
        except: return False
    
    def isci(self, t, tp, tid):
        s = self.oturum()
        
        while self.s < self.mx:
            r = self.rr()
            
            try:
                if tp == "1":
                    rs = self.rpt1(t, r, s) if random.random() > 0.5 else self.rpt2(t, r, s)
                elif tp == "2":
                    rs = self.rpt3(t, r, s)
                elif tp == "3":
                    rs = self.rpt4(t, r, s)
                elif tp == "4":
                    c = random.random()
                    if c < 0.4: rs = self.rpt1(t, r, s)
                    elif c < 0.7: rs = self.rpt2(t, r, s)
                    else: rs = self.rpt4(t, r, s)
                else:
                    rs = False
                
                with self.k:
                    if self.s >= self.mx: break
                    self.s += 1
                    if rs: self.b += 1
                    else: self.f += 1
                    
                    if self.s % 25 == 0 or self.s == self.mx:
                        e = time.time() - self.st
                        rt = self.s / e if e > 0 else 0
                        et = (self.mx - self.s) / rt if rt > 0 else 0
                        print(f"\r[{Fore.GREEN}✓{Style.RESET_ALL}] {self.s}/{self.mx} | "
                              f"✅{self.b} ❌{self.f} | ⚡{rt:.1f}/s | ⏳{et:.0f}s", end="")
                
                time.sleep(random.uniform(0.5, 1.5))
            except: continue
    
    def baslat(self, t, tp, c=100, th=30):
        self.mx = c
        
        print(Fore.CYAN + f"\n📱 Hedef: {t}")
        print(Fore.CYAN + f"🌍 Ülke Kodu: +{self.ulke_kodu}")
        print(Fore.CYAN + f"📊 Rapor: {c} | 🧵 Thread: {th}")
        print(Fore.RED + "\n💣 BAŞLATILIYOR...\n")
        
        self.st = time.time()
        tl = []
        for i in range(th):
            tr = threading.Thread(target=self.isci, args=(t, tp, i))
            tr.daemon = True
            tr.start()
            tl.append(tr)
        
        try:
            for tr in tl: tr.join()
        except KeyboardInterrupt:
            print(Fore.RED + "\n\n[!] Durduruldu!")
        
        self.sonuc()
    
    def sonuc(self):
        e = time.time() - self.st if self.st else 0
        t = self.b + self.f
        rt = t / e if e > 0 else 0
        pm = rt * 60
        
        print("\n\n" + "="*50)
        print(Fore.GREEN + "📊 SONUÇ")
        print("="*50)
        print(f"⏱️  Süre: {e:.1f}s ({e/60:.1f}dk)")
        print(f"📨 Toplam: {t}")
        print(f"✅ Başarılı: {self.b}")
        print(f"❌ Başarısız: {self.f}")
        if t > 0: print(f"📈 Oran: %{self.b/t*100:.1f}")
        print(f"⚡ Hız: {rt:.1f}/s | ⏱️ {pm:.0f}/dk")
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
        # ÜLKE SEÇİMİ
        w.ulke_kodu = ulke_sec()
        
        print(Fore.YELLOW + f"\n📱 Telefon numarası (+{w.ulke_kodu} için):")
        print(Fore.CYAN + f"   Sadece numarayı yaz, +{w.ulke_kodu} otomatik eklenecek")
        numara = input(Fore.GREEN + "> ")
        
        # Numarayı birleştir
        numara = ''.join(filter(str.isdigit, numara))
        if numara.startswith('0'):
            numara = numara[1:]
        t = w.ulke_kodu + numara
    
    print(Fore.YELLOW + "\n📊 Rapor Sayısı:")
    print("1. 100 | 2. 500 | 3. 1000 | 4. 3000 | 5. 5000")
    c = input(Fore.GREEN + "Seçim (1-5): ")
    ct = {"1": 100, "2": 500, "3": 1000, "4": 3000, "5": 5000}.get(c, 100)
    
    th = int(input(Fore.GREEN + "\n🧵 Thread (30): ") or "30")
    
    print(Fore.RED + "\n⚠️  Sorumluluk size ait!")
    if input(Fore.GREEN + "Devam? (E/H): ").upper() == 'E':
        w.baslat(t, tp, ct, th)

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Çıkış yapıldı!")
        sys.exit(0)
