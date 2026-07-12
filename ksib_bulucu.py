#!/usr/bin/env python3
# KSIB OSINT v3.0 - Email | Numara | Kullanıcı Adı | Data Leaks
import requests, threading, time, sys, os, json, re, random, hashlib, base64
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

class MegaOSINT:
    def __init__(self):
        self.ua = UserAgent()
        self.bulunan = []
        self.bulunmayan = []
        self.leaks = []
        self.session = requests.Session()
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + Style.BRIGHT + """
        ╔══════════════════════════════════════════╗
        ║   🔍 KSIB OSINT v3.0 MEGA ULTRA        ║
        ║  📧 Email | 📱 Numara | 👤 Kullanıcı    ║
        ║  🩸 Data Leaks | 🌐 50+ Site           ║
        ╚══════════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def baslik(self, text):
        print(Fore.YELLOW + f"\n{'='*60}")
        print(Fore.CYAN + Style.BRIGHT + f"  {text}")
        print(Fore.YELLOW + f"{'='*60}\n")
    
    def request(self, url, method='get', data=None, json_data=None, headers=None, timeout=10):
        try:
            h = {"User-Agent": self.ua.random, "Accept": "*/*", "Accept-Language": "en-US,en;q=0.9"}
            if headers: h.update(headers)
            
            if method == 'post':
                if json_data:
                    h["Content-Type"] = "application/json"
                    r = requests.post(url, json=json_data, headers=h, timeout=timeout, verify=False)
                else:
                    r = requests.post(url, data=data, headers=h, timeout=timeout, verify=False)
            else:
                r = requests.get(url, headers=h, timeout=timeout, verify=False)
            return r
        except:
            return None
    
    # ==================== DATA LEAKS ====================
    
    def check_leaks_email(self, email):
        self.leaks = []
        print(Fore.RED + "\n  🩸 DATA LEAK KONTROLÜ (Veri İhlalleri):")
        
        # HaveIBeenPwned
        try:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            headers = {"hibp-api-key": "0", "User-Agent": "KSIB-OSINT"}
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                for breach in r.json():
                    self.leaks.append({
                        "kaynak": "HIBP",
                        "site": breach.get("Name", "?"),
                        "tarih": breach.get("BreachDate", "?"),
                        "veri": ", ".join(breach.get("DataClasses", []))[:100],
                        "aciklama": breach.get("Description", "")[:150]
                    })
                print(Fore.GREEN + f"  ✅ HaveIBeenPwned: {len(r.json())} ihlal bulundu!")
            elif r.status_code == 404:
                print(Fore.GREEN + "  ✅ HaveIBeenPwned: İhlal bulunamadı (iyi!)")
        except:
            print(Fore.RED + "  ❌ HaveIBeenPwned: Erişilemedi")
        
        # LeakCheck
        try:
            url = f"https://leakcheck.io/api/public?check={email}"
            r = requests.get(url, headers={"User-Agent": self.ua.random}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get("success") and data.get("sources"):
                    for source in data["sources"]:
                        self.leaks.append({
                            "kaynak": "LeakCheck",
                            "site": source.get("name", "?"),
                            "tarih": source.get("date", "?"),
                            "veri": f"{source.get('lines', '?')} kayıt",
                            "aciklama": ""
                        })
                    print(Fore.GREEN + f"  ✅ LeakCheck: {len(data['sources'])} kaynak bulundu!")
        except:
            pass
        
        # FireFox Monitor
        try:
            url = f"https://monitor.firefox.com/api/v1/scan"
            data = {"email": email}
            r = requests.post(url, json=data, headers={"User-Agent": self.ua.random}, timeout=10)
            if r.status_code == 200:
                breaches = r.json().get("breaches", [])
                for breach in breaches:
                    self.leaks.append({
                        "kaynak": "Firefox Monitor",
                        "site": breach.get("Name", "?"),
                        "tarih": breach.get("BreachDate", "?"),
                        "veri": ", ".join(breach.get("DataClasses", []))[:100],
                        "aciklama": breach.get("Description", "")[:150]
                    })
                if breaches:
                    print(Fore.GREEN + f"  ✅ Firefox Monitor: {len(breaches)} ihlal bulundu!")
        except:
            pass
        
        # SnusBase
        try:
            url = f"https://snusbase.com/api/v1/search"
            headers = {"Auth": "free", "Content-Type": "application/json"}
            data = {"terms": [email], "types": ["email"]}
            r = requests.post(url, json=data, headers=headers, timeout=15)
            if r.status_code == 200 and r.json().get("results"):
                for result in r.json()["results"].get(email, [])[:5]:
                    self.leaks.append({
                        "kaynak": "SnusBase",
                        "site": result.get("database", "?"),
                        "tarih": "?",
                        "veri": str(result)[:100],
                        "aciklama": ""
                    })
                print(Fore.GREEN + f"  ✅ SnusBase: Sonuç bulundu!")
        except:
            pass
        
        # PwnedOrNot
        try:
            url = f"https://pwnedornot.com/api/check"
            data = {"email": email}
            r = requests.post(url, json=data, headers={"User-Agent": self.ua.random}, timeout=10)
            if r.status_code == 200 and r.json().get("breaches"):
                for breach in r.json()["breaches"]:
                    self.leaks.append({
                        "kaynak": "PwnedOrNot",
                        "site": breach.get("name", "?"),
                        "tarih": breach.get("date", "?"),
                        "veri": breach.get("data", "")[:100],
                        "aciklama": ""
                    })
                print(Fore.GREEN + f"  ✅ PwnedOrNot: Sonuç bulundu!")
        except:
            pass
        
        # Sonuçları göster
        if self.leaks:
            print(Fore.RED + f"\n  ⚠️  BU EMAİL {len(self.leaks)} VERİ İHLALİNDE BULUNDU!")
            print(Fore.RED + "  🔴 ŞİFRENİZİ HEMEN DEĞİŞTİRİN!\n")
            for i, leak in enumerate(self.leaks[:15], 1):
                print(Fore.YELLOW + f"  [{i}] {leak['site']} ({leak['kaynak']})")
                print(Fore.WHITE + f"      📅 Tarih: {leak['tarih']}")
                print(Fore.WHITE + f"      📋 Sızan Veri: {leak['veri']}")
                if leak['aciklama']:
                    print(Fore.WHITE + f"      📝 {leak['aciklama'][:100]}")
        else:
            print(Fore.GREEN + "\n  ✅ Hiçbir veri ihlalinde bulunamadı!")
    
    def check_leaks_phone(self, phone):
        self.leaks = []
        print(Fore.RED + "\n  🩸 DATA LEAK KONTROLÜ:")
        
        # SnusBase - telefon için
        try:
            url = f"https://snusbase.com/api/v1/search"
            headers = {"Auth": "free", "Content-Type": "application/json"}
            data = {"terms": [phone], "types": ["phone"]}
            r = requests.post(url, json=data, headers=headers, timeout=15)
            if r.status_code == 200 and r.json().get("results"):
                for result in r.json()["results"].get(phone, [])[:5]:
                    self.leaks.append({
                        "kaynak": "SnusBase",
                        "site": result.get("database", "?"),
                        "tarih": "?",
                        "veri": str(result)[:100]
                    })
                print(Fore.GREEN + f"  ✅ SnusBase: {len(self.leaks)} sonuç bulundu!")
        except:
            pass
        
        # DeHashed
        try:
            url = f"https://api.dehashed.com/search?query=phone:{phone}"
            r = requests.get(url, headers={"Accept": "application/json", "User-Agent": self.ua.random}, timeout=10)
            if r.status_code == 200:
                entries = r.json().get("entries", [])
                for entry in entries[:5]:
                    self.leaks.append({
                        "kaynak": "DeHashed",
                        "site": entry.get("database_name", "?"),
                        "tarih": entry.get("id", "?")[:10],
                        "veri": f"Email: {entry.get('email', '?')}, Name: {entry.get('name', '?')}"
                    })
                if entries:
                    print(Fore.GREEN + f"  ✅ DeHashed: {len(entries)} sonuç bulundu!")
        except:
            pass
        
        if self.leaks:
            print(Fore.RED + f"\n  ⚠️  BU NUMARA {len(self.leaks)} VERİ İHLALİNDE BULUNDU!\n")
            for i, leak in enumerate(self.leaks[:10], 1):
                print(Fore.YELLOW + f"  [{i}] {leak['site']} ({leak['kaynak']})")
                print(Fore.WHITE + f"      📅 Tarih: {leak['tarih']}")
                print(Fore.WHITE + f"      📋 Sızan Veri: {leak['veri']}")
        else:
            print(Fore.GREEN + "\n  ✅ Veri ihlali bulunamadı!")
    
    # ==================== EMAİL TARAMA ====================
    
    def email_tara(self, email):
        self.baslik(f"📧 EMAİL TARAMA: {email}")
        self.bulunan = []
        self.bulunmayan = []
        
        # Data leaks kontrolü
        self.check_leaks_email(email)
        
        # Email format kontrolü
        if '@' in email:
            kullanici, domain = email.split('@')
            print(Fore.CYAN + f"\n  📋 EMAİL ANALİZİ:")
            print(Fore.WHITE + f"  👤 Kullanıcı: {kullanici}")
            print(Fore.WHITE + f"  🌐 Domain: {domain}")
            
            domain_info = {
                'gmail.com': '🔵 Google - YouTube, Drive, Photos, Android',
                'hotmail.com': '🟢 Microsoft - Skype, Xbox, Office, Windows',
                'outlook.com': '🟢 Microsoft - Skype, Xbox, Office, Windows',
                'live.com': '🟢 Microsoft - Skype, Xbox, Office',
                'yahoo.com': '🟣 Yahoo - Flickr, Tumblr',
                'icloud.com': '⚪ Apple - iMessage, FaceTime, iCloud',
                'me.com': '⚪ Apple - iMessage, FaceTime, iCloud',
                'protonmail.com': '🟡 ProtonMail - Şifreli email, VPN',
                'proton.me': '🟡 Proton - Şifreli servisler',
                'tutanota.com': '🟢 Tutanota - Şifreli email',
                'yandex.com': '🔴 Yandex - Rusya, Yandex Disk',
                'yandex.ru': '🔴 Yandex - Rusya',
                'mail.ru': '🔴 Mail.ru - Rusya, VK',
                'bk.ru': '🔴 Mail.ru - Rusya',
                'inbox.ru': '🔴 Mail.ru - Rusya',
                'list.ru': '🔴 Mail.ru - Rusya',
            }
            
            if domain in domain_info:
                print(Fore.YELLOW + f"  💡 {domain_info[domain]}")
            
            # Domain yaşı kontrolü
            print(Fore.CYAN + f"\n  🔍 GÜVENLİK ANALİZİ:")
            if any(x in domain for x in ['temp', 'fake', 'throwaway', 'disposable', '10minute', 'guerrillamail']):
                print(Fore.RED + "  ⚠️  Geçici/tek kullanımlık email!")
            elif domain in ['gmail.com', 'outlook.com', 'yahoo.com', 'icloud.com', 'protonmail.com']:
                print(Fore.GREEN + "  ✅ Güvenilir email sağlayıcısı")
        
        # Sosyal Medya Taraması
        print(Fore.CYAN + f"\n  📱 SOSYAL MEDYA TARAMASI:")
        
        siteler = {
            # Sosyal Medya
            "Instagram": {
                "url": "https://www.instagram.com/api/v1/accounts/send_password_reset/",
                "method": "post", "data": {"user_email": email},
                "check": lambda r: r.status_code == 200 and ("obfuscated" in r.text or "sent" in r.text.lower())
            },
            "Facebook": {
                "url": f"https://www.facebook.com/login/identify/?ctx=recover&email={email}",
                "check": lambda r: r.status_code == 200 and "password" in r.text.lower() and "no_account" not in r.text.lower()
            },
            "Twitter/X": {
                "url": "https://api.twitter.com/i/users/email_available.json",
                "method": "post", "data": {"email": email},
                "check": lambda r: r.status_code == 200 and r.json().get("valid") == False
            },
            "TikTok": {
                "url": "https://www.tiktok.com/passport/email/available/",
                "method": "post", "json": {"email": email},
                "check": lambda r: r.status_code == 200 and "registered" in r.text.lower()
            },
            "Snapchat": {
                "url": "https://accounts.snapchat.com/accounts/get_username",
                "method": "post", "json": {"email": email},
                "check": lambda r: r.status_code == 200 and "username" in r.text.lower()
            },
            "LinkedIn": {
                "url": "https://www.linkedin.com/uas/request-password-reset",
                "method": "post", "data": {"session_key": email},
                "check": lambda r: r.status_code == 200 and "reset" in r.text.lower()
            },
            "Reddit": {
                "url": "https://www.reddit.com/api/check_email.json",
                "method": "post", "data": {"email": email},
                "check": lambda r: r.status_code == 200
            },
            "Pinterest": {
                "url": f"https://www.pinterest.com/resource/EmailExistsResource/get/?data=%7B%22options%22%3A%7B%22email%22%3A%22{email}%22%7D%7D",
                "check": lambda r: r.status_code == 200
            },
            
            # Teknoloji
            "GitHub": {
                "url": "https://github.com/signup_check/email",
                "method": "post", "data": {"value": email},
                "check": lambda r: r.status_code == 200 and "already" in r.text.lower()
            },
            "GitLab": {
                "url": "https://gitlab.com/users/sign_in",
                "check": lambda r: r.status_code == 200
            },
            "Spotify": {
                "url": "https://www.spotify.com/api/signup/validate",
                "method": "post", "json": {"email": email},
                "check": lambda r: r.status_code == 200 and "already" in r.text.lower()
            },
            "Steam": {
                "url": "https://store.steampowered.com/join/checkemail/",
                "method": "post", "data": {"email": email},
                "check": lambda r: r.status_code == 200
            },
            "Discord": {
                "url": "https://discord.com/api/v9/auth/register",
                "method": "post", "json": {"email": email, "username": "test123", "password": "Test123!"},
                "check": lambda r: r.status_code in [200, 400] and "email" in r.text.lower()
            },
            "Adobe": {
                "url": f"https://auth.services.adobe.com/signup/v1/users/email?email={email}",
                "check": lambda r: r.status_code == 200
            },
            
            # Alışveriş
            "Amazon": {
                "url": f"https://www.amazon.com/ap/forgotpassword?email={email}",
                "check": lambda r: r.status_code == 200 and "password" in r.text.lower()
            },
            "eBay": {
                "url": f"https://signin.ebay.com/ws/eBayISAPI.dll?co_partnerId=2&siteid=0&pageType=4&email={email}",
                "check": lambda r: r.status_code == 200
            },
            "Etsy": {
                "url": "https://www.etsy.com/signin/email",
                "method": "post", "data": {"email": email},
                "check": lambda r: r.status_code == 200
            },
            "Netflix": {
                "url": "https://www.netflix.com/tr/LoginHelp",
                "method": "post", "data": {"email": email},
                "check": lambda r: r.status_code == 200
            },
        }
        
        for site, config in siteler.items():
            try:
                if config.get("method") == "post":
                    if "json" in config:
                        r = self.request(config["url"], method="post", json_data=config["json"])
                    else:
                        r = self.request(config["url"], method="post", data=config.get("data"))
                else:
                    r = self.request(config["url"])
                
                if r and config["check"](r):
                    self.bulunan.append(site)
                    print(Fore.GREEN + f"  ✅ {site}")
                else:
                    print(Fore.RED + f"  ❌ {site}")
            except:
                print(Fore.RED + f"  ❌ {site}")
            time.sleep(0.05)
        
        print(Fore.CYAN + f"\n  📊 EMAİL SONUCU:")
        print(Fore.GREEN + f"  ✅ {len(self.bulunan)} platformda KAYITLI")
        if self.bulunan:
            print(Fore.YELLOW + "  🎯 KAYITLI PLATFORMLAR:")
            for s in self.bulunan:
                print(Fore.GREEN + f"  • {s}")
    
    # ==================== NUMARA TARAMA ====================
    
    def numara_tara(self, phone):
        self.baslik(f"📱 NUMARA TARAMA: +{phone}")
        self.bulunan = []
        
        # Operatör
        if phone.startswith('90') and len(phone) == 12:
            op = phone[2:5]
            print(Fore.CYAN + "  📡 OPERATÖR:")
            if op[:2] == '53': print(Fore.YELLOW + "  📞 Turkcell")
            elif op[:2] == '54': print(Fore.YELLOW + "  📞 Vodafone")
            elif op[:2] == '55': print(Fore.YELLOW + "  📞 Türk Telekom")
            
            # Bölge tahmini
            print(Fore.CYAN + "  📍 BÖLGE:")
            bolge_kodlari = {
                '530': 'İstanbul (Avrupa)', '532': 'İstanbul (Anadolu)', '533': 'Ankara',
                '535': 'İzmir', '536': 'Bursa', '537': 'Antalya', '538': 'Adana',
                '540': 'İstanbul', '541': 'Ankara', '542': 'İzmir',
                '550': 'İstanbul', '551': 'Ankara', '552': 'İzmir'
            }
            print(Fore.WHITE + f"  🗺️  {bolge_kodlari.get(op, 'Mobil numara')}")
        
        # Data leaks
        self.check_leaks_phone(phone)
        
        # Mesajlaşma & Sosyal Medya
        print(Fore.CYAN + f"\n  📱 MESAJLAŞMA & SOSYAL MEDYA:")
        
        # WhatsApp
        try:
            r = self.request(f"https://wa.me/{phone}")
            if r and "whatsapp" in r.text.lower():
                self.bulunan.append("WhatsApp")
                print(Fore.GREEN + "  ✅ WhatsApp")
            else:
                print(Fore.RED + "  ❌ WhatsApp")
        except: print(Fore.RED + "  ❌ WhatsApp")
        
        # Telegram
        try:
            r = self.request(f"https://t.me/+{phone}")
            if r and r.status_code == 200 and "tgme" in r.text.lower():
                self.bulunan.append("Telegram")
                print(Fore.GREEN + "  ✅ Telegram")
            else:
                print(Fore.RED + "  ❌ Telegram")
        except: print(Fore.RED + "  ❌ Telegram")
        
        # Instagram
        try:
            r = self.request("https://www.instagram.com/api/v1/accounts/send_password_reset/",
                           method="post", data={"phone_number": phone})
            if r and r.status_code == 200 and ("obfuscated" in r.text or "sent" in r.text.lower()):
                self.bulunan.append("Instagram")
                print(Fore.GREEN + "  ✅ Instagram")
            else:
                print(Fore.RED + "  ❌ Instagram")
        except: print(Fore.RED + "  ❌ Instagram")
        
        # Facebook
        try:
            r = self.request(f"https://www.facebook.com/login/identify/?ctx=recover&phone={phone}")
            if r and "password" in r.text.lower() and "no_account" not in r.text.lower():
                self.bulunan.append("Facebook")
                print(Fore.GREEN + "  ✅ Facebook")
            else:
                print(Fore.RED + "  ❌ Facebook")
        except: print(Fore.RED + "  ❌ Facebook")
        
        # Twitter
        try:
            r = self.request("https://api.twitter.com/i/users/phone_available.json",
                           method="post", data={"phone_number": phone})
            if r and r.status_code == 200:
                data = r.json()
                if data.get("valid") == False:
                    self.bulunan.append("Twitter/X")
                    print(Fore.GREEN + "  ✅ Twitter/X")
                else:
                    print(Fore.RED + "  ❌ Twitter/X")
            else:
                print(Fore.RED + "  ❌ Twitter/X")
        except: print(Fore.RED + "  ❌ Twitter/X")
        
        # TikTok
        try:
            r = self.request("https://www.tiktok.com/passport/account/send_code/",
                           method="post", json_data={"mobile": phone, "type": "1"})
            if r and r.status_code == 200:
                self.bulunan.append("TikTok")
                print(Fore.GREEN + "  ✅ TikTok")
            else:
                print(Fore.RED + "  ❌ TikTok")
        except: print(Fore.RED + "  ❌ TikTok")
        
        # Google
        try:
            r = self.request(f"https://accounts.google.com/signup/v2/webcreateaccount?phone={phone}")
            if r and r.status_code == 200 and "exists" in r.text.lower():
                self.bulunan.append("Google")
                print(Fore.GREEN + "  ✅ Google")
            else:
                print(Fore.RED + "  ❌ Google")
        except: print(Fore.RED + "  ❌ Google")
        
        # Snapchat
        try:
            r = self.request("https://accounts.snapchat.com/accounts/get_username",
                           method="post", json_data={"phone_number": phone})
            if r and r.status_code == 200 and "username" in r.text.lower():
                self.bulunan.append("Snapchat")
                print(Fore.GREEN + "  ✅ Snapchat")
            else:
                print(Fore.RED + "  ❌ Snapchat")
        except: print(Fore.RED + "  ❌ Snapchat")
        
        # Tinder
        try:
            r = self.request("https://api.tinder.com/v2/auth/send-code",
                           method="post", json_data={"phone_number": phone})
            if r and r.status_code in [200, 201]:
                self.bulunan.append("Tinder")
                print(Fore.GREEN + "  ✅ Tinder")
            else:
                print(Fore.RED + "  ❌ Tinder")
        except: print(Fore.RED + "  ❌ Tinder")
        
        print(Fore.CYAN + f"\n  📊 NUMARA SONUCU:")
        print(Fore.GREEN + f"  ✅ {len(self.bulunan)} platformda KAYITLI")
        if self.bulunan:
            print(Fore.YELLOW + "  🎯 KAYITLI PLATFORMLAR:")
            for s in self.bulunan:
                print(Fore.GREEN + f"  • {s}")
    
    # ==================== KULLANICI ADI TARAMA ====================
    
    def sherlock_tara(self, username):
        self.baslik(f"👤 KULLANICI ADI TARAMA: @{username}")
        self.bulunan = []
        
        platformlar = {
            "Instagram": f"https://www.instagram.com/{username}/",
            "Twitter/X": f"https://x.com/{username}",
            "Facebook": f"https://www.facebook.com/{username}",
            "TikTok": f"https://www.tiktok.com/@{username}",
            "YouTube": f"https://www.youtube.com/@{username}",
            "Reddit": f"https://www.reddit.com/user/{username}",
            "LinkedIn": f"https://www.linkedin.com/in/{username}",
            "Pinterest": f"https://www.pinterest.com/{username}/",
            "Snapchat": f"https://www.snapchat.com/add/{username}",
            "Telegram": f"https://t.me/{username}",
            "GitHub": f"https://github.com/{username}",
            "GitLab": f"https://gitlab.com/{username}",
            "BitBucket": f"https://bitbucket.org/{username}/",
            "Stack Overflow": f"https://stackoverflow.com/users/{username}",
            "Medium": f"https://medium.com/@{username}",
            "Twitch": f"https://www.twitch.tv/{username}",
            "Steam": f"https://steamcommunity.com/id/{username}",
            "Spotify": f"https://open.spotify.com/user/{username}",
            "SoundCloud": f"https://soundcloud.com/{username}",
            "DeviantArt": f"https://www.deviantart.com/{username}",
            "Flickr": f"https://www.flickr.com/people/{username}",
            "Dribbble": f"https://dribbble.com/{username}",
            "Behance": f"https://www.behance.net/{username}",
            "Patreon": f"https://www.patreon.com/{username}",
            "OnlyFans": f"https://onlyfans.com/{username}",
            "CashApp": f"https://cash.app/${username}",
            "PayPal": f"https://www.paypal.com/paypalme/{username}",
            "Etsy": f"https://www.etsy.com/people/{username}",
            "Vimeo": f"https://vimeo.com/{username}",
            "Quora": f"https://www.quora.com/profile/{username}",
            "WordPress": f"https://{username}.wordpress.com",
            "Blogger": f"https://{username}.blogspot.com",
            "Roblox": f"https://www.roblox.com/user.aspx?username={username}",
        }
        
        print(Fore.WHITE + "  Taranıyor...\n")
        
        for site, url in platformlar.items():
            try:
                r = self.request(url)
                if not r: continue
                
                text = r.text.lower()
                bulundu = False
                
                if site == "Instagram":
                    bulundu = '"followers_count"' in text or '"biography"' in text
                elif site == "Twitter/X":
                    bulundu = 'profile' in text and 'this account doesn' not in text and 'suspended' not in text
                elif site == "GitHub":
                    bulundu = 'repositories' in text and 'not found' not in text and 'page not found' not in text
                elif site == "Reddit":
                    bulundu = 'karma' in text or 'overview' in text
                elif site == "TikTok":
                    bulundu = 'user_id' in text or 'uniqueId' in text
                elif site == "YouTube":
                    bulundu = 'subscriber' in text or 'videos' in text
                elif site == "Steam":
                    bulundu = 'profile' in text and 'not found' not in text
                elif site == "Spotify":
                    bulundu = 'display_name' in text or 'followers' in text
                else:
                    bulundu = r.status_code == 200 and 'not found' not in text and 'doesn\'t exist' not in text and 'page not found' not in text
                
                if bulundu:
                    self.bulunan.append((site, url))
                    print(Fore.GREEN + f"  ✅ {site:<20s} → {url}")
                
            except:
                pass
            time.sleep(0.05)
        
        print(Fore.CYAN + f"\n  📊 SONUÇ:")
        print(Fore.GREEN + f"  ✅ {len(self.bulunan)} platformda BULUNDU")
        if self.bulunan:
            print(Fore.YELLOW + "\n  🎯 BULUNAN HESAPLAR:")
            for site, url in self.bulunan:
                print(Fore.GREEN + f"  • {site}: {url}")
        
        # Benzer öneriler
        print(Fore.CYAN + f"\n  💡 BENZER KULLANICI ADLARI:")
        for v in [f"{username}1", f"{username}_", f"_{username}", f"{username}official", f"the{username}", f"{username}real", f"x{username}", f"{username}x"]:
            print(Fore.WHITE + f"  • {v}")

def ana():
    giris()
    o = MegaOSINT()
    o.bnr()
    
    while True:
        print(Fore.YELLOW + "\n🔍 MEGA MENÜ:")
        print("1. 📧 Email Tara (30+ Site + Data Leaks)")
        print("2. 📱 Numara Tara (15+ Site + Data Leaks)")
        print("3. 👤 Kullanıcı Adı Tara (30+ Site)")
        print("4. 🚪 Çıkış")
        
        sec = input(Fore.GREEN + "\nSeçim: ")
        
        if sec == "1":
            email = input(Fore.GREEN + "📧 Email: ").strip()
            if '@' in email:
                o.email_tara(email)
            else:
                print(Fore.RED + "❌ Geçerli email gir!")
            input(Fore.YELLOW + "\nDevam için Enter...")
            o.bnr()
            
        elif sec == "2":
            phone = input(Fore.GREEN + "📱 Numara (5XXXXXXXXX): ").strip()
            phone = '90' + ''.join(filter(str.isdigit, phone))
            if phone.startswith('900'): phone = '90' + phone[3:]
            if len(phone) >= 12:
                o.numara_tara(phone)
            else:
                print(Fore.RED + "❌ Geçerli numara gir!")
            input(Fore.YELLOW + "\nDevam için Enter...")
            o.bnr()
            
        elif sec == "3":
            username = input(Fore.GREEN + "👤 Kullanıcı adı (@ olmadan): ").strip()
            if username:
                o.sherlock_tara(username)
            else:
                print(Fore.RED + "❌ Kullanıcı adı gir!")
            input(Fore.YELLOW + "\nDevam için Enter...")
            o.bnr()
            
        elif sec == "4":
            print(Fore.GREEN + "\n👋 Görüşürüz!")
            break

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Çıkış!")
        sys.exit(0)
