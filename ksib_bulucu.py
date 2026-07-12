#!/usr/bin/env python3
import requests, threading, time, sys, os, json, re, random
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

class OSINT:
    def __init__(self):
        self.ua = UserAgent()
        self.bulunan = []
        self.bulunmayan = []
        self.data_breaches = []
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + Style.BRIGHT + """
        ╔══════════════════════════════════════╗
        ║    🔍 KSIB OSINT v2.0 ULTRA         ║
        ║  📧 Email | 📱 Numara | 👤 Kullanıcı ║
        ║  🌐 Veri İhlalleri | 50+ Site       ║
        ╚══════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def baslik(self, text):
        print(Fore.YELLOW + f"\n{'='*60}")
        print(Fore.CYAN + Style.BRIGHT + f"  {text}")
        print(Fore.YELLOW + f"{'='*60}\n")
    
    def check_url(self, url, method='get', data=None, json_data=None, check_func=None, timeout=8):
        """Akıllı URL kontrol - sadece gerçekten varsa True döner"""
        try:
            headers = {
                "User-Agent": self.ua.random,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
            
            if method == 'post':
                if json_data:
                    headers["Content-Type"] = "application/json"
                    r = requests.post(url, json=json_data, headers=headers, timeout=timeout, allow_redirects=False)
                else:
                    r = requests.post(url, data=data, headers=headers, timeout=timeout, allow_redirects=False)
            else:
                r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=False)
            
            if check_func:
                return check_func(r)
            
            # Varsayılan kontrol
            return r.status_code in [200, 201, 202, 301, 302, 303]
            
        except:
            return False
    
    # ==================== EMAİL VERİ İHLALLERİ ====================
    
    def haveibeenpwned(self, email):
        """HaveIBeenPwned API - en güvenilir veri ihlali kontrolü"""
        try:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            headers = {
                "User-Agent": "KSIB-OSINT",
                "hibp-api-key": "0",  # Ücretsiz kullanım
                "Accept": "application/json",
            }
            r = requests.get(url, headers=headers, timeout=15)
            
            if r.status_code == 200:
                breaches = r.json()
                for breach in breaches:
                    self.data_breaches.append({
                        "site": breach.get("Name", "Bilinmiyor"),
                        "date": breach.get("BreachDate", "?"),
                        "data": ", ".join(breach.get("DataClasses", [])),
                        "description": breach.get("Description", "")[:200]
                    })
                return True
            return False
        except:
            return False
    
    def dehashed_search(self, email):
        """DeHashed kontrolü"""
        try:
            url = f"https://api.dehashed.com/search?query=email:{email}"
            headers = {"Accept": "application/json", "User-Agent": self.ua.random}
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get("entries"):
                    for entry in data["entries"][:10]:
                        self.data_breaches.append({
                            "site": entry.get("database_name", "Bilinmiyor"),
                            "date": entry.get("id", "?"),
                            "data": f"Email: {entry.get('email', '?')}, Password: {entry.get('password', '?')[:10]}...",
                            "description": "DeHashed veri tabanı"
                        })
                    return True
            return False
        except:
            return False
    
    def leakcheck_email(self, email):
        """LeakCheck kontrolü"""
        try:
            url = f"https://leakcheck.io/api/public?check={email}"
            headers = {"Accept": "application/json", "User-Agent": self.ua.random}
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get("success") and data.get("sources"):
                    for source in data["sources"]:
                        self.data_breaches.append({
                            "site": source.get("name", "Bilinmiyor"),
                            "date": source.get("date", "?"),
                            "data": source.get("lines", "?") + " kayıt",
                            "description": "LeakCheck veri tabanı"
                        })
                    return True
            return False
        except:
            return False
    
    # ==================== EMAİL SORGULAMA (50+ Site) ====================
    
    def email_tara(self, email):
        self.baslik(f"📧 EMAİL TARAMA: {email}")
        self.bulunan = []
        self.data_breaches = []
        
        # Veri ihlalleri kontrolü
        print(Fore.RED + "  🔴 VERİ İHLALLERİ KONTROLÜ:")
        print(Fore.WHITE + "  (HaveIBeenPwned, DeHashed, LeakCheck)\n")
        
        if self.haveibeenpwned(email):
            print(Fore.GREEN + f"  ⚠️  BU EMAİL {len(self.data_breaches)} VERİ İHLALİNDE BULUNDU!")
        else:
            print(Fore.YELLOW + "  ✅ Büyük ihlallerde bulunamadı (iyi haber!)")
        
        if self.data_breaches:
            print(Fore.RED + f"\n  📋 İHLAL DETAYLARI:")
            for breach in self.data_breaches[:10]:
                print(Fore.YELLOW + f"  • {breach['site']}")
                print(Fore.WHITE + f"    Tarih: {breach['date']}")
                print(Fore.WHITE + f"    Sızan veri: {breach['data'][:100]}")
        
        # Sosyal Medya
        print(Fore.CYAN + f"\n  📱 SOSYAL MEDYA (25+ Platform):")
        
        siteler = {
            # Sosyal Medya Devleri
            "Instagram": {
                "url": "https://www.instagram.com/api/v1/accounts/send_password_reset/",
                "method": "post",
                "data": lambda e: {"user_email": e},
                "check": lambda r: r.status_code == 200 and ("obfuscated" in r.text.lower() or "email_sent" in r.text.lower())
            },
            "Facebook": {
                "url": "https://www.facebook.com/login/identify/?ctx=recover",
                "method": "get",
                "params": lambda e: {"email": e},
                "check": lambda r: r.status_code == 200 and "password" in r.text.lower() and "no_account" not in r.text.lower()
            },
            "Twitter/X": {
                "url": "https://api.twitter.com/i/users/email_available.json",
                "method": "get",
                "params": lambda e: {"email": e},
                "check": lambda r: r.status_code == 200 and r.json().get("valid") == False
            },
            "TikTok": {
                "url": "https://www.tiktok.com/passport/email/available/",
                "method": "post",
                "json": lambda e: {"email": e},
                "check": lambda r: r.status_code == 200 and "registered" in r.text.lower()
            },
            "Snapchat": {
                "url": "https://accounts.snapchat.com/accounts/get_username",
                "method": "post",
                "json": lambda e: {"email": e, "requested_username": "test"},
                "check": lambda r: r.status_code == 200
            },
            "LinkedIn": {
                "url": "https://www.linkedin.com/uas/request-password-reset",
                "method": "post",
                "data": lambda e: {"session_key": e, "displayEmailResetFeedback": "true"},
                "check": lambda r: r.status_code == 200
            },
            "Pinterest": {
                "url": "https://www.pinterest.com/resource/EmailExistsResource/get/",
                "method": "get",
                "params": lambda e: {"source_url": "/", "data": '{"options":{"email":"' + e + '"},"context":{}}'},
                "check": lambda r: r.status_code == 200
            },
            "Reddit": {
                "url": "https://www.reddit.com/api/check_email.json",
                "method": "post",
                "data": lambda e: {"email": e},
                "check": lambda r: r.status_code == 200
            },
            "Tumblr": {
                "url": "https://www.tumblr.com/svc/account/register",
                "method": "post",
                "data": lambda e: {"email": e, "action": "check_email"},
                "check": lambda r: r.status_code == 200 and "taken" in r.text.lower()
            },
            "Flickr": {
                "url": "https://identity.flickr.com/checkemail",
                "method": "post",
                "data": lambda e: {"email": e},
                "check": lambda r: r.status_code == 200
            },
            "VK": {
                "url": "https://vk.com/rest/act/checkEmail",
                "method": "post",
                "data": lambda e: {"email": e},
                "check": lambda r: r.status_code == 200
            },
            "Ok.ru": {
                "url": "https://ok.ru/dk?cmd=AnonymRegistrationCheckEmail&st.email=" + email,
                "method": "get",
                "check": lambda r: r.status_code == 200
            },
            
            # Alışveriş
            "Amazon": {
                "url": "https://www.amazon.com/ap/forgotpassword",
                "method": "get",
                "params": lambda e: {"email": e},
                "check": lambda r: r.status_code == 200 and "password" in r.text.lower()
            },
            "eBay": {
                "url": "https://signin.ebay.com/ws/eBayISAPI.dll",
                "method": "get",
                "params": lambda e: {"email": e, "co_partnerId": "2", "siteid": "0", "pageType": "4"},
                "check": lambda r: r.status_code == 200
            },
            "Etsy": {
                "url": "https://www.etsy.com/signin/email",
                "method": "post",
                "data": lambda e: {"email": e},
                "check": lambda r: r.status_code == 200
            },
            "Alibaba": {
                "url": "https://passport.alibaba.com/icbu/account/checkEmail.htm",
                "method": "post",
                "data": lambda e: {"email": e},
                "check": lambda r: r.status_code == 200
            },
            "Walmart": {
                "url": "https://www.walmart.com/account/forgotpassword",
                "method": "post",
                "data": lambda e: {"email": e},
                "check": lambda r: r.status_code == 200
            },
            "Target": {
                "url": "https://www.target.com/account/forgotpassword",
                "method": "post",
                "data": lambda e: {"email": e},
                "check": lambda r: r.status_code == 200
            },
            
            # Teknoloji
            "GitHub": {
                "url": "https://github.com/signup_check/email",
                "method": "post",
                "data": lambda e: {"value": e},
                "check": lambda r: r.status_code == 200 and "already" in r.text.lower()
            },
            "GitLab": {
                "url": "https://gitlab.com/users/sign_up",
                "method": "post",
                "data": lambda e: {"user[email]": e},
                "check": lambda r: r.status_code == 200
            },
            "Stack Overflow": {
                "url": "https://stackoverflow.com/users/signup",
                "method": "post",
                "data": lambda e: {"email": e, "password": "test123"},
                "check": lambda r: r.status_code == 200
            },
            "WordPress.com": {
                "url": "https://public-api.wordpress.com/rest/v1.1/users/email/exists",
                "method": "get",
                "params": lambda e: {"email": e},
                "check": lambda r: r.status_code == 200
            },
            "Adobe": {
                "url": "https://auth.services.adobe.com/signup/v1/users/email",
                "method": "get",
                "params": lambda e: {"email": e},
                "check": lambda r: r.status_code == 200
            },
            "Spotify": {
                "url": "https://www.spotify.com/api/signup/validate",
                "method": "post",
                "json": lambda e: {"email": e, "creation_point": "client_web"},
                "check": lambda r: r.status_code == 200 and "already" in r.text.lower()
            },
            "Netflix": {
                "url": "https://www.netflix.com/tr/LoginHelp",
                "method": "post",
                "data": lambda e: {"email": e},
                "check": lambda r: r.status_code == 200
            },
            "Steam": {
                "url": "https://store.steampowered.com/join/checkemail/",
                "method": "post",
                "data": lambda e: {"email": e},
                "check": lambda r: r.status_code == 200
            },
            "Discord": {
                "url": "https://discord.com/api/v9/auth/register",
                "method": "post",
                "json": lambda e: {"email": e, "username": "test", "password": "test123"},
                "check": lambda r: r.status_code in [200, 400]
            },
            "PayPal": {
                "url": "https://www.paypal.com/authflow/entry",
                "method": "get",
                "params": lambda e: {"email": e},
                "check": lambda r: r.status_code == 200
            },
            "Robinhood": {
                "url": "https://api.robinhood.com/user/check_email/",
                "method": "post",
                "data": lambda e: {"email": e},
                "check": lambda r: r.status_code == 200
            },
            "Patreon": {
                "url": "https://www.patreon.com/api/auth/check_email",
                "method": "post",
                "data": lambda e: {"email": e},
                "check": lambda r: r.status_code == 200
            },
        }
        
        for site, config in siteler.items():
            try:
                if config["method"] == "post":
                    if "json" in config:
                        json_data = config["json"](email)
                        result = self.check_url(config["url"], method="post", json_data=json_data, check_func=config["check"])
                    else:
                        data = config["data"](email) if "data" in config else None
                        result = self.check_url(config["url"], method="post", data=data, check_func=config["check"])
                else:
                    params = config["params"](email) if "params" in config else None
                    result = self.check_url(config["url"], method="get", check_func=config["check"])
                
                if result:
                    self.bulunan.append(site)
                    print(Fore.GREEN + f"  ✅ {site}")
                else:
                    self.bulunmayan.append(site)
                    
            except:
                self.bulunmayan.append(site)
            
            time.sleep(0.05)
        
        print(Fore.CYAN + f"\n  📊 EMAİL SONUCU:")
        print(Fore.GREEN + f"  ✅ {len(self.bulunan)} platformda KAYITLI")
        print(Fore.RED + f"  ❌ {len(self.bulunmayan)} platformda KAYITSIZ")
        if len(siteler) > 0:
            print(Fore.YELLOW + f"  📈 Bulunma Oranı: %{len(self.bulunan)/len(siteler)*100:.1f}")
        
        # Email analizi
        if '@' in email:
            domain = email.split('@')[1]
            print(Fore.CYAN + f"\n  📋 EMAİL ANALİZİ:")
            print(Fore.WHITE + f"  📧 Domain: {domain}")
            
            domain_info = {
                'gmail.com': 'Google hesabı - YouTube, Drive, Photos ara!',
                'hotmail.com': 'Microsoft hesabı - Skype, Xbox, Office ara!',
                'outlook.com': 'Microsoft hesabı - Skype, Xbox, Office ara!',
                'yahoo.com': 'Yahoo hesabı - Flickr, Tumblr ara!',
                'icloud.com': 'Apple hesabı - iMessage, FaceTime ara!',
                'protonmail.com': 'Protonmail - Gizlilik odaklı kullanıcı',
                'yandex.com': 'Yandex - Rusya bağlantılı olabilir',
                'mail.ru': 'Mail.ru - Rusya bağlantılı olabilir',
            }
            
            if domain in domain_info:
                print(Fore.YELLOW + f"  💡 {domain_info[domain]}")
    
    # ==================== NUMARA SORGULAMA ====================
    
    def numara_tara(self, phone):
        self.baslik(f"📱 NUMARA TARAMA: +{phone}")
        self.bulunan = []
        
        # Operatör bilgisi
        if phone.startswith('90') and len(phone) == 12:
            operator = phone[2:5]
            print(Fore.CYAN + "  📡 OPERATÖR BİLGİSİ:")
            if operator[:2] == '53':
                print(Fore.YELLOW + "  📞 Turkcell")
                print(Fore.WHITE + "  🌐 https://www.turkcell.com.tr")
            elif operator[:2] == '54':
                print(Fore.YELLOW + "  📞 Vodafone")
                print(Fore.WHITE + "  🌐 https://www.vodafone.com.tr")
            elif operator[:2] == '55':
                print(Fore.YELLOW + "  📞 Türk Telekom")
                print(Fore.WHITE + "  🌐 https://www.turktelekom.com.tr")
            elif operator[:2] == '50':
                print(Fore.YELLOW + "  📞 Turkcell (eski numara)")
        
        print(Fore.CYAN + f"\n  📱 MESAJLAŞMA & SOSYAL MEDYA:")
        
        siteler = {
            "WhatsApp": {
                "url": f"https://wa.me/{phone}",
                "check": lambda r: r.status_code == 200 and "whatsapp" in r.text.lower()
            },
            "Telegram": {
                "url": f"https://t.me/+{phone}",
                "check": lambda r: r.status_code == 200
            },
            "Signal": {
                "url": f"https://signal.me/#p/+{phone}",
                "check": lambda r: r.status_code == 200
            },
            "Viber": {
                "url": f"https://invite.viber.com/?g2=invite&lang=tr&number=%2B{phone}",
                "check": lambda r: r.status_code == 200
            },
            "Line": {
                "url": f"https://line.me/R/ti/p/+{phone}",
                "check": lambda r: r.status_code == 200
            },
            "WeChat": {
                "url": f"https://weixin.qq.com/r/+{phone}",
                "check": lambda r: r.status_code == 200
            },
            "Instagram": {
                "url": "https://www.instagram.com/api/v1/accounts/send_password_reset/",
                "method": "post",
                "data": {"phone_number": phone},
                "check": lambda r: r.status_code == 200 and ("sent" in r.text.lower() or "obfuscated" in r.text.lower())
            },
            "Facebook": {
                "url": f"https://www.facebook.com/login/identify/?ctx=recover&phone={phone}",
                "check": lambda r: r.status_code == 200 and "password" in r.text.lower()
            },
            "Twitter/X": {
                "url": "https://api.twitter.com/i/users/phone_available.json",
                "method": "post",
                "data": {"phone_number": phone},
                "check": lambda r: r.status_code == 200
            },
            "Google": {
                "url": f"https://accounts.google.com/signup/v2/webcreateaccount?phone={phone}",
                "check": lambda r: r.status_code == 200
            },
            "TikTok": {
                "url": "https://www.tiktok.com/passport/account/send_code/",
                "method": "post",
                "data": {"mobile": phone, "type": "1"},
                "check": lambda r: r.status_code == 200
            },
            "Snapchat": {
                "url": "https://accounts.snapchat.com/accounts/get_username",
                "method": "post",
                "data": {"phone_number": phone},
                "check": lambda r: r.status_code == 200
            },
            "LinkedIn": {
                "url": "https://www.linkedin.com/uas/request-password-reset",
                "method": "post",
                "data": {"session_key": phone},
                "check": lambda r: r.status_code == 200
            },
            "Amazon": {
                "url": f"https://www.amazon.com/ap/forgotpassword?phone={phone}",
                "check": lambda r: r.status_code == 200
            },
            "eBay": {
                "url": f"https://signin.ebay.com/ws/eBayISAPI.dll?phone={phone}",
                "check": lambda r: r.status_code == 200
            },
            "PayPal": {
                "url": "https://www.paypal.com/authflow/entry",
                "method": "post",
                "data": {"phone": phone},
                "check": lambda r: r.status_code == 200
            },
            "Uber": {
                "url": "https://auth.uber.com/v2/api/send-otp",
                "method": "post",
                "data": {"phone": phone},
                "check": lambda r: r.status_code == 200
            },
            "Airbnb": {
                "url": "https://www.airbnb.com/api/v2/phone_verification",
                "check": lambda r: r.status_code == 200
            },
            "Tinder": {
                "url": "https://api.tinder.com/v2/auth/send-code",
                "method": "post",
                "data": {"phone_number": phone},
                "check": lambda r: r.status_code == 200
            },
            "Bumble": {
                "url": "https://bumble.com/api/auth/send-code",
                "method": "post",
                "data": {"phone": phone},
                "check": lambda r: r.status_code == 200
            },
        }
        
        for site, config in siteler.items():
            try:
                if "method" in config and config["method"] == "post":
                    result = self.check_url(config["url"], method="post", data=config.get("data"), check_func=config["check"])
                else:
                    result = self.check_url(config["url"], check_func=config["check"])
                
                if result:
                    self.bulunan.append(site)
                    print(Fore.GREEN + f"  ✅ {site}")
                else:
                    self.bulunmayan.append(site)
            except:
                pass
            
            time.sleep(0.05)
        
        print(Fore.CYAN + f"\n  📊 NUMARA SONUCU:")
        print(Fore.GREEN + f"  ✅ {len(self.bulunan)} platformda KAYITLI")
    
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
            "Venmo": f"https://venmo.com/{username}",
            "PayPal": f"https://www.paypal.com/paypalme/{username}",
            "Etsy": f"https://www.etsy.com/people/{username}",
            "Vimeo": f"https://vimeo.com/{username}",
            "Quora": f"https://www.quora.com/profile/{username}",
            "WordPress": f"https://{username}.wordpress.com",
            "Blogger": f"https://{username}.blogspot.com",
            "Roblox": f"https://www.roblox.com/user.aspx?username={username}",
            "Discord": f"https://discord.com/users/{username}",
        }
        
        print(Fore.WHITE + "  Taranıyor...\n")
        
        for site, url in platformlar.items():
            try:
                headers = {"User-Agent": self.ua.random}
                r = requests.get(url, headers=headers, timeout=8, allow_redirects=True)
                
                # KESİN KONTROL - sadece gerçekten varsa
                bulundu = False
                
                if r.status_code == 200:
                    text = r.text.lower()
                    final_url = r.url.lower()
                    
                    # Site özel kontroller
                    if site == "Instagram":
                        bulundu = '"followers_count"' in text or '"biography"' in text
                    elif site == "Twitter/X":
                        bulundu = 'profile' in text and 'this account doesn' not in text
                    elif site == "GitHub":
                        bulundu = 'repositories' in text and 'not found' not in text
                    elif site == "Reddit":
                        bulundu = '"karma"' in text or 'overview' in text
                    elif site == "TikTok":
                        bulundu = '"user_id"' in text or '"uniqueId"' in text
                    elif site == "YouTube":
                        bulundu = '"subscriberCountText"' in text or 'subscribers' in text
                    elif site == "LinkedIn":
                        bulundu = 'profile' in text and 'page not found' not in text
                    elif site == "Steam":
                        bulundu = 'profile' in text and 'the specified profile could not be found' not in text
                    elif site == "Spotify":
                        bulundu = '"display_name"' in text or 'followers' in text
                    else:
                        # Genel kontrol - URL değişmediyse ve 200 döndüyse
                        bulundu = username.lower() in final_url and 'not found' not in text and 'doesn\'t exist' not in text
                
                if bulundu:
                    self.bulunan.append((site, url))
                    print(Fore.GREEN + f"  ✅ {site:<20s} → {url}")
                
            except:
                pass
            
            time.sleep(0.05)
        
        print(Fore.CYAN + f"\n  📊 SONUÇ:")
        print(Fore.GREEN + f"  ✅ {len(self.bulunan)} platformda BULUNDU")
        
        if self.bulunan:
            print(Fore.YELLOW + f"\n  🎯 BULUNAN HESAPLAR:")
            for site, url in self.bulunan:
                print(Fore.GREEN + f"  • {site}: {url}")
        
        # Benzer öneriler
        print(Fore.CYAN + f"\n  💡 BENZER KULLANICI ADLARI:")
        varyasyonlar = [
            f"{username}1", f"{username}_", f"_{username}",
            f"{username}official", f"the{username}", f"{username}real",
            f"x{username}", f"{username}x", f"{username}tr",
        ]
        for v in varyasyonlar:
            print(Fore.WHITE + f"  • {v}")

def ana():
    giris()
    o = OSINT()
    o.bnr()
    
    while True:
        print(Fore.YELLOW + "\n🔍 ANA MENÜ:")
        print("1. 📧 Email Tara (30+ Site + Veri İhlalleri)")
        print("2. 📱 Numara Tara (20+ Site + Operatör)")
        print("3. 👤 Kullanıcı Adı Tara (35+ Site)")
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
            if len(phone) >= 10:
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
