#!/usr/bin/env python3
"""
KSIB TİKTOK MASS REPORTER v3.1 - USER ID FIX
VPN'siz de çalışır, gelişmiş User ID algılama
"""

import requests
import threading
import random
import time
import json
import re
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

class TikTokReporter:
    def __init__(self):
        self.ua = UserAgent()
        self.success_count = 0
        self.fail_count = 0
        self.lock = threading.Lock()
        self.start_time = None
        self.session_pool = []
        self.session_lock = threading.Lock()
        
        # Rapor sebepleri
        self.video_reasons = [
            "violence", "sexual_content", "harassment", 
            "spam", "hate_speech", "dangerous_acts",
            "minor_safety", "suicide_self_harm",
            "illegal_activities", "drugs", "weapons",
            "adult_nudity", "bullying", "misinformation",
            "terrorism", "child_abuse", "fraud",
            "intellectual_property", "privacy", "other"
        ]
        
        self.account_reasons = [
            "spam_account", "impersonation", 
            "under_age", "harassment_account",
            "hate_speech_account", "dangerous_organization",
            "suicide_self_harm_account", "terrorism_account",
            "child_exploitation", "drugs_account",
            "weapons_account", "fraud_account",
            "intellectual_property_account", "other"
        ]
        
    def banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.RED + Style.BRIGHT + """
        ╔══════════════════════════════════════════════════╗
        ║     KSIB TİKTOK MASS REPORTER v3.1              ║
        ║        🔧 USER ID FIX - VPN'SİZ ÇALIŞIR         ║
        ║     Video + Hesap Raporlama | 10x Speed        ║
        ╚══════════════════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def create_session(self):
        """Her thread için özel session"""
        session = requests.Session()
        session.headers.update({
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        })
        return session
    
    def get_user_id_method1(self, username):
        """Yöntem 1: Web scraping ile ID alma"""
        try:
            session = self.create_session()
            url = f"https://www.tiktok.com/@{username}"
            response = session.get(url, timeout=15)
            
            print(Fore.YELLOW + f"[*] Yöntem 1 deneniyor... Status: {response.status_code}")
            
            if response.status_code == 200:
                html = response.text
                
                # Farklı pattern'lerle ID ara
                patterns = [
                    r'"user_id":"(\d+)"',
                    r'"id":"(\d+)"',
                    r'user_id=(\d+)',
                    r'"authorId":"(\d+)"',
                    r'"owner_id":"(\d+)"',
                    r'"uid":"(\d+)"',
                    r'uniqueId":"' + username + '".*?"id":"(\d+)"',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, html)
                    if match:
                        user_id = match.group(1)
                        print(Fore.GREEN + f"[+] User ID bulundu (Pattern): {user_id}")
                        session.close()
                        return user_id
                
            session.close()
            return None
        except Exception as e:
            print(Fore.RED + f"[-] Yöntem 1 hata: {str(e)[:50]}")
            return None
    
    def get_user_id_method2(self, username):
        """Yöntem 2: TikTok API ile ID alma"""
        try:
            session = self.create_session()
            
            # Farklı API endpoint'leri dene
            apis = [
                f"https://www.tiktok.com/api/user/detail/?uniqueId={username}",
                f"https://www.tiktok.com/node/share/user/@{username}",
                f"https://m.tiktok.com/api/user/detail/?uniqueId={username}",
            ]
            
            for api_url in apis:
                try:
                    print(Fore.YELLOW + f"[*] API deneniyor: {api_url[:50]}...")
                    
                    headers = {
                        "User-Agent": self.ua.random,
                        "Accept": "application/json, text/plain, */*",
                        "Referer": f"https://www.tiktok.com/@{username}",
                    }
                    
                    response = session.get(api_url, headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # JSON içinde ID ara
                        user_info = None
                        if "userInfo" in data:
                            user_info = data["userInfo"]
                        elif "user" in data:
                            user_info = data["user"]
                        elif "data" in data:
                            user_info = data["data"]
                        
                        if user_info:
                            user_id = user_info.get("id") or user_info.get("userId") or user_info.get("uid")
                            if user_id:
                                print(Fore.GREEN + f"[+] User ID bulundu (API): {user_id}")
                                session.close()
                                return str(user_id)
                
                except Exception as e:
                    continue
            
            session.close()
            return None
            
        except Exception as e:
            print(Fore.RED + f"[-] Yöntem 2 hata: {str(e)[:50]}")
            return None
    
    def get_user_id_method3(self, username):
        """Yöntem 3: Alternatif siteler üzerinden ID alma"""
        try:
            # TikTok'un mobile versiyonu daha az korumalı
            session = self.create_session()
            
            mobile_headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            
            url = f"https://m.tiktok.com/@{username}"
            response = session.get(url, headers=mobile_headers, timeout=15)
            
            print(Fore.YELLOW + f"[*] Mobil site deneniyor... Status: {response.status_code}")
            
            if response.status_code == 200:
                html = response.text
                
                # Mobil sitede ID ara
                patterns = [
                    r'"userId":"(\d+)"',
                    r'"id":"(\d+)"',
                    r'userId=(\d+)',
                    r'"author_id":"(\d+)"',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, html)
                    if match:
                        user_id = match.group(1)
                        print(Fore.GREEN + f"[+] User ID bulundu (Mobil): {user_id}")
                        session.close()
                        return user_id
            
            session.close()
            return None
            
        except Exception as e:
            print(Fore.RED + f"[-] Yöntem 3 hata: {str(e)[:50]}")
            return None
    
    def get_user_id_manual_input(self):
        """Kullanıcıdan manuel ID girişi al"""
        print(Fore.YELLOW + "\n[!] Otomatik ID bulunamadı!")
        print(Fore.CYAN + "Manuel olarak User ID girebilirsiniz.")
        print(Fore.CYAN + "User ID'yi şuradan bulabilirsiniz:")
        print(Fore.CYAN + "1. TikTok profil sayfasına gidin")
        print(Fore.CYAN + "2. Sayfa kaynağını görüntüleyin (Sağ tık > Sayfa Kaynağını Görüntüle)")
        print(Fore.CYAN + '3. "user_id" veya "authorId" araması yapın')
        print(Fore.CYAN + "4. Bulduğunuz sayısal ID'yi girin\n")
        
        user_id = input(Fore.GREEN + "User ID girin (veya çıkmak için 'q'): ")
        return user_id if user_id.lower() != 'q' else None
    
    def get_user_id(self, username):
        """Tüm yöntemleri dene, User ID'yi bul"""
        print(Fore.CYAN + f"\n[*] @{username} için User ID aranıyor...\n")
        
        # Eğer direkt sayı girildiyse
        if username.isdigit():
            print(Fore.GREEN + f"[+] Sayısal ID algılandı: {username}")
            return username
        
        # Yöntemleri sırayla dene
        methods = [
            ("Web Scraping", self.get_user_id_method1),
            ("TikTok API", self.get_user_id_method2),
            ("Mobil Site", self.get_user_id_method3),
        ]
        
        for method_name, method_func in methods:
            print(Fore.CYAN + f"\n🔍 {method_name} yöntemi deneniyor...")
            user_id = method_func(username)
            if user_id:
                return user_id
            time.sleep(1)  # Rate limit yememek için bekle
        
        # Hiçbiri çalışmazsa manuel giriş
        return self.get_user_id_manual_input()
    
    def get_random_reason(self, report_type="video"):
        """Rastgele rapor sebebi"""
        if report_type == "video":
            return random.choice(self.video_reasons)
        return random.choice(self.account_reasons)
    
    def video_report(self, video_id, reason=None, session=None):
        """Video raporla"""
        try:
            if reason is None:
                reason = self.get_random_reason("video")
            
            if session is None:
                session = self.create_session()
            
            url = "https://www.tiktok.com/api/report/item/"
            
            headers = {
                "User-Agent": self.ua.random,
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
                "Origin": "https://www.tiktok.com",
                "Referer": "https://www.tiktok.com/",
            }
            
            data = {
                "object_id": video_id,
                "reason": reason,
                "report_type": "video",
                "source": "video_detail"
            }
            
            response = session.post(url, json=data, headers=headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                return True, "Başarılı"
            elif response.status_code == 429:
                return False, "Rate Limit"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, str(e)[:50]
    
    def account_report(self, username, user_id, reason=None, session=None):
        """Hesap raporla"""
        try:
            if reason is None:
                reason = self.get_random_reason("account")
            
            if session is None:
                session = self.create_session()
            
            url = "https://www.tiktok.com/api/report/user/"
            
            headers = {
                "User-Agent": self.ua.random,
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
                "Origin": "https://www.tiktok.com",
                "Referer": f"https://www.tiktok.com/@{username}",
            }
            
            data = {
                "object_id": user_id,
                "owner_id": user_id,
                "reason": reason,
                "report_type": "user",
                "source": "profile"
            }
            
            response = session.post(url, json=data, headers=headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                return True, "Başarılı"
            elif response.status_code == 429:
                return False, "Rate Limit"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, str(e)[:50]
    
    def worker(self, target_id, report_type="video", count=1000, username=None, thread_id=0):
        """Worker thread"""
        local_success = 0
        local_fail = 0
        session = self.create_session()
        
        for i in range(count):
            time.sleep(random.uniform(0.001, 0.01))
            
            if report_type == "video":
                success, message = self.video_report(target_id, session=session)
            else:
                success, message = self.account_report(username, target_id, session=session)
            
            with self.lock:
                if success:
                    local_success += 1
                    self.success_count += 1
                else:
                    local_fail += 1
                    self.fail_count += 1
                
                total = self.success_count + self.fail_count
                if total % 50 == 0:
                    elapsed = time.time() - self.start_time
                    rate = total / elapsed if elapsed > 0 else 0
                    print(f"\r[Thread-{thread_id}] 📨 {total} | ✅ {self.success_count} | "
                          f"❌ {self.fail_count} | ⚡ {rate:.1f}/s", end="")
        
        session.close()
        return local_success, local_fail
    
    def mass_report(self, target, report_type="video", count=1000, threads=50, username=None):
        """Toplu rapor başlat"""
        print(Fore.CYAN + f"\n🎯 Hedef: {target}")
        print(Fore.CYAN + f"📋 Tip: {report_type.upper()}")
        print(Fore.CYAN + f"🔢 Rapor: {count} | 🧵 Thread: {threads}")
        print(Fore.RED + "[!] Başlatılıyor...\n")
        
        self.start_time = time.time()
        
        reports_per_thread = count // threads
        remaining = count % threads
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            
            for i in range(threads):
                thread_count = reports_per_thread + (1 if i < remaining else 0)
                future = executor.submit(
                    self.worker, target, report_type, thread_count, username, i
                )
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(Fore.RED + f"\n[-] Thread hatası: {e}")
        
        # Sonuçlar
        elapsed = time.time() - self.start_time
        total = self.success_count + self.fail_count
        rate = total / elapsed if elapsed > 0 else 0
        
        print("\n\n" + "="*60)
        print(Fore.GREEN + Style.BRIGHT + "✅ TAMAMLANDI!")
        print("="*60)
        print(f"⏱️  Süre: {elapsed:.2f}s | ⚡ Hız: {rate:.1f}/s")
        print(f"✅ Başarılı: {self.success_count} | ❌ Başarısız: {self.fail_count}")
        print("="*60)

def main():
    reporter = TikTokReporter()
    reporter.banner()
    
    # Menü
    print(Fore.YELLOW + "Rapor modu:")
    print("1. 📹 Video Raporlama")
    print("2. 👤 Hesap Raporlama")
    mode = input(Fore.GREEN + "Seçim (1-2): ")
    report_type = "video" if mode == "1" else "account"
    
    if report_type == "video":
        target = input(Fore.CYAN + "Video ID girin: ")
        username = None
    else:
        target = input(Fore.CYAN + "Kullanıcı adı girin (@ olmadan): ")
        
        # User ID'yi al
        user_id = reporter.get_user_id(target)
        
        if not user_id:
            print(Fore.RED + "\n[!] User ID alınamadı! Program sonlandırılıyor.")
            sys.exit(1)
        
        username = target
        target = user_id
    
    print(Fore.YELLOW + "\nRapor sayısı:")
    print("1. 300 | 2. 1000 | 3. 3000 | 4. 5000")
    count_choice = input(Fore.GREEN + "Seçim (1-4): ")
    count_map = {"1": 300, "2": 1000, "3": 3000, "4": 5000}
    count = count_map.get(count_choice, 1000)
    
    threads = int(input(Fore.GREEN + "Thread sayısı (50): ") or "50")
    
    # Onay
    print(f"\n⚠️  {count} rapor gönderilecek!")
    confirm = input("Devam? (E/H): ")
    if confirm.upper() != 'E':
        sys.exit(0)
    
    # Başlat
    reporter.mass_report(target, report_type, count, threads, username)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n[!] Durduruldu!")
        sys.exit(0)
