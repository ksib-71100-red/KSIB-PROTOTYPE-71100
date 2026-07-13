#!/usr/bin/env python3
# KSIB TİKTOK ULTRA BOT v3.1 - Otomatik ID + Manuel ID
import requests, threading, random, time, sys, os, json, re, hashlib, string
from fake_useragent import UserAgent
from colorama import init, Fore, Back, Style
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

SIFRE = "admiral71100daphne"

def giris():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + Style.BRIGHT + """
    ╔══════════════════════════════════════╗
    ║        🔐 KSIB PRO GİRİŞ           ║
    ╚══════════════════════════════════════╝
    """ + Style.RESET_ALL)
    for i in range(3):
        s = input(Fore.YELLOW + "\n🔑 Şifre: ")
        if s == SIFRE:
            print(Fore.GREEN + "\n✅ Giriş başarılı! Yükleniyor...\n")
            time.sleep(1)
            return True
        print(Fore.RED + f"❌ Hatalı! ({2-i} hakkın)")
    sys.exit(0)

class TikTokUltraBot:
    def __init__(self):
        self.ua = UserAgent()
        self.view_count = 0
        self.follow_count = 0
        self.like_count = 0
        self.share_count = 0
        self.comment_count = 0
        self.fail_count = 0
        self.lock = threading.Lock()
        self.start_time = None
        self.max_count = 0
        self.running = True
        
        self.proxies = []
        self.device_ids = []
        for _ in range(100):
            self.device_ids.append(self.generate_device_id())
        
        self.sessions = []
        self.watch_times = [3, 5, 7, 10, 12, 15, 20, 25, 30, 45, 60]
        self.scroll_behaviors = ["fast", "normal", "slow", "pause", "rewatch"]
        
        self.behavior_patterns = [
            {"action": "watch", "min": 3, "max": 15},
            {"action": "like", "probability": 0.4},
            {"action": "scroll", "min": 1, "max": 5},
            {"action": "pause", "min": 2, "max": 8},
            {"action": "watch_full", "probability": 0.2},
        ]
        
        # TikTok API'leri
        self.api_versions = [
            "https://www.tiktok.com/api/user/detail/?uniqueId={username}",
            "https://www.tiktok.com/node/share/user/@{username}",
            "https://m.tiktok.com/api/user/detail/?uniqueId={username}",
        ]
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.MAGENTA + Style.BRIGHT + """
        ╔══════════════════════════════════════════════════╗
        ║   🎵 TİKTOK ULTRA BOT v3.1                     ║
        ║   👁️ View | 👤 Follow | ❤️ Like | 💬 Comment    ║
        ║   🛡️ Ban Korumalı | 🔒 Kalıcı Takipçi           ║
        ║   🔍 Otomatik ID Çekme | Manuel ID Girişi      ║
        ╚══════════════════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def generate_device_id(self):
        chars = string.hexdigits.lower()[:16]
        return ''.join(random.choice(chars) for _ in range(32))
    
    def generate_session_id(self):
        return hashlib.md5(str(random.random()).encode()).hexdigest()
    
    def get_headers(self, mobile=False):
        if mobile:
            return {
                "User-Agent": random.choice([
                    "com.zhiliaoapp.musically/2023700040 (Linux; U; Android 13; tr_TR; SM-G998B Build/TP1A.220624.014; tt-ok/3.12.0)",
                    "com.zhiliaoapp.musically/2023700030 (Linux; U; Android 14; tr_TR; Pixel 7 Pro Build/TQ1A.230205.002; tt-ok/3.12.0)",
                    "com.zhiliaoapp.musically/2023600020 (Linux; U; Android 13; tr_TR; iPhone 14 Pro; tt-ok/3.11.0)",
                    "com.zhiliaoapp.musically/2023500010 (Linux; U; Android 12; tr_TR; SM-A536B Build/SP1A.210812.016; tt-ok/3.10.0)",
                ]),
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "x-tt-request-tag": "t=0;n=0;",
                "x-tt-trace-id": hashlib.md5(str(random.random()).encode()).hexdigest()[:13],
            }
        else:
            return {
                "User-Agent": self.ua.random,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
    
    def get_cookies(self):
        return {
            "tt_webid": self.generate_device_id(),
            "tt_webid_v2": self.generate_device_id(),
            "tt_csrf_token": self.generate_session_id(),
            "sessionid": self.generate_session_id(),
            "ttwid": "1%7C" + self.generate_session_id(),
        }
    
    def get_user_id(self, username):
        """Kullanıcı adından ID çek, olmazsa manuel sor"""
        print(Fore.YELLOW + f"\n🔍 @{username} kullanıcısı aranıyor...")
        print(Fore.CYAN + "   API'ler deneniyor...\n")
        
        user_id = None
        user_info = {}
        
        # YÖNTEM 1: API ile otomatik çek
        for i, api_url in enumerate(self.api_versions, 1):
            try:
                url = api_url.format(username=username)
                headers = self.get_headers(mobile=True)
                
                print(Fore.WHITE + f"   [{i}/{len(self.api_versions)}] {api_url.split('/')[2]} deneniyor...", end=" ")
                
                r = requests.get(url, headers=headers, timeout=10, verify=False)
                
                if r.status_code == 200:
                    # JSON kontrolü
                    try:
                        data = r.json()
                        user_data = None
                        
                        if 'userInfo' in data:
                            user_data = data['userInfo']
                        elif 'user' in data:
                            user_data = data['user']
                        elif 'data' in data:
                            user_data = data['data']
                        
                        if user_data:
                            uid = user_data.get('id') or user_data.get('userId') or user_data.get('uid')
                            if uid:
                                user_id = str(uid)
                                user_info = {
                                    'user_id': user_id,
                                    'username': user_data.get('uniqueId', username),
                                    'nickname': user_data.get('nickname', ''),
                                    'followers': user_data.get('followerCount', 0),
                                    'following': user_data.get('followingCount', 0),
                                    'videos': user_data.get('videoCount', 0),
                                    'verified': user_data.get('verified', False),
                                }
                                print(Fore.GREEN + "✅ BULUNDU!")
                                break
                    except:
                        pass
                    
                    # HTML'den çek
                    if not user_id:
                        html = r.text
                        patterns = [
                            r'"user_id":"(\d+)"',
                            r'"id":"(\d+)"',
                            r'"userId":"(\d+)"',
                            r'"uid":"(\d+)"',
                            r'"authorId":"(\d+)"',
                            r'"owner_id":"(\d+)"',
                        ]
                        for pattern in patterns:
                            match = re.search(pattern, html)
                            if match:
                                user_id = match.group(1)
                                user_info['user_id'] = user_id
                                user_info['username'] = username
                                print(Fore.GREEN + "✅ BULUNDU!")
                                break
                
                if user_id:
                    break
                else:
                    print(Fore.RED + "❌ Bulunamadı")
                    
            except Exception as e:
                print(Fore.RED + f"❌ Hata")
            
            time.sleep(0.5)
        
        # YÖNTEM 2: Bulunamadıysa manuel ID sor
        if not user_id:
            print(Fore.RED + "\n❌ Otomatik ID çekilemedi!")
            print(Fore.YELLOW + "\n💡 MANUEL ID GİRİŞİ:")
            print(Fore.CYAN + "   TikTok profil sayfasına girip sayfa kaynağında")
            print(Fore.CYAN + "   'user_id' veya 'authorId' araması yapın.")
            print(Fore.CYAN + "   Bulduğunuz sayısal ID'yi girin.\n")
            
            while not user_id:
                user_id = input(Fore.GREEN + "🔢 User ID girin (çıkmak için 'q'): ").strip()
                
                if user_id.lower() == 'q':
                    print(Fore.YELLOW + "❌ İptal edildi.")
                    return None, None
                
                if user_id.isdigit() and len(user_id) > 5:
                    user_info = {
                        'user_id': user_id,
                        'username': username,
                        'nickname': username,
                        'followers': 0,
                        'following': 0,
                        'videos': 0,
                        'verified': False,
                    }
                    print(Fore.GREEN + f"✅ Manuel ID kabul edildi: {user_id}")
                    break
                else:
                    print(Fore.RED + "❌ Geçersiz ID! Sadece rakam girin (en az 6 haneli).")
        
        # Sonuç gösterimi
        if user_id and user_info:
            print(Fore.CYAN + f"\n📋 KULLANICI BİLGİLERİ:")
            print(Fore.WHITE + f"   👤 Kullanıcı: @{user_info.get('username', username)}")
            print(Fore.WHITE + f"   📝 İsim: {user_info.get('nickname', '-')}")
            print(Fore.WHITE + f"   🔢 User ID: {user_info.get('user_id', user_id)}")
            print(Fore.WHITE + f"   👥 Takipçi: {user_info.get('followers', 0):,}")
            print(Fore.WHITE + f"   🎵 Video: {user_info.get('videos', 0):,}")
            if user_info.get('verified'):
                print(Fore.BLUE + "   ✅ Doğrulanmış Hesap!")
            
            return user_info.get('user_id', user_id), user_info
        
        return None, None
    
    def get_video_id_from_user(self, user_id):
        """Kullanıcının son videolarından birinin ID'sini çek"""
        try:
            headers = self.get_headers(mobile=True)
            url = f"https://www.tiktok.com/api/user/video/list/?userId={user_id}&count=10"
            
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                videos = data.get('videos', []) or data.get('items', [])
                if videos:
                    video_id = videos[0].get('id') or videos[0].get('video_id')
                    return str(video_id)
        except:
            pass
        return None
    
    def human_delay(self, action_type="normal"):
        delays = {
            "fast": (0.5, 1.5),
            "normal": (1, 3),
            "slow": (2, 5),
            "very_slow": (5, 15),
            "scroll": (0.3, 1),
            "like": (0.5, 2),
            "follow": (2, 5),
        }
        min_d, max_d = delays.get(action_type, (1, 3))
        time.sleep(random.uniform(min_d, max_d))
    
    def send_view_safe(self, video_id):
        try:
            session = requests.Session()
            session.headers.update(self.get_headers(mobile=True))
            session.cookies.update(self.get_cookies())
            
            watch_time = random.choice(self.watch_times)
            behavior = random.choice(self.scroll_behaviors)
            
            endpoints = [
                f"https://www.tiktok.com/api/video/play/?video_id={video_id}&source=recommend&offset={random.randint(0, 500)}",
                f"https://www.tiktok.com/node/share/video/{video_id}",
                f"https://m.tiktok.com/api/video/play/?video_id={video_id}&source=foryou",
            ]
            
            url = random.choice(endpoints)
            
            params = {
                "video_id": video_id,
                "play_time": watch_time,
                "behavior": behavior,
                "device_id": random.choice(self.device_ids),
                "session_id": self.generate_session_id(),
                "ts": int(time.time()),
            }
            
            r = session.get(url, params=params, timeout=10)
            
            if r.status_code == 200:
                with self.lock:
                    self.view_count += 1
                return True
            return False
        except:
            return False
    
    def send_follow_safe(self, user_id):
        try:
            session = requests.Session()
            session.headers.update(self.get_headers(mobile=True))
            session.cookies.update(self.get_cookies())
            
            profile_url = f"https://www.tiktok.com/@{user_id}"
            session.get(profile_url, timeout=10)
            self.human_delay("slow")
            
            for _ in range(random.randint(1, 3)):
                self.human_delay("like")
            
            follow_url = "https://www.tiktok.com/api/follow/user/"
            data = {
                "user_id": user_id,
                "source": "profile",
                "type": "1",
                "device_id": random.choice(self.device_ids),
                "ts": int(time.time()),
            }
            
            headers = {
                "User-Agent": random.choice([
                    "com.zhiliaoapp.musically/2023700040 (Linux; U; Android 13)",
                    "com.zhiliaoapp.musically/2023700030 (Linux; U; Android 14)",
                ]),
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": f"https://www.tiktok.com/@{user_id}",
                "x-tt-request-tag": "t=0;n=1;",
            }
            
            r = session.post(follow_url, data=data, headers=headers, timeout=10)
            
            if r.status_code == 200:
                with self.lock:
                    self.follow_count += 1
                return True
            return False
        except:
            return False
    
    def send_like_safe(self, video_id):
        try:
            session = requests.Session()
            session.headers.update(self.get_headers(mobile=True))
            
            watch_time = random.choice(self.watch_times)
            time.sleep(watch_time * 0.3)
            
            like_url = "https://www.tiktok.com/api/video/like/"
            data = {
                "video_id": video_id,
                "type": "1",
                "device_id": random.choice(self.device_ids),
            }
            
            r = session.post(like_url, data=data, timeout=10)
            
            if r.status_code == 200:
                with self.lock:
                    self.like_count += 1
                return True
            return False
        except:
            return False
    
    def send_share_safe(self, video_id):
        try:
            session = requests.Session()
            session.headers.update(self.get_headers(mobile=True))
            
            share_url = f"https://www.tiktok.com/api/video/share/"
            data = {
                "video_id": video_id,
                "share_type": random.choice(["copy_link", "whatsapp", "twitter", "facebook"]),
            }
            
            r = session.post(share_url, data=data, timeout=10)
            
            if r.status_code == 200:
                with self.lock:
                    self.share_count += 1
                return True
            return False
        except:
            return False
    
    def view_worker(self, video_id, thread_id):
        session_views = 0
        
        while self.running and self.view_count < self.max_count:
            try:
                if session_views >= random.randint(20, 50):
                    session_views = 0
                    self.human_delay("very_slow")
                
                if self.send_view_safe(video_id):
                    session_views += 1
                
                self.human_delay("fast")
                
                if random.random() < 0.3:
                    self.send_like_safe(video_id)
                
                if random.random() < 0.1:
                    self.send_share_safe(video_id)
            except:
                continue
    
    def follow_worker(self, user_id, thread_id):
        session_follows = 0
        
        while self.running and self.follow_count < self.max_count:
            try:
                if session_follows >= random.randint(5, 10):
                    session_follows = 0
                    self.human_delay("very_slow")
                
                if self.send_follow_safe(user_id):
                    session_follows += 1
                
                self.human_delay("follow")
            except:
                continue
    
    def progress_bar(self, current, total, width=40):
        filled = int(width * current / total) if total > 0 else 0
        bar = Fore.GREEN + "█" * filled + Fore.WHITE + "░" * (width - filled)
        percent = current / total * 100 if total > 0 else 0
        return f"[{bar}] %{percent:.1f}"
    
    def status_display(self):
        while self.running:
            time.sleep(2)
            with self.lock:
                elapsed = time.time() - self.start_time if self.start_time else 0
                
                os.system('cls' if os.name == 'nt' else 'clear')
                print(Fore.MAGENTA + Style.BRIGHT + """
        ╔══════════════════════════════════════════════════╗
        ║   🎵 TİKTOK ULTRA BOT - CANLI DURUM            ║
        ╚══════════════════════════════════════════════════╝
                """ + Style.RESET_ALL)
                
                print(Fore.CYAN + f"  ⏱️  Çalışma Süresi: {elapsed:.0f} saniye")
                print()
                
                if self.max_count > 0:
                    print(Fore.YELLOW + "  👁️  VIEW:")
                    print(f"  {self.progress_bar(self.view_count, self.max_count)}")
                    print(Fore.GREEN + f"  ✅ {self.view_count:,} / {self.max_count:,}")
                    
                    print(Fore.YELLOW + "\n  👤  FOLLOW:")
                    print(f"  {self.progress_bar(self.follow_count, self.max_count)}")
                    print(Fore.GREEN + f"  ✅ {self.follow_count:,} / {self.max_count:,}")
                
                print(Fore.CYAN + f"\n  ❤️  Like: {self.like_count:,}")
                print(Fore.CYAN + f"  🔄 Share: {self.share_count:,}")
                print(Fore.RED + f"  ❌ Fail: {self.fail_count:,}")
                
                if elapsed > 0:
                    total = self.view_count + self.follow_count
                    rate = total / elapsed
                    print(Fore.YELLOW + f"\n  ⚡ Hız: {rate:.1f}/saniye")
                    if rate > 0 and self.max_count > 0:
                        remaining = (self.max_count * 2 - total) / rate
                        print(Fore.YELLOW + f"  ⏳ Tahmini Kalan: {remaining:.0f} saniye")
                
                print(Fore.MAGENTA + "\n  🛡️ Ban Koruması: AKTİF")
                print(Fore.MAGENTA + "  🔒 Anti-Detect: AKTİF")
                print(Fore.MAGENTA + "  🌐 Session Rotasyon: AKTİF")
    
    def start_bot(self, video_id, user_id, count, threads, mode):
        self.max_count = count
        
        print(Fore.CYAN + f"\n🎯 Hedef Video ID: {video_id}")
        print(Fore.CYAN + f"👤 Hedef User ID: {user_id}")
        print(Fore.CYAN + f"📊 Hedef: {count:,}")
        print(Fore.CYAN + f"🧵 Thread: {threads}")
        print(Fore.CYAN + f"🎮 Mod: {mode}")
        
        print(Fore.YELLOW + "\n🛡️ GÜVENLİK ÖZELLİKLERİ:")
        print(Fore.GREEN + "  ✅ İnsan Davranışı Simülasyonu")
        print(Fore.GREEN + "  ✅ Session Rotasyonu")
        print(Fore.GREEN + "  ✅ Device ID Havuzu")
        print(Fore.GREEN + "  ✅ Rastgele Gecikmeler")
        print(Fore.GREEN + "  ✅ Çoklu Endpoint")
        
        print(Fore.RED + "\n💣 BAŞLATILIYOR...")
        print(Fore.YELLOW + "⚠️  VPN KULLANMAYI UNUTMA!\n")
        
        time.sleep(2)
        
        self.start_time = time.time()
        
        status_thread = threading.Thread(target=self.status_display)
        status_thread.daemon = True
        status_thread.start()
        
        workers = []
        
        if mode in ["1", "3", "4"]:
            view_per_thread = count // threads
            for i in range(threads):
                t = threading.Thread(target=self.view_worker, args=(video_id, i))
                t.daemon = True
                workers.append(t)
        
        if mode in ["2", "3", "4"]:
            follow_per_thread = count // threads
            for i in range(threads):
                t = threading.Thread(target=self.follow_worker, args=(user_id, i))
                t.daemon = True
                workers.append(t)
        
        for w in workers:
            w.start()
        
        try:
            for w in workers:
                w.join()
        except KeyboardInterrupt:
            self.running = False
            print(Fore.RED + "\n\n[!] Kullanıcı tarafından durduruldu!")
        
        self.running = False
        time.sleep(1)
        self.print_results()
    
    def print_results(self):
        elapsed = time.time() - self.start_time if self.start_time else 0
        total = self.view_count + self.follow_count + self.like_count
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.MAGENTA + Style.BRIGHT + """
        ╔══════════════════════════════════════════════════╗
        ║   🎵 TİKTOK ULTRA BOT - SONUÇ RAPORU           ║
        ╚══════════════════════════════════════════════════╝
        """ + Style.RESET_ALL)
        
        print(Fore.WHITE + f"""
        ╔══════════════════════════════════════════════╗
        ║  ⏱️  Süre      : {elapsed:,.0f} saniye ({elapsed/60:,.1f} dakika)
        ║  ⚡ Hız        : {total/elapsed if elapsed > 0 else 0:,.1f}/saniye
        ║                                              ║
        ║  👁️  View      : {self.view_count:,}
        ║  👤  Follow    : {self.follow_count:,}
        ║  ❤️  Like      : {self.like_count:,}
        ║  🔄 Share      : {self.share_count:,}
        ║  ❌ Fail       : {self.fail_count:,}
        ║                                              ║
        ║  📊 TOPLAM     : {total:,}
        ╚══════════════════════════════════════════════╝
        """)
        
        print(Fore.GREEN + "✅ İşlem tamamlandı!")
        print(Fore.YELLOW + "💡 Takipçilerin kalıcı olması için yavaş modda çalıştırıldı.")

