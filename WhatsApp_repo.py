#!/usr/bin/env python3
"""
KSIB TOOLS - WhatsApp Mass Reporter
TEK KOMUT | ŞİFRE KORUMALI
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
        ║  WHATSAPP MASS REPORTER v2.0       ║
        ║  💬 Bireysel | Grup | Business     ║
        ╚══════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def oturum(self):
        s = requests.Session()
        s.headers.update({
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
        })
        return s
    
    def fmt(self, p):
        p = ''.join(filter(str.isdigit, p))
        if p.startswith('0'): p = p[1:]
        if not p.startswith('90'): p = '90' + p
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
                "phone_number": p, "violation": r,
                "description": f"Report for {r}",
                "email": f"r{random.randint(1000,9999)}@gmail.com",
                "language": "en", "country": "TR",
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
                "report_country": "TR",
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
                "report_type": "group", "group_invite_link": g,
                "violation_type": r, "message": f"Reporting group for {r}",
                "report_country": "TR",
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
                "report_country": "TR",
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
        print(Fore.YELLOW + "\n📱 Telefon (5XXXXXXXXX):")
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
