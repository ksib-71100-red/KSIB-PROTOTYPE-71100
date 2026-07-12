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
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.ua.random})
        self.sonuclar = []
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + Style.BRIGHT + """
        ╔══════════════════════════════════════╗
        ║    🔍 KSIB OSINT v1.0               ║
        ║  📧 Email | 📱 Numara | 👤 Kullanıcı ║
        ╚══════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def baslik(self, text):
        print(Fore.YELLOW + f"\n{'='*50}")
        print(Fore.CYAN + Style.BRIGHT + f"  {text}")
        print(Fore.YELLOW + f"{'='*50}\n")
    
    def sonuc_yaz(self, platform, durum, detay=""):
        if durum:
            print(Fore.GREEN + f"  ✅ {platform:<20s} {detay}")
        else:
            print(Fore.RED + f"  ❌ {platform:<20s}")
    
    # ==================== EMAİL SORGULAMA ====================
    
    def instagram_email(self, email):
        try:
            url = "https://www.instagram.com/api/v1/accounts/send_password_reset/"
            data = {"user_email": email}
            headers = {
                "User-Agent": self.ua.random,
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest",
            }
            r = self.session.post(url, data=data, headers=headers, timeout=10)
            return "obfuscated_email" in r.text or "email_sent" in r.text.lower()
        except: return False
    
    def facebook_email(self, email):
        try:
            url = "https://www.facebook.com/login/identify"
            params = {"ctx": "recover", "email": email}
            headers = {"User-Agent": self.ua.random}
            r = self.session.get(url, params=params, headers=headers, timeout=10)
            return "recover" in r.text.lower() and "no account" not in r.text.lower()
        except: return False
    
    def twitter_email(self, email):
        try:
            url = "https://api.twitter.com/i/users/email_available.json"
            params = {"email": email}
            headers = {
                "User-Agent": self.ua.random,
                "X-Requested-With": "XMLHttpRequest",
            }
            r = self.session.get(url, params=params, headers=headers, timeout=10)
            data = r.json()
            return not data.get("valid", True)
        except: return False
    
    def tiktok_email(self, email):
        try:
            url = "https://www.tiktok.com/passport/email/available/"
            data = {"email": email}
            headers = {
                "User-Agent": self.ua.random,
                "Content-Type": "application/json",
            }
            r = self.session.post(url, json=data, headers=headers, timeout=10)
            return "already" in r.text.lower() or "registered" in r.text.lower()
        except: return False
    
    def snapchat_email(self, email):
        try:
            url = "https://accounts.snapchat.com/accounts/get_username"
            data = {"email": email}
            headers = {
                "User-Agent": self.ua.random,
                "Content-Type": "application/json",
            }
            r = self.session.post(url, json=data, headers=headers, timeout=10)
            return "username" in r.text.lower()
        except: return False
    
    def google_email(self, email):
        try:
            url = "https://accounts.google.com/signup/v2/webcreateaccount"
            params = {"email": email, "flowName": "GlifWebSignIn"}
            headers = {"User-Agent": self.ua.random}
            r = self.session.get(url, params=params, headers=headers, timeout=10)
            return "account exists" in r.text.lower() or "exists" in r.text.lower()
        except: return False
    
    def spotify_email(self, email):
        try:
            url = "https://www.spotify.com/api/signup/validate"
            data = {"email": email}
            headers = {
                "User-Agent": self.ua.random,
                "Content-Type": "application/json",
            }
            r = self.session.post(url, json=data, headers=headers, timeout=10)
            return "already" in r.text.lower()
        except: return False
    
    def netflix_email(self, email):
        try:
            url = "https://www.netflix.com/tr/LoginHelp"
            data = {"email": email}
            headers = {"User-Agent": self.ua.random}
            r = self.session.post(url, data=data, headers=headers, timeout=10)
            return "password" in r.text.lower() or "reset" in r.text.lower()
        except: return False
    
    def linkedin_email(self, email):
        try:
            url = "https://www.linkedin.com/uas/request-password-reset"
            data = {"session_key": email}
            headers = {
                "User-Agent": self.ua.random,
                "Content-Type": "application/x-www-form-urlencoded",
            }
            r = self.session.post(url, data=data, headers=headers, timeout=10)
            return "reset" in r.text.lower() or "sent" in r.text.lower()
        except: return False
    
    def amazon_email(self, email):
        try:
            url = "https://www.amazon.com/ap/forgotpassword"
            params = {"email": email}
            headers = {"User-Agent": self.ua.random}
            r = self.session.get(url, params=params, headers=headers, timeout=10)
            return "password" in r.text.lower()
        except: return False
    
    def email_tara(self, email):
        self.baslik(f"📧 EMAİL TARAMA: {email}")
        
        print(Fore.WHITE + "  Sosyal Medya:")
        self.sonuc_yaz("Instagram", self.instagram_email(email))
        self.sonuc_yaz("Facebook", self.facebook_email(email))
        self.sonuc_yaz("Twitter/X", self.twitter_email(email))
        self.sonuc_yaz("TikTok", self.tiktok_email(email))
        self.sonuc_yaz("Snapchat", self.snapchat_email(email))
        self.sonuc_yaz("LinkedIn", self.linkedin_email(email))
        
        print(Fore.WHITE + "\n  Diğer Platformlar:")
        self.sonuc_yaz("Google", self.google_email(email))
        self.sonuc_yaz("Spotify", self.spotify_email(email))
        self.sonuc_yaz("Netflix", self.netflix_email(email))
        self.sonuc_yaz("Amazon", self.amazon_email(email))
        
        # Email formatı kontrol
        print(Fore.WHITE + "\n  📋 Email Analizi:")
        if '@' in email:
            domain = email.split('@')[1]
            print(Fore.CYAN + f"  📧 Domain: {domain}")
            
            if 'gmail.com' in domain:
                print(Fore.YELLOW + "  💡 Gmail hesabı - Google servislerinde ara!")
            elif 'hotmail.com' in domain or 'outlook.com' in domain:
                print(Fore.YELLOW + "  💡 Microsoft hesabı - Skype/Xbox ara!")
            elif 'yahoo.com' in domain:
                print(Fore.YELLOW + "  💡 Yahoo hesabı - Flickr/Tumblr ara!")
            elif 'protonmail.com' in domain:
                print(Fore.YELLOW + "  💡 Protonmail - Gizlilik odaklı kullanıcı!")
    
    # ==================== NUMARA SORGULAMA ====================
    
    def whatsapp_numara(self, phone):
        try:
            url = "https://web.whatsapp.com/check"
            headers = {"User-Agent": self.ua.random}
            r = self.session.get(url, headers=headers, timeout=10)
            return "ok" in r.text.lower()
        except: return False
    
    def telegram_numara(self, phone):
        try:
            url = f"https://my.telegram.org/auth/check"
            data = {"phone": phone}
            headers = {"User-Agent": self.ua.random}
            r = self.session.post(url, data=data, headers=headers, timeout=10)
            return "ok" in r.text.lower() or "sent" in r.text.lower()
        except: return False
    
    def signal_numara(self, phone):
        try:
            url = "https://textsecure-service.whispersystems.org/v1/accounts/sms/code/+" + phone
            headers = {"User-Agent": self.ua.random}
            r = self.session.get(url, headers=headers, timeout=10)
            return r.status_code in [200, 201, 204]
        except: return False
    
    def numara_tara(self, phone):
        self.baslik(f"📱 NUMARA TARAMA: +{phone}")
        
        print(Fore.WHITE + "  Mesajlaşma:")
        self.sonuc_yaz("WhatsApp", self.whatsapp_numara(phone))
        self.sonuc_yaz("Telegram", self.telegram_numara(phone))
        self.sonuc_yaz("Signal", self.signal_numara(phone))
        
        # Instagram numara kontrolü
        try:
            url = "https://www.instagram.com/api/v1/accounts/send_password_reset/"
            data = {"phone_number": phone}
            headers = {"User-Agent": self.ua.random, "Content-Type": "application/x-www-form-urlencoded"}
            r = self.session.post(url, data=data, headers=headers, timeout=10)
            insta = "sent" in r.text.lower() or "obfuscated" in r.text.lower()
            self.sonuc_yaz("Instagram", insta)
        except: self.sonuc_yaz("Instagram", False)
        
        # Facebook numara kontrolü
        try:
            url = "https://www.facebook.com/login/identify"
            params = {"ctx": "recover", "phone": phone}
            headers = {"User-Agent": self.ua.random}
            r = self.session.get(url, params=params, headers=headers, timeout=10)
            fb = "recover" in r.text.lower()
            self.sonuc_yaz("Facebook", fb)
        except: self.sonuc_yaz("Facebook", False)
        
        print(Fore.WHITE + "\n  📋 Numara Analizi:")
        if phone.startswith('90'):
            operator = phone[2:5]
            print(Fore.CYAN + f"  📞 Ülke: Türkiye (+90)")
            
            if operator in ['530', '531', '532', '533', '534', '535', '536', '537', '538', '539']:
                print(Fore.YELLOW + f"  📡 Operatör: Turkcell")
            elif operator in ['540', '541', '542', '543', '544', '545', '546', '547', '548', '549']:
                print(Fore.YELLOW + f"  📡 Operatör: Vodafone")
            elif operator in ['550', '551', '552', '553', '554', '555', '556', '557', '558', '559']:
                print(Fore.YELLOW + f"  📡 Operatör: Türk Telekom")
    
    # ==================== KULLANICI ADI TARAMA ====================
    
    def sherlock_tara(self, username):
        self.baslik(f"👤 KULLANICI ADI TARAMA: @{username}")
        
        platformlar = {
            # Sosyal Medya
            "Instagram": {
                "url": f"https://www.instagram.com/{username}/",
                "check": lambda r: "followers" in r.text or "following" in r.text
            },
            "Twitter/X": {
                "url": f"https://twitter.com/{username}",
                "check": lambda r: "profile" in r.text.lower() and "doesn't exist" not in r.text.lower()
            },
            "Facebook": {
                "url": f"https://www.facebook.com/{username}",
                "check": lambda r: "profile" in r.text.lower() and "not found" not in r.text.lower()
            },
            "TikTok": {
                "url": f"https://www.tiktok.com/@{username}",
                "check": lambda r: "user_id" in r.text or "uniqueId" in r.text
            },
            "YouTube": {
                "url": f"https://www.youtube.com/@{username}",
                "check": lambda r: "subscriber" in r.text.lower()
            },
            "LinkedIn": {
                "url": f"https://www.linkedin.com/in/{username}",
                "check": lambda r: "profile" in r.text.lower() and "not found" not in r.text.lower()
            },
            "Snapchat": {
                "url": f"https://www.snapchat.com/add/{username}",
                "check": lambda r: "snapchat" in r.text.lower()
            },
            "Reddit": {
                "url": f"https://www.reddit.com/user/{username}",
                "check": lambda r: "karma" in r.text.lower() or "overview" in r.text.lower()
            },
            "Pinterest": {
                "url": f"https://www.pinterest.com/{username}/",
                "check": lambda r: "profile" in r.text.lower()
            },
            "Telegram": {
                "url": f"https://t.me/{username}",
                "check": lambda r: "tgme" in r.text.lower() or "telegram" in r.text.lower()
            },
            
            # Kod/Yazılım
            "GitHub": {
                "url": f"https://github.com/{username}",
                "check": lambda r: "repositories" in r.text.lower()
            },
            "GitLab": {
                "url": f"https://gitlab.com/{username}",
                "check": lambda r: "projects" in r.text.lower()
            },
            "BitBucket": {
                "url": f"https://bitbucket.org/{username}",
                "check": lambda r: "repositories" in r.text.lower()
            },
            "Stack Overflow": {
                "url": f"https://stackoverflow.com/users/{username}",
                "check": lambda r: "profile" in r.text.lower()
            },
            
            # Oyun
            "Steam": {
                "url": f"https://steamcommunity.com/id/{username}",
                "check": lambda r: "profile" in r.text.lower()
            },
            "Twitch": {
                "url": f"https://www.twitch.tv/{username}",
                "check": lambda r: "stream" in r.text.lower() or "offline" in r.text.lower()
            },
            "Discord": {
                "url": f"https://discord.com/users/{username}",
                "check": lambda r: "discord" in r.text.lower()
            },
            "Roblox": {
                "url": f"https://www.roblox.com/user.aspx?username={username}",
                "check": lambda r: "profile" in r.text.lower()
            },
            "Epic Games": {
                "url": f"https://www.epicgames.com/id/{username}",
                "check": lambda r: "epic" in r.text.lower()
            },
            "Spotify": {
                "url": f"https://open.spotify.com/user/{username}",
                "check": lambda r: "spotify" in r.text.lower()
            },
            
            # Forum/Blog
            "Medium": {
                "url": f"https://medium.com/@{username}",
                "check": lambda r: "followers" in r.text.lower() or "following" in r.text.lower()
            },
            "WordPress": {
                "url": f"https://{username}.wordpress.com",
                "check": lambda r: "blog" in r.text.lower()
            },
            "Blogger": {
                "url": f"https://{username}.blogspot.com",
                "check": lambda r: "blog" in r.text.lower()
            },
            "Quora": {
                "url": f"https://www.quora.com/profile/{username}",
                "check": lambda r: "profile" in r.text.lower()
            },
            
            # Diğer
            "Patreon": {
                "url": f"https://www.patreon.com/{username}",
                "check": lambda r: "patron" in r.text.lower()
            },
            "OnlyFans": {
                "url": f"https://onlyfans.com/{username}",
                "check": lambda r: "onlyfans" in r.text.lower()
            },
            "CashApp": {
                "url": f"https://cash.app/${username}",
                "check": lambda r: "cash" in r.text.lower()
            },
            "PayPal": {
                "url": f"https://www.paypal.com/paypalme/{username}",
                "check": lambda r: "paypal" in r.text.lower()
            },
            "Venmo": {
                "url": f"https://venmo.com/{username}",
                "check": lambda r: "venmo" in r.text.lower()
            },
            "Etsy": {
                "url": f"https://www.etsy.com/people/{username}",
                "check": lambda r: "etsy" in r.text.lower()
            },
        }
        
        bulunan = []
        bulunmayan = []
        
        print(Fore.WHITE + "  Taranıyor...\n")
        
        for platform, bilgi in platformlar.items():
            try:
                headers = {
                    "User-Agent": self.ua.random,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                }
                r = requests.get(bilgi["url"], headers=headers, timeout=10, allow_redirects=True)
                
                if bilgi["check"](r):
                    bulunan.append(platform)
                    print(Fore.GREEN + f"  ✅ {platform:<20s} Bulundu! → {bilgi['url']}")
                else:
                    bulunmayan.append(platform)
                    
            except Exception as e:
                bulunmayan.append(platform)
            
            time.sleep(0.1)
        
        print(Fore.CYAN + f"\n  📊 SONUÇ:")
        print(Fore.GREEN + f"  ✅ Bulunan: {len(bulunan)} platform")
        print(Fore.RED + f"  ❌ Bulunmayan: {len(bulunmayan)} platform")
        
        if bulunan:
            print(Fore.YELLOW + f"\n  🎯 BULUNAN HESAPLAR:")
            for p in bulunan:
                url = platformlar[p]["url"]
                print(Fore.GREEN + f"  • {p}: {url}")
        
        # Benzer kullanıcı adları öner
        print(Fore.CYAN + f"\n  💡 BENZER KULLANICI ADI ÖNERİLERİ:")
        varyasyonlar = [
            f"{username}1", f"{username}2", f"{username}123",
            f"{username}_", f"_{username}", f"{username}official",
            f"{username}real", f"the{username}", f"{username}tr",
            f"{username}0", f"x{username}", f"{username}x",
        ]
        for v in varyasyonlar[:8]:
            print(Fore.WHITE + f"  • {v}")

def ana():
    giris()
    o = OSINT()
    o.bnr()
    
    while True:
        print(Fore.YELLOW + "\n🔍 SEÇENEKLER:")
        print("1. 📧 Email Tara")
        print("2. 📱 Numara Tara (+90)")
        print("3. 👤 Kullanıcı Adı Tara (Sherlock)")
        print("4. 🚪 Çıkış")
        
        sec = input(Fore.GREEN + "\nSeçim: ")
        
        if sec == "1":
            email = input(Fore.GREEN + "📧 Email: ")
            o.email_tara(email)
            input(Fore.YELLOW + "\nDevam için Enter...")
            o.bnr()
            
        elif sec == "2":
            phone = input(Fore.GREEN + "📱 Numara (5XXXXXXXXX): ")
            phone = '90' + ''.join(filter(str.isdigit, phone))
            if phone.startswith('900'): phone = '90' + phone[3:]
            o.numara_tara(phone)
            input(Fore.YELLOW + "\nDevam için Enter...")
            o.bnr()
            
        elif sec == "3":
            username = input(Fore.GREEN + "👤 Kullanıcı adı (@ olmadan): ")
            o.sherlock_tara(username)
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
