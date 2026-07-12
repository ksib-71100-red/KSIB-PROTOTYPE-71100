#!/usr/bin/env python3
"""
KSIB TİKTOK MASS REPORTER v3.0 - VPN EDITION
Proxy gerektirmez! VPN ile kullanım için optimize edildi.
Video + Hesap Raporlama | 10x Speed Boost
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
import socket
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Colorama başlat
init(autoreset=True)

class VPNTikTokReporter:
    def __init__(self):
        self.ua = UserAgent()
        self.success_count = 0
        self.fail_count = 0
        self.lock = threading.Lock()
        self.start_time = None
        self.session_pool = []
        self.session_lock = threading.Lock()
        
        # Rapor sebepleri - GENİŞLETİLMİŞ
        self.video_reasons = [
            "violence", 
            "sexual_content", 
            "harassment", 
            "spam", 
            "hate_speech", 
            "dangerous_acts",
            "minor_safety", 
            "suicide_self_harm",
            "illegal_activities", 
            "drugs", 
            "weapons",
            "adult_nudity", 
            "bullying", 
            "misinformation",
            "terrorism", 
            "child_abuse", 
            "fraud",
            "intellectual_property", 
            "privacy", 
            "other",
            "violent_extremism",
            "animal_cruelty",
            "dangerous_challenges",
            "hateful_behavior"
        ]
        
        self.account_reasons = [
            "spam_account", 
            "impersonation", 
            "under_age", 
            "harassment_account",
            "hate_speech_account", 
            "dangerous_organization",
            "suicide_self_harm_account", 
            "terrorism_account",
            "child_exploitation", 
            "drugs_account",
            "weapons_account", 
            "fraud_account",
            "intellectual_property_account", 
            "other",
            "fake_engagement",
            "scam_account",
            "platform_manipulation"
        ]
        
    def banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.RED + Style.BRIGHT + """
        ╔══════════════════════════════════════════════════╗
        ║     KSIB TİKTOK MASS REPORTER v3.0              ║
        ║        🛡️  VPN EDITION - NO PROXY  🛡️          ║
        ║     Video + Hesap Raporlama | 10x Speed        ║
        ╚══════════════════════════════════════════════════╝
        """ + Style.RESET_ALL)
        
        # VPN kontrolü
        print(Fore.YELLOW + "[*] VPN durumu kontrol ediliyor...")
        try:
            # IP kontrolü
            real_ip = requests.get('https://api.ipify.org', timeout=5).text
            print(Fore.GREEN + f"[+] Aktif IP: {real_ip}")
            print(Fore.CYAN + "[!] VPN'inizin açık olduğundan emin olun!")
            print(Fore.CYAN + "[!] Her 50-100 istekte bir VPN sunucusu değiştirin!\n")
        except:
            print(Fore.RED + "[-] IP kontrolü yapılamadı, internet bağlantınızı kontrol edin!")
    
    def create_session(self):
        """Her thread için özel session oluştur"""
        session = requests.Session()
        
        # Rastgele User-Agent
        session.headers.update({
            "User-Agent": self.ua.random,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": random.choice([
                "en-US,en;q=0.9", "tr-TR,tr;q=0.9", 
                "es-ES,es;q=0.9", "de-DE,de;q=0.9",
                "fr-FR,fr;q=0.9", "pt-BR,pt;q=0.9"
            ]),
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Origin": "https://www.tiktok.com",
            "Referer": "https://www.tiktok.com/",
            "sec-ch-ua": self.get_random_chrome_ua(),
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": random.choice(['"Windows"', '"macOS"', '"Linux"']),
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "DNT": "1",
            "Connection": "keep-alive",
        })
        
        return session
    
    def get_random_chrome_ua(self):
        """Rastgele Chrome versiyonu"""
        versions = [
            '"Chromium";v="120", "Google Chrome";v="120"',
            '"Chromium";v="119", "Google Chrome";v="119"',
            '"Chromium";v="118", "Google Chrome";v="118"',
            '"Chromium";v="117", "Google Chrome";v="117"',
        ]
        return random.choice(versions)
    
    def get_session(self):
        """Session havuzundan session al"""
        with self.session_lock:
            if self.session_pool:
                return self.session_pool.pop()
            return self.create_session()
    
    def return_session(self, session):
        """Session'ı havuza geri koy"""
        with self.session_lock:
            if len(self.session_pool) < 100:  # Maximum 100 session
                self.session_pool.append(session)
    
    def get_random_reason(self, report_type="video"):
        """Rastgele rapor sebebi seç"""
        if report_type == "video":
            return random.choice(self.video_reasons)
        else:
            return random.choice(self.account_reasons)
    
    def video_report(self, video_id, reason=None, session=None):
        """Video raporla - VPN üzerinden"""
        try:
            if reason is None:
                reason = self.get_random_reason("video")
            
            if session is None:
                session = self.get_session()
            
            # TikTok'un farklı API endpointleri
            endpoints = [
                f"https://www.tiktok.com/api/report/item/",
                f"https://www.tiktok.com/api/report/video/",
                f"https://api.tiktokv.com/aweme/v1/commit/item/report/",
            ]
            
            url = random.choice(endpoints)
            
            # Farklı data formatları
            data_formats = [
                {
                    "object_id": video_id,
                    "reason": reason,
                    "report_type": "video",
                    "source": "video_detail"
                },
                {
                    "object_id": video_id,
                    "reason": reason,
                    "type": 1,
                    "source": "discover"
                },
                {
                    "item_id": video_id,
                    "report_reason": reason,
                    "source": "for_you"
                }
            ]
            
            data = random.choice(data_formats)
            
            # Rastgele timeout
            timeout = random.uniform(3, 8)
            
            response = session.post(
                url, 
                json=data, 
                timeout=timeout,
                verify=False
            )
            
            if response.status_code == 200:
                return True, "Başarılı"
            elif response.status_code == 429:
                return False, "Rate Limit - VPN Değiştir!"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, str(e)[:50]
    
    def account_report(self, username, user_id, reason=None, session=None):
        """Hesap raporla - VPN üzerinden"""
        try:
            if reason is None:
                reason = self.get_random_reason("account")
            
            if session is None:
                session = self.get_session()
            
            endpoints = [
                f"https://www.tiktok.com/api/report/user/",
                f"https://www.tiktok.com/api/report/account/",
                f"https://api.tiktokv.com/aweme/v1/commit/user/report/",
            ]
            
            url = random.choice(endpoints)
            
            data_formats = [
                {
                    "object_id": user_id,
                    "owner_id": user_id,
                    "reason": reason,
                    "report_type": "user",
                    "source": "profile"
                },
                {
                    "user_id": user_id,
                    "report_reason": reason,
                    "username": username,
                    "source": "search"
                }
            ]
            
            data = random.choice(data_formats)
            
            timeout = random.uniform(3, 8)
            
            response = session.post(
                url, 
                json=data, 
                timeout=timeout,
                verify=False
            )
            
            if response.status_code == 200:
                return True, "Başarılı"
            elif response.status_code == 429:
                return False, "Rate Limit - VPN Değiştir!"
            else:
                return False, f"HTTP {response.status_code}"
                
        except Exception as e:
            return False, str(e)[:50]
    
    def worker(self, target_id, report_type="video", count=1000, username=None, thread_id=0):
        """Worker thread - VPN optimized"""
        local_success = 0
        local_fail = 0
        
        # Her thread kendi session'ını kullansın
        session = self.create_session()
        
        for i in range(count):
            # VPN kullanırken düşük gecikme yeterli
            time.sleep(random.uniform(0.001, 0.01))
            
            # Rastgele reason (her seferinde farklı)
            if report_type == "video":
                success, message = self.video_report(target_id, session=session)
            else:
                success, message = self.account_report(username, target_id, session=session)
            
            # Sonuçları güncelle
            with self.lock:
                if success:
                    local_success += 1
                    self.success_count += 1
                else:
                    local_fail += 1
                    self.fail_count += 1
                
                # Her 50 istekte bir VPN değiştirme uyarısı
                total = self.success_count + self.fail_count
                if total % 50 == 0 and "Rate Limit" in message:
                    print(Fore.RED + f"\n[!] Rate limit aşıldı! VPN sunucusunu değiştirin!")
                
                # İlerleme göster
                if total % 50 == 0:
                    elapsed = time.time() - self.start_time
                    rate = total / elapsed if elapsed > 0 else 0
                    print(f"\r[Thread-{thread_id}] 📨 Gönderilen: {total} | ✅ Başarılı: {self.success_count} | "
                          f"❌ Başarısız: {self.fail_count} | ⚡ Hız: {rate:.1f}/s", end="")
        
        # Session'ı temizle
        session.close()
        
        return local_success, local_fail
    
    def mass_report(self, target, report_type="video", count=1000, threads=50, username=None):
        """Toplu rapor başlat - VPN Edition"""
        print(Fore.CYAN + f"\n🎯 Hedef: {target}")
        print(Fore.CYAN + f"📋 Tip: {report_type.upper()}")
        print(Fore.CYAN + f"🔢 Rapor Sayısı: {count}")
        print(Fore.CYAN + f"🧵 Thread Sayısı: {threads}")
        print(Fore.GREEN + "🔒 VPN Koruması: Aktif (Proxy Gereksiz)")
        print(Fore.YELLOW + "⚠️  Uyarı: Her 50-100 raporda bir VPN sunucusu değiştirin!")
        print(Fore.RED + "[!] Saldırı başlıyor...\n")
        
        self.start_time = time.time()
        
        # Her thread'e düşen rapor sayısı
        reports_per_thread = count // threads
        remaining = count % threads
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            
            for i in range(threads):
                thread_count = reports_per_thread + (1 if i < remaining else 0)
                future = executor.submit(
                    self.worker, 
                    target, 
                    report_type, 
                    thread_count,
                    username,
                    i  # Thread ID
                )
                futures.append(future)
            
            # Bekle ve sonuçları topla
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(Fore.RED + f"\n[-] Thread hatası: {e}")
        
        # Final raporu
        self.print_final_report(target, report_type, count)
    
    def print_final_report(self, target, report_type, count):
        """Final raporunu yazdır"""
        elapsed = time.time() - self.start_time
        total = self.success_count + self.fail_count
        rate = total / elapsed if elapsed > 0 else 0
        
        print("\n\n" + "="*70)
        print(Fore.GREEN + Style.BRIGHT + "✅ RAPORLAMA TAMAMLANDI!")
        print("="*70)
        print(Fore.YELLOW + f"⏱️  Süre: {elapsed:.2f} saniye")
        print(Fore.GREEN + f"✅ Başarılı: {self.success_count}")
        print(Fore.RED + f"❌ Başarısız: {self.fail_count}")
        print(Fore.CYAN + f"📊 Toplam: {total}")
        print(Fore.MAGENTA + f"🚀 Ortalama Hız: {rate:.2f} rapor/saniye")
        print(Fore.CYAN + f"📈 Başarı Oranı: %{(self.success_count/total*100):.1f}" if total > 0 else "")
        print("="*70)
        
        # VPN tavsiyesi
        if rate < 10:
            print(Fore.YELLOW + "\n💡 İPUCU: Hız düşük! VPN sunucunuzu değiştirip tekrar deneyin.")
        
        # Sonuçları kaydet
        self.save_results(target, report_type, count, elapsed, rate)
    
    def save_results(self, target, report_type, count, elapsed, rate):
        """Sonuçları dosyaya kaydet"""
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results = {
            "target": target,
            "type": report_type,
            "mode": "VPN Edition",
            "total_reports": count,
            "successful": self.success_count,
            "failed": self.fail_count,
            "duration": elapsed,
            "rate_per_second": rate,
            "success_rate": f"%{(self.success_count/(self.success_count+self.fail_count)*100):.1f}" if (self.success_count+self.fail_count) > 0 else "0",
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        
        print(Fore.CYAN + f"\n💾 Sonuçlar kaydedildi: {filename}")
    
    def get_user_id(self, username):
        """Kullanıcı ID'sini al"""
        try:
            url = f"https://www.tiktok.com/@{username}"
            session = self.create_session()
            response = session.get(url, timeout=10)
            
            # ID çıkarma
            if "user_id" in response.text:
                import re
                match = re.search(r'"user_id":"(\d+)"', response.text)
                if match:
                    session.close()
                    return match.group(1)
            
            session.close()
            return None
        except:
            return None

def main():
    reporter = VPNTikTokReporter()
    reporter.banner()
    
    # Argümanları parse et
    parser = argparse.ArgumentParser(description='KSIB TikTok Mass Reporter v3.0 - VPN Edition')
    parser.add_argument('-t', '--target', help='Video ID veya Kullanıcı Adı (@ olmadan)')
    parser.add_argument('-m', '--mode', choices=['video', 'account'], default='video',
                       help='Rapor modu: video veya account')
    parser.add_argument('-c', '--count', type=int, default=1000,
                       help='Rapor sayısı (300, 1000, 3000, 5000)')
    parser.add_argument('-th', '--threads', type=int, default=50,
                       help='Thread sayısı (önerilen: 50-200)')
    
    args = parser.parse_args()
    
    # İnteraktif mod
    if not args.target:
        print(Fore.YELLOW + "🎮 İnteraktif Mod Başlatılıyor...\n")
        
        print(Fore.CYAN + "Rapor modu seçin:")
        print("1. 📹 Video Raporlama")
        print("2. 👤 Hesap Raporlama")
        mode = input(Fore.GREEN + "Seçiminiz (1-2): ")
        report_type = "video" if mode == "1" else "account"
        
        if report_type == "video":
            target = input(Fore.CYAN + "Video ID girin: ")
        else:
            target = input(Fore.CYAN + "Kullanıcı adı girin (@ olmadan): ")
        
        print(Fore.YELLOW + "\n📊 Rapor sayısı seçenekleri:")
        print("1. 🔥 300 rapor (Hızlı)")
        print("2. 💪 1.000 rapor (Standart)")
        print("3. 🚀 3.000 rapor (Güçlü)")
        print("4. 💣 5.000 rapor (Maximum)")
        print("5. ⚡ Özel sayı")
        
        count_choice = input(Fore.GREEN + "Seçiminiz (1-5): ")
        
        count_map = {"1": 300, "2": 1000, "3": 3000, "4": 5000}
        if count_choice in count_map:
            count = count_map[count_choice]
        else:
            count = int(input("Özel rapor sayısı girin: "))
        
        print(Fore.YELLOW + "\n🧵 Thread sayısı önerileri:")
        print("• 50 thread: Dengeli")
        print("• 100 thread: Hızlı")
        print("• 200 thread: Ultra Hızlı (Güçlü PC)")
        threads = int(input(Fore.GREEN + "Thread sayısı (varsayılan: 50): ") or "50")
        
    else:
        report_type = args.mode
        target = args.target
        count = args.count
        threads = args.threads
    
    # Username kontrolü
    username = target if report_type == "account" else None
    
    # Hesap modunda user_id al
    if report_type == "account":
        if target.isdigit():
            print(Fore.GREEN + f"[+] User ID direkt kullanılıyor: {target}")
        else:
            print(Fore.YELLOW + f"[*] @{target} kullanıcısının ID'si alınıyor...")
            user_id = reporter.get_user_id(target)
            if user_id:
                print(Fore.GREEN + f"[+] User ID bulundu: {user_id}")
                target = user_id
            else:
                print(Fore.RED + "[-] User ID alınamadı! Kullanıcı adı doğru mu?")
                sys.exit(1)
    
    # Son onay
    print(Fore.YELLOW + "\n" + "="*50)
    print(Fore.CYAN + "📋 OPERASYON ÖZETİ:")
    print(f"   Hedef: {target}")
    print(f"   Mod: {report_type.upper()}")
    print(f"   Rapor: {count} adet")
    print(f"   Thread: {threads}")
    print(f"   VPN: ✅ Aktif")
    print("="*50)
    
    confirm = input(Fore.RED + f"\n⚠️  {count} rapor gönderilecek. Devam edilsin mi? (E/H): ")
    if confirm.upper() != 'E':
        print(Fore.YELLOW + "İptal edildi.")
        sys.exit(0)
    
    print(Fore.GREEN + "\n🔔 VPN'inizin açık olduğundan emin olun!")
    print(Fore.GREEN + "💡 İpucu: Rate limit yerseniz VPN sunucusu değiştirin!\n")
    
    # BAŞLAT!
    reporter.mass_report(
        target=target,
        report_type=report_type,
        count=count,
        threads=threads,
        username=username
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n[!] Program durduruldu!")
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"\n[!] Kritik hata: {e}")
        sys.exit(1)
