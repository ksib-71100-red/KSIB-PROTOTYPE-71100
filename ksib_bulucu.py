#!/usr/bin/env python3
# KSIB OSINT v4.0 FINAL - 80+ Site | Discord Fix | Doğrulama Sistemi
import requests, threading, time, sys, os, json, re, random, hashlib
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
        ║   🔍 KSIB OSINT v4.0 FINAL ULTRA       ║
        ║  📧 Email | 📱 Numara | 👤 Kullanıcı    ║
        ║  🩸 Data Leaks | ✅ Doğrulama           ║
        ║  🌐 80+ Site | Discord Fix              ║
        ╚══════════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def baslik(self, text):
        print(Fore.YELLOW + f"\n{'='*60}")
        print(Fore.CYAN + Style.BRIGHT + f"  {text}")
        print(Fore.YELLOW + f"{'='*60}\n")
    
    def request(self, url, method='get', data=None, json_data=None, headers=None, timeout=10, allow_redirects=True):
        try:
            h = {
                "User-Agent": self.ua.random,
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }
            if headers: h.update(headers)
            
            if method == 'post':
                if json_data:
                    h["Content-Type"] = "application/json"
                    r = requests.post(url, json=json_data, headers=h, timeout=timeout, verify=False, allow_redirects=allow_redirects)
                else:
                    r = requests.post(url, data=data, headers=h, timeout=timeout, verify=False, allow_redirects=allow_redirects)
            else:
                r = requests.get(url, headers=h, timeout=timeout, verify=False, allow_redirects=allow_redirects)
            return r
        except:
            return None
    
    # ==================== DATA LEAKS ====================
    
    def check_leaks(self, query, query_type="email"):
        self.leaks = []
        print(Fore.RED + "\n  🩸 DATA LEAK KONTROLÜ (Veri İhlalleri):")
        print(Fore.WHITE + "  HaveIBeenPwned | LeakCheck | SnusBase | Firefox Monitor\n")
        
        # HaveIBeenPwned
        try:
            if query_type == "email":
                url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{query}"
            else:
                url = f"https://haveibeenpwned.com/api/v3/pasteaccount/{query}"
            
            headers = {"hibp-api-key": "0", "User-Agent": "KSIB-OSINT"}
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                if query_type == "email":
                    for breach in r.json():
                        self.leaks.append({
                            "kaynak": "HIBP", "site": breach.get("Name", "?"),
                            "tarih": breach.get("BreachDate", "?"),
                            "veri": ", ".join(breach.get("DataClasses", []))[:120]
                        })
                print(Fore.GREEN + f"  ✅ HaveIBeenPwned: {len(self.leaks)} ihlal bulundu!")
            elif r.status_code == 404:
                print(Fore.GREEN + "  ✅ HaveIBeenPwned: Temiz!")
        except: print(Fore.RED + "  ❌ HaveIBeenPwned: Erişilemedi")
        
        # LeakCheck
        try:
            url = f"https://leakcheck.io/api/public?check={query}"
            r = requests.get(url, headers={"User-Agent": self.ua.random}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get("success") and data.get("sources"):
                    for source in data["sources"]:
                        self.leaks.append({
                            "kaynak": "LeakCheck", "site": source.get("name", "?"),
                            "tarih": source.get("date", "?"), "veri": f"{source.get('lines', '?')} kayıt"
                        })
                    print(Fore.GREEN + f"  ✅ LeakCheck: {len(data['sources'])} kaynak bulundu!")
        except: pass
        
        # Sonuçları göster
        if self.leaks:
            print(Fore.RED + f"\n  ⚠️  {len(self.leaks)} VERİ İHLALİNDE BULUNDU!")
            print(Fore.RED + "  🔴 ŞİFRENİZİ HEMEN DEĞİŞTİRİN!\n")
            for i, leak in enumerate(self.leaks[:15], 1):
                print(Fore.YELLOW + f"  [{i}] {leak['site']}")
                print(Fore.WHITE + f"      📅 {leak['tarih']} | 📋 {leak['veri']}")
        else:
            print(Fore.GREEN + "\n  ✅ Hiçbir veri ihlalinde bulunamadı!")
    
    # ==================== EMAİL TARAMA (50+ Site) ====================
    
    def email_tara(self, email):
        self.baslik(f"📧 EMAİL TARAMA: {email}")
        self.bulunan = []
        
        # Data leaks
        self.check_leaks(email, "email")
        
        # Email analizi
        if '@' in email:
            kullanici, domain = email.split('@')
            print(Fore.CYAN + f"\n  📋 EMAİL ANALİZİ:")
            print(Fore.WHITE + f"  👤 {kullanici} @ 🌐 {domain}")
            
            info = {
                'gmail.com': '🔵 Google - YouTube, Drive, Photos, Android, Gmail',
                'hotmail.com': '🟢 Microsoft - Skype, Xbox, Office, Windows',
                'outlook.com': '🟢 Microsoft - Skype, Xbox, Office, Windows',
                'live.com': '🟢 Microsoft - Skype, Xbox, Office',
                'yahoo.com': '🟣 Yahoo - Flickr, Tumblr',
                'icloud.com': '⚪ Apple - iMessage, FaceTime, iCloud',
                'me.com': '⚪ Apple - iMessage, FaceTime',
                'protonmail.com': '🟡 Proton - Şifreli email, VPN',
                'proton.me': '🟡 Proton - Şifreli servisler',
                'yandex.com': '🔴 Yandex - Rusya',
                'mail.ru': '🔴 Mail.ru - Rusya, VK',
            }
            if domain in info: print(Fore.YELLOW + f"  💡 {info[domain]}")
        
        # TÜM SİTELER
        print(Fore.CYAN + f"\n  📱 SOSYAL MEDYA & MESAJLAŞMA:")
        
        siteler = {
            "Instagram": {
                "url": "https://www.instagram.com/api/v1/accounts/send_password_reset/",
                "method": "post", "data": {"user_email": email},
                "check": lambda r: r.status_code == 200 and ("obfuscated" in r.text or "sent" in r.text.lower())
            },
            "Facebook": {
                "url": f"https://www.facebook.com/login/identify/?ctx=recover&email={email}",
                "check": lambda r: r.status_code == 200 and "password" in r.text.lower() and "no_account" not in r.text.lower()
            },
            "Messenger": {
                "url": f"https://www.facebook.com/login/identify/?ctx=recover&email={email}",
                "check": lambda r: r.status_code == 200  # Messenger = Facebook hesabı
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
                "method": "post", "json": {"email": email, "requested_username": "test"},
                "check": lambda r: r.status_code == 200 and "username" in r.text.lower()
            },
            "LinkedIn": {
                "url": "https://www.linkedin.com/uas/request-password-reset",
                "method": "post", "data": {"session_key": email},
                "check": lambda r: r.status_code == 200
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
            "Tumblr": {
                "url": "https://www.tumblr.com/svc/account/register",
                "method": "post", "data": {"email": email, "action": "check_email"},
                "check": lambda r: r.status_code == 200 and "taken" in r.text.lower()
            },
            "Flickr": {
                "url": "https://identity.flickr.com/checkemail",
                "method": "post", "data": {"email": email},
                "check": lambda r: r.status_code == 200
            },
            "VK": {
                "url": "https://vk.com/rest/act/checkEmail",
                "method": "post", "data": {"email": email},
                "check": lambda r: r.status_code == 200
            },
            "Discord": {
                "url": "https://discord.com/api/v9/auth/register",
                "method": "post",
                "json": {"email": email, "username": "testuser" + str(random.randint(1000,9999)), "password": "Test123!@#", "consent": True},
                "check": lambda r: r.status_code == 400 and ("email" in r.text.lower() or "already" in r.text.lower())
            },
            "Telegram": {
                "url": "https://my.telegram.org/auth/send_password",
                "method": "post", "data": {"email": email},
                "check": lambda r: r.status_code == 200
            },
            "WhatsApp": {
                "url": f"https://wa.me/{email.split('@')[0] if '@' in email else email}",
                "check": lambda r: r.status_code == 200  # Zayıf kontrol
            },
            "Skype": {
                "url": f"https://login.skype.com/recovery?email={email}",
                "check": lambda r: r.status_code == 200
            },
            
            # Teknoloji
            "GitHub": {
                "url": "https://github.com/signup_check/email",
                "method": "post", "data": {"value": email},
                "check": lambda r: r.status_code == 200 and "already" in r.text.lower()
            },
            "GitLab": {
                "url": "https://gitlab.com/users/sign_up",
                "method": "post", "data": {"user[email]": email},
                "check": lambda r: r.status_code == 200
            },
            "BitBucket": {
                "url": "https://bitbucket.org/account/signup/",
                "method": "post", "data": {"email": email},
                "check": lambda r: r.status_code == 200
            },
            "Stack Overflow": {
                "url": "https://stackoverflow.com/users/signup",
                "method": "post", "data": {"email": email, "password": "test123"},
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
            "Adobe": {
                "url": f"https://auth.services.adobe.com/signup/v1/users/email?email={email}",
                "check": lambda r: r.status_code == 200
            },
            "Dropbox": {
                "url": f"https://www.dropbox.com/forgot?email={email}",
                "check": lambda r: r.status_code == 200 and "password" in r.text.lower()
            },
            "WordPress": {
                "url": f"https://public-api.wordpress.com/rest/v1.1/users/email/exists?email={email}",
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
            "Shopify": {
                "url": f"https://accounts.shopify.com/lookup?email={email}",
                "check": lambda r: r.status_code == 200
            },
            "Alibaba": {
                "url": "https://passport.alibaba.com/icbu/account/checkEmail.htm",
                "method": "post", "data": {"email": email},
                "check": lambda r: r.status_code == 200
            },
            "Walmart": {
                "url": f"https://www.walmart.com/account/forgotpassword?email={email}",
                "check": lambda r: r.status_code == 200
            },
            "Nike": {
                "url": f"https://www.nike.com/forgotpassword?email={email}",
                "check": lambda r: r.status_code == 200
            },
            
            # Eğlence
            "Netflix": {
                "url": "https://www.netflix.com/tr/LoginHelp",
                "method": "post", "data": {"email": email},
                "check": lambda r: r.status_code == 200
            },
            "Hulu": {
                "url": f"https://auth.hulu.com/account/forgotpassword?email={email}",
                "check": lambda r: r.status_code == 200
            },
            "Disney+": {
                "url": f"https://www.disneyplus.com/forgotpassword?email={email}",
                "check": lambda r: r.status_code == 200
            },
            
            # Flört
            "Tinder": {
                "url": "https://api.gotinder.com/v2/auth/login/email",
                "method": "post", "data": {"email": email},
                "check": lambda r: r.status_code in [200, 400]
            },
            "Bumble": {
                "url": "https://bumble.com/api/auth/send-code",
                "method": "post", "data": {"email": email},
                "check": lambda r: r.status_code == 200
            },
            "Badoo": {
                "url": "https://badoo.com/api/auth/check-email",
                "method": "post", "data": {"email": email},
                "check": lambda r: r.status_code == 200
            },
            
            # Finans
            "PayPal": {
                "url": "https://www.paypal.com/authflow/entry",
                "method": "post", "data": {"email": email, "flowType": "forgot"},
                "check": lambda r: r.status_code == 200
            },
            "Venmo": {
                "url": f"https://venmo.com/account/forgotpassword?email={email}",
                "check": lambda r: r.status_code == 200
            },
            "Robinhood": {
                "url": "https://api.robinhood.com/user/check_email/",
                "method": "post", "data": {"email": email},
                "check": lambda r: r.status_code == 200
            },
            "Coinbase": {
                "url": f"https://www.coinbase.com/forgotpassword?email={email}",
                "check": lambda r: r.status_code == 200
            },
            
            # Seyahat
            "Airbnb": {
                "url": f"https://www.airbnb.com/forgot_password?email={email}",
                "check": lambda r: r.status_code == 200
            },
            "Uber": {
                "url": "https://auth.uber.com/v2/api/send-reset-password-email",
                "method": "post", "data": {"email": email},
                "check": lambda r: r.status_code in [200, 400]
            },
            "Booking.com": {
                "url": f"https://account.booking.com/sign-in?op=forgot_password&email={email}",
                "check": lambda r: r.status_code == 200
            },
            
            # İçerik
            "OnlyFans": {
                "url": "https://onlyfans.com/api2/v2/users/check_email",
                "method": "post", "data": {"email": email},
                "check": lambda r: r.status_code == 200
            },
            "Patreon": {
                "url": "https://www.patreon.com/api/auth/check_email",
                "method": "post", "data": {"email": email},
                "check": lambda r: r.status_code == 200
            },
            "Medium": {
                "url": f"https://medium.com/m/account/forgotpassword?email={email}",
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
            time.sleep(0.03)
        
        # Sonuç
        print(Fore.CYAN + f"\n  📊 SONUÇ:")
        print(Fore.GREEN + f"  ✅ {len(self.bulunan)} platformda KAYITLI")
        print(Fore.RED + f"  ❌ {len(siteler) - len(self.bulunan)} platformda KAYITSIZ")
        if self.bulunan:
            print(Fore.YELLOW + "\n  🎯 KAYITLI PLATFORMLAR:")
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
        
        # Data leaks
        self.check_leaks(phone, "phone")
        
        # Platformlar
        print(Fore.CYAN + f"\n  📱 PLATFORM TARAMASI:")
        
        platformlar = [
            ("WhatsApp", f"https://wa.me/{phone}", lambda r: r and "whatsapp" in r.text.lower()),
            ("Telegram", f"https://t.me/+{phone}", lambda r: r and r.status_code == 200 and "tgme" in r.text.lower()),
            ("Instagram", "https://www.instagram.com/api/v1/accounts/send_password_reset/", None),
            ("Facebook", f"https://www.facebook.com/login/identify/?ctx=recover&phone={phone}", None),
            ("Messenger", f"https://www.facebook.com/login/identify/?ctx=recover&phone={phone}", None),  # Messenger = Facebook
            ("Twitter/X", "https://api.twitter.com/i/users/phone_available.json", None),
            ("TikTok", "https://www.tiktok.com/passport/account/send_code/", None),
            ("Snapchat", "https://accounts.snapchat.com/accounts/get_username", None),
            ("Google", f"https://accounts.google.com/signup/v2/webcreateaccount?phone={phone}", None),
            ("LinkedIn", "https://www.linkedin.com/uas/request-password-reset", None),
            ("Tinder", "https://api.tinder.com/v2/auth/send-code", None),
            ("Uber", "https://auth.uber.com/v2/api/send-otp", None),
            ("Airbnb", "https://www.airbnb.com/api/v2/phone_verification", None),
        ]
        
        for site, url, check_func in platformlar:
            try:
                if "send_password_reset" in url and site == "Instagram":
                    r = self.request(url, method="post", data={"phone_number": phone})
                    durum = r and r.status_code == 200 and ("obfuscated" in r.text or "sent" in r.text.lower())
                elif "phone_available" in url:
                    r = self.request(url, method="post", data={"phone_number": phone})
                    durum = r and r.status_code == 200 and r.json().get("valid") == False
                elif "send_code" in url and site == "TikTok":
                    r = self.request(url, method="post", json_data={"mobile": phone, "type": "1"})
                    durum = r and r.status_code == 200
                elif "send-code" in url and site == "Tinder":
                    r = self.request(url, method="post", json_data={"phone_number": phone})
                    durum = r and r.status_code in [200, 201]
                elif "send-otp" in url and site == "Uber":
                    r = self.request(url, method="post", data={"phone": phone})
                    durum = r and r.status_code in [200, 400]
                elif site == "Snapchat":
                    r = self.request(url, method="post", json_data={"phone_number": phone})
                    durum = r and r.status_code == 200 and "username" in r.text.lower()
                elif site == "LinkedIn":
                    r = self.request(url, method="post", data={"session_key": phone})
                    durum = r and r.status_code == 200
                elif check_func:
                    r = self.request(url)
                    durum = check_func(r)
                else:
                    r = self.request(url)
                    durum = r and r.status_code == 200
                
                if durum:
                    self.bulunan.append(site)
                    print(Fore.GREEN + f"  ✅ {site}")
                else:
                    print(Fore.RED + f"  ❌ {site}")
            except:
                print(Fore.RED + f"  ❌ {site}")
            time.sleep(0.05)
        
        print(Fore.CYAN + f"\n  📊 SONUÇ:")
        print(Fore.GREEN + f"  ✅ {len(self.bulunan)} platformda KAYITLI")
        if self.bulunan:
            print(Fore.YELLOW + "\n  🎯 KAYITLI PLATFORMLAR:")
            for s in self.bulunan:
                print(Fore.GREEN + f"  • {s}")
    
    # ==================== KULLANICI ADI TARAMA (60+ Site) ====================
    
    def sherlock_tara(self, username):
        self.baslik(f"👤 KULLANICI ADI TARAMA: @{username}")
        self.bulunan = []
        
        platformlar = {
            # Sosyal Medya
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
            "Tumblr": f"https://{username}.tumblr.com",
            "Flickr": f"https://www.flickr.com/people/{username}",
            "VK": f"https://vk.com/{username}",
            
            # Kod/Yazılım
            "GitHub": f"https://github.com/{username}",
            "GitLab": f"https://gitlab.com/{username}",
            "BitBucket": f"https://bitbucket.org/{username}/",
            "Stack Overflow": f"https://stackoverflow.com/users/{username}",
            "Codecademy": f"https://www.codecademy.com/profiles/{username}",
            "Codepen": f"https://codepen.io/{username}",
            "HackerRank": f"https://www.hackerrank.com/{username}",
            "LeetCode": f"https://leetcode.com/{username}",
            "Replit": f"https://replit.com/@{username}",
            
            # Oyun
            "Steam": f"https://steamcommunity.com/id/{username}",
            "Twitch": f"https://www.twitch.tv/{username}",
            "Roblox": f"https://www.roblox.com/user.aspx?username={username}",
            "Discord": f"https://discord.com/users/{username}",
            
            # Müzik
            "Spotify": f"https://open.spotify.com/user/{username}",
            "SoundCloud": f"https://soundcloud.com/{username}",
            "Last.fm": f"https://www.last.fm/user/{username}",
            "Bandcamp": f"https://bandcamp.com/{username}",
            "Mixcloud": f"https://www.mixcloud.com/{username}/",
            
            # Sanat/Tasarım
            "DeviantArt": f"https://www.deviantart.com/{username}",
            "Behance": f"https://www.behance.net/{username}",
            "Dribbble": f"https://dribbble.com/{username}",
            
            # Blog/Yazı
            "Medium": f"https://medium.com/@{username}",
            "WordPress": f"https://{username}.wordpress.com",
            "Blogger": f"https://{username}.blogspot.com",
            "Quora": f"https://www.quora.com/profile/{username}",
            "Gravatar": f"https://gravatar.com/{username}",
            
            # Finans
            "Patreon": f"https://www.patreon.com/{username}",
            "OnlyFans": f"https://onlyfans.com/{username}",
            "BuyMeACoffee": f"https://www.buymeacoffee.com/{username}",
            "Ko-fi": f"https://ko-fi.com/{username}",
            "PayPal": f"https://www.paypal.com/paypalme/{username}",
            "CashApp": f"https://cash.app/${username}",
            
            # Diğer
            "Keybase": f"https://keybase.io/{username}",
            "About.me": f"https://about.me/{username}",
            "Linktree": f"https://linktr.ee/{username}",
            "Pastebin": f"https://pastebin.com/u/{username}",
            "ProductHunt": f"https://www.producthunt.com/@{username}",
            "SlideShare": f"https://www.slideshare.net/{username}",
            "Goodreads": f"https://www.goodreads.com/{username}",
            "Letterboxd": f"https://letterboxd.com/{username}/",
            "Etsy": f"https://www.etsy.com/people/{username}",
            "Vimeo": f"https://vimeo.com/{username}",
        }
        
        print(Fore.WHITE + f"  {len(platformlar)} platform taranıyor...\n")
        
        for site, url in platformlar.items():
            try:
                r = self.request(url, timeout=8)
                if not r: continue
                
                text = r.text.lower()
                final_url = r.url.lower()
                bulundu = False
                
                # Site-özel KESİN kontroller
                if site == "Instagram":
                    bulundu = '"followers_count"' in text or '"biography"' in text
                elif site == "Twitter/X":
                    bulundu = ('profile' in text and 'this account doesn' not in text and 
                              'suspended' not in text and 'doesn\'t exist' not in text)
                elif site == "GitHub":
                    bulundu = ('repositories' in text and 'not found' not in text and 
                              'page not found' not in text and 'this is not the web page you are looking for' not in text)
                elif site == "Reddit":
                    bulundu = ('karma' in text or 'overview' in text or 'subreddits' in text)
                elif site == "TikTok":
                    bulundu = '"user_id"' in text or '"uniqueId"' in text
                elif site == "YouTube":
                    bulundu = ('subscriber' in text or 'videos' in text or 'channel' in text)
                elif site == "Steam":
                    bulundu = ('profile' in text and 'not found' not in text and 
                              'the specified profile could not be found' not in text)
                elif site == "Spotify":
                    bulundu = '"display_name"' in text or 'followers' in text or 'playlists' in text
                elif site == "Discord":
                    bulundu = username in final_url and 'discord' in final_url
                elif site == "Telegram":
                    bulundu = 'tgme' in text or 'telegram' in text
                elif site == "Snapchat":
                    bulundu = 'snapchat' in text and username.lower() in text
                elif site == "LinkedIn":
                    bulundu = 'profile' in text and 'page not found' not in text
                elif site == "Medium":
                    bulundu = 'followers' in text or 'following' in text
                elif site == "Tumblr":
                    bulundu = username.lower() in final_url and r.status_code == 200
                elif site == "Pinterest":
                    bulundu = 'profile' in text and username.lower() in final_url
                elif site == "Roblox":
                    bulundu = 'profile' in text and 'not found' not in text
                elif site == "Twitch":
                    bulundu = 'stream' in text or 'offline' in text or 'channel' in text
                elif site == "WordPress":
                    bulundu = 'blog' in text and 'doesn\'t exist' not in text
                elif site == "Blogger":
                    bulundu = 'blog' in text and 'not found' not in text
                elif site == "OnlyFans":
                    bulundu = 'onlyfans' in text and username.lower() in final_url
                elif site == "Patreon":
                    bulundu = 'patron' in text and 'page not found' not in text
                elif site == "PayPal":
                    bulundu = username.lower() in final_url and 'paypal' in final_url
                elif site == "SoundCloud":
                    bulundu = 'tracks' in text or 'followers' in text or 'soundcloud' in text
                elif site == "DeviantArt":
                    bulundu = 'deviantart' in text and 'not found' not in text
                elif site == "Behance":
                    bulundu = 'behance' in text and username.lower() in final_url
                elif site == "Dribbble":
                    bulundu = 'dribbble' in text and username.lower() in final_url
                elif site == "GitLab":
                    bulundu = 'gitlab' in text and username.lower() in final_url
                elif site == "Keybase":
                    bulundu = 'keybase' in text and username.lower() in final_url
                elif site == "Gravatar":
                    bulundu = 'gravatar' in text and r.status_code == 200
                elif site == "Pastebin":
                    bulundu = 'pastebin' in text and 'not found' not in text
                elif site == "ProductHunt":
                    bulundu = 'producthunt' in text and username.lower() in final_url
                elif site == "Goodreads":
                    bulundu = 'goodreads' in text and 'profile' in text
                elif site == "Letterboxd":
                    bulundu = 'letterboxd' in text and username.lower() in final_url
                elif site == "Etsy":
                    bulundu = 'etsy' in text and username.lower() in final_url
                elif site == "Vimeo":
                    bulundu = 'vimeo' in text and username.lower() in final_url
                elif site == "Linktree":
                    bulundu = 'linktree' in text and username.lower() in final_url
                elif site == "BuyMeACoffee":
                    bulundu = 'buymeacoffee' in text and username.lower() in final_url
                elif site == "Ko-fi":
                    bulundu = 'ko-fi' in text and username.lower() in final_url
                elif site == "CashApp":
                    bulundu = 'cash' in text and username.lower() in final_url
                elif site == "About.me":
                    bulundu = 'about.me' in text and username.lower() in final_url
                elif site == "SlideShare":
                    bulundu = 'slideshare' in text and username.lower() in final_url
                elif site == "Codecademy":
                    bulundu = 'codecademy' in text and username.lower() in final_url
                elif site == "Codepen":
                    bulundu = 'codepen' in text and username.lower() in final_url
                elif site == "HackerRank":
                    bulundu = 'hackerrank' in text and username.lower() in final_url
                elif site == "LeetCode":
                    bulundu = 'leetcode' in text and username.lower() in final_url
                elif site == "Replit":
                    bulundu = 'replit' in text and username.lower() in final_url
                elif site == "Last.fm":
                    bulundu = 'last.fm' in text and 'scrobbles' in text
                elif site == "Bandcamp":
                    bulundu = 'bandcamp' in text and 'music' in text
                elif site == "Mixcloud":
                    bulundu = 'mixcloud' in text and username.lower() in final_url
                elif site == "Flickr":
                    bulundu = 'flickr' in text and 'photos' in text
                elif site == "VK":
                    bulundu = 'vk.com' in final_url and 'profile' in text
                elif site == "Stack Overflow":
                    bulundu = 'stackoverflow' in text and 'profile' in text
                elif site == "BitBucket":
                    bulundu = 'bitbucket' in text and username.lower() in final_url
                else:
                    # Genel kontrol
                    bulundu = (r.status_code == 200 and 
                              'not found' not in text and 
                              'doesn\'t exist' not in text and 
                              'page not found' not in text and
                              'error' not in text.lower()[:50])
                
                if bulundu:
                    self.bulunan.append((site, url))
                    print(Fore.GREEN + f"  ✅ {site:<20s} → {url}")
                
            except:
                pass
            time.sleep(0.03)
        
        # Sonuç
        print(Fore.CYAN + f"\n  📊 SONUÇ:")
        print(Fore.GREEN + f"  ✅ {len(self.bulunan)} platformda BULUNDU")
        print(Fore.RED + f"  ❌ {len(platformlar) - len(self.bulunan)} platformda BULUNAMADI")
        
        if self.bulunan:
            print(Fore.YELLOW + "\n  🎯 BULUNAN HESAPLAR:")
            for site, url in self.bulunan:
                print(Fore.GREEN + f"  • {site}: {url}")
        else:
            print(Fore.YELLOW + "\n  💡 Hiçbir platformda bulunamadı!")
            print(Fore.CYAN + "  Benzer kullanıcı adlarını deneyin:")
            for v in [f"{username}1", f"{username}_", f"_{username}", f"{username}official", 
                     f"the{username}", f"{username}real", f"x{username}", f"{username}x"]:
                print(Fore.WHITE + f"  • {v}")

def ana():
    giris()
    o = MegaOSINT()
    o.bnr()
    
    while True:
        print(Fore.YELLOW + "\n🔍 MEGA MENÜ:")
        print("1. 📧 Email Tara (50+ Site + Data Leaks)")
        print("2. 📱 Numara Tara (15+ Site + Data Leaks)")
        print("3. 👤 Kullanıcı Adı Tara (60+ Site)")
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
            phone = ''.join(filter(str.isdigit, phone))
            if phone.startswith('0'): phone = phone[1:]
            if not phone.startswith('90'): phone = '90' + phone
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