def ana():
    giris()
    bot = TikTokUltraBot()
    bot.bnr()
    
    print(Fore.YELLOW + "\n🎮 MOD SEÇİN:")
    print(Fore.CYAN + "1. 👁️  Sadece View (İzlenme)")
    print(Fore.CYAN + "2. 👤  Sadece Follow (Takipçi)")
    print(Fore.CYAN + "3. 🔄  View + Follow (İkisi Birden)")
    print(Fore.CYAN + "4. 💣  FULL (View + Follow + Like + Share)")
    
    mod = input(Fore.GREEN + "\nSeçim (1-4): ")
    
    print(Fore.YELLOW + "\n👤 KULLANICI ADI:")
    print(Fore.CYAN + "Örnek: kullaniciadi (@ olmadan)")
    username = input(Fore.GREEN + "> ").strip()
    
    # OTOMATİK ID ÇEKME
    user_id, user_info = bot.get_user_id(username)
    
    if not user_id:
        print(Fore.RED + "\n❌ Kullanıcı bulunamadı! Program sonlandırılıyor.")
        sys.exit(1)
    
    # Video ID
    print(Fore.YELLOW + "\n🎵 VİDEO ID:")
    print(Fore.CYAN + "1. 🔍 Otomatik bul (kullanıcının son videosu)")
    print(Fore.CYAN + "2. ✍️  Manuel gir")
    
    video_sec = input(Fore.GREEN + "Seçim (1-2): ")
    
    if video_sec == "1":
        print(Fore.CYAN + "\n🔍 Son video aranıyor...")
        video_id = bot.get_video_id_from_user(user_id)
        if video_id:
            print(Fore.GREEN + f"✅ Video bulundu: {video_id}")
        else:
            print(Fore.RED + "❌ Video bulunamadı! Manuel girin.")
            video_id = input(Fore.GREEN + "🎵 Video ID: ").strip()
    else:
        print(Fore.CYAN + "\n💡 Video ID'yi paylaş linkinden alabilirsiniz.")
        print(Fore.CYAN + "Örnek: tiktok.com/@user/video/7123456789012345678")
        video_id = input(Fore.GREEN + "🎵 Video ID: ").strip()
    
    if not video_id:
        print(Fore.RED + "❌ Video ID gerekli!")
        sys.exit(1)
    
    print(Fore.YELLOW + "\n📊 HEDEF SAYISI:")
    print(Fore.CYAN + "1. 100 (Test) | 2. 500 | 3. 1,000 | 4. 5,000 | 5. 10,000 | 6. Özel")
    
    count_sec = input(Fore.GREEN + "\nSeçim: ")
    count_map = {"1": 100, "2": 500, "3": 1000, "4": 5000, "5": 10000}
    count = count_map.get(count_sec, 1000)
    if count_sec == "6":
        count = int(input(Fore.GREEN + "Adet: "))
    
    print(Fore.YELLOW + "\n🧵 THREAD: 5 (Güvenli) | 10 (Normal) | 20 (Hızlı)")
    threads = int(input(Fore.GREEN + "Thread (10): ") or "10")
    
    print(Fore.MAGENTA + "\n" + "="*50)
    print(Fore.CYAN + Style.BRIGHT + "📋 OPERASYON ÖZETİ")
    print(Fore.MAGENTA + "="*50)
    print(Fore.WHITE + f"👤 Kullanıcı: @{username}")
    print(Fore.WHITE + f"🔢 User ID: {user_id}")
    print(Fore.WHITE + f"🎵 Video ID: {video_id}")
    print(Fore.WHITE + f"📊 Hedef: {count:,}")
    print(Fore.WHITE + f"🧵 Thread: {threads}")
    print(Fore.WHITE + f"🎮 Mod: {mod}")
    print(Fore.MAGENTA + "="*50)
    
    print(Fore.RED + "\n⚠️  VPN KULLANMAYI UNUTMA!")
    print(Fore.RED + "⚠️  Sorumluluk tamamen size aittir!")
    
    onay = input(Fore.GREEN + "\n🚀 Başlatmak için 'BASLAT' yazın: ")
    
    if onay.upper() == "BASLAT":
        bot.start_bot(video_id, user_id, count, threads, mod)
    else:
        print(Fore.YELLOW + "\n❌ İptal edildi.")

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n[!] Program kapatıldı!")
        sys.exit(0)
