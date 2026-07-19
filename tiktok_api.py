#!/usr/bin/env python3
# KSIB TİKTOK GRABBER v2 - Tüm Cookie'lerle Çalışan
import requests, json, sys, os, time
from colorama import init, Fore
init(autoreset=True)

SIFRE = "admiral71100daphne"

def giris():
    os.system('cls' if os.name == 'nt' else 'clear')
    for i in range(3):
        if input(Fore.YELLOW + "\nSifre: ") == SIFRE:
            return True
        print(Fore.RED + f"Hatali ({2-i})")
    sys.exit(0)

class TikTokGrabberV2:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "tr-TR,tr;q=0.9",
            "Referer": "https://www.tiktok.com/",
        })
    
    def load_cookies_from_text(self, cookie_text):
        """Cookie metnini parse et"""
        cookies = {}
        
        for line in cookie_text.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Format: domain TRUE path TRUE/FALSE expiry name value
            parts = line.split('\t')
            if len(parts) >= 7:
                name = parts[5]
                value = parts[6]
                cookies[name] = value
            # Alternatif format: name=value
            elif '=' in line and 'TRUE' not in line:
                name, value = line.split('=', 1)
                cookies[name.strip()] = value.strip()
        
        return cookies
    
    def set_cookies(self, cookies):
        """Cookie'leri session'a yükle"""
        for name, value in cookies.items():
            self.session.cookies.set(name, value, domain='.tiktok.com')
    
    def get_user_info(self, username):
        """Kullanıcı bilgilerini çek"""
        print(Fore.CYAN + f"\n🔍 @{username} bilgileri cekiliyor...\n")
        
        try:
            # API isteği
            url = f"https://www.tiktok.com/api/user/detail/?uniqueId={username}&language=tr"
            r = self.session.get(url, timeout=15)
            
            if r.status_code != 200:
                print(Fore.RED + f"❌ HTTP {r.status_code}")
                return None
            
            data = r.json()
            
            # Başarılı mı?
            if data.get("status_code") == 0 or "userInfo" in data:
                user = data.get("userInfo", {})
                
                if not user:
                    print(Fore.RED + "❌ Kullanici bulunamadi!")
                    return None
                
                info = {
                    "username": user.get("uniqueId", "?"),
                    "nickname": user.get("nickname", "?"),
                    "user_id": user.get("id", "?"),
                    "sec_uid": user.get("secUid", "?"),
                    "followers": user.get("followerCount", 0),
                    "following": user.get("followingCount", 0),
                    "videos": user.get("videoCount", 0),
                    "likes": user.get("heartCount", 0),
                    "verified": user.get("verified", False),
                    "private": user.get("secret", False),
                    "bio": user.get("signature", ""),
                    "region": user.get("region", "?"),
                    "avatar": user.get("avatarMedium", ""),
                    "email": user.get("email", "?"),
                    "phone": user.get("mobile", "?"),
                }
                
                return info
            else:
                print(Fore.RED + f"❌ Session gecersiz! Cookie'leri kontrol et.")
                return None
                
        except Exception as e:
            print(Fore.RED + f"❌ Hata: {e}")
            return None
    
    def get_email_phone(self, sec_uid):
        """Email ve telefon çek"""
        try:
            url = f"https://www.tiktok.com/api/user/detail/?secUid={sec_uid}&language=tr"
            r = self.session.get(url, timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                user = data.get("userInfo", {})
                return {
                    "email": user.get("email", user.get("emailAddress", "?")),
                    "phone": user.get("mobile", user.get("phoneNumber", "?")),
                }
            return {}
        except:
            return {}
    
    def print_card(self, info, email_info):
        """Bilgileri yazdır"""
        print(Fore.MAGENTA + """
        ╔══════════════════════════════════════╗
        ║     🎵 TİKTOK KULLANICI BİLGİSİ    ║
        ╚══════════════════════════════════════╝
        """)
        
        print(Fore.WHITE + f"""
        👤 @{info['username']} | 📝 {info['nickname']}
        🆔 ID: {info['user_id']}
        {'✅ Dogrulanmis' if info['verified'] else '❌ Dogrulanmamis'}
        {'🔒 Gizli Hesap' if info['private'] else '🌍 Acik Hesap'}
        
        📊 İstatistikler:
        👥 Takipci: {info['followers']:,}
        🚶 Takip: {info['following']:,}
        🎵 Video: {info['videos']:,}
        ❤️  Like: {info['likes']:,}
        
        📧 Email: {info.get('email') or email_info.get('email', 'Bulunamadi')}
        📞 Telefon: {info.get('phone') or email_info.get('phone', 'Bulunamadi')}
        🌍 Bolge: {info['region']}
        """)
        
        if info.get('bio'):
            print(Fore.CYAN + f"        📝 Bio: {info['bio'][:150]}")
        
        print(Fore.YELLOW + "\n        " + "="*40 + "\n")

def ana():
    giris()
    grabber = TikTokGrabberV2()
    
    print(Fore.YELLOW + "\n🎵 TİKTOK COOKIE GİRİN:")
    print(Fore.CYAN + "Tum cookie'leri tek seferde yapistirin.")
    print(Fore.CYAN + "Bitince bos satirda Enter'a basin.\n")
    
    print(Fore.WHITE + "┌─ Cookie'leri Yapistir ─┐")
    lines = []
    while True:
        line = input(Fore.WHITE + "│ " + Fore.GREEN).strip()
        if not line:
            break
        lines.append(line)
    print(Fore.WHITE + "└─────────────────────────┘")
    
    if not lines:
        print(Fore.RED + "❌ Cookie girilmedi!")
        return
    
    # Cookie'leri yükle
    cookie_text = '\n'.join(lines)
    cookies = grabber.load_cookies_from_text(cookie_text)
    
    # Gerekli cookie'leri kontrol et
    required = ['sessionid', 'ttwid']
    missing = [c for c in required if c not in cookies]
    
    if missing:
        print(Fore.RED + f"\n❌ Eksik cookie: {', '.join(missing)}")
        return
    
    grabber.set_cookies(cookies)
    
    print(Fore.GREEN + f"\n✅ {len(cookies)} cookie yuklendi!")
    print(Fore.CYAN + f"🔑 Session ID: {cookies.get('sessionid', '?')[:20]}...")
    
    while True:
        print(Fore.YELLOW + "\n🎵 MENÜ:")
        print("1. 🔍 Kullanici Bilgisi Cek")
        print("2. 🚪 Cikis")
        
        sec = input(Fore.GREEN + "\n> ").strip()
        
        if sec == "1":
            username = input(Fore.GREEN + "\nKullanici adi (@ olmadan): ").strip()
            if username:
                info = grabber.get_user_info(username)
                if info:
                    email_info = grabber.get_email_phone(info["sec_uid"])
                    grabber.print_card(info, email_info)
        
        elif sec == "2":
            print(Fore.GREEN + "\n👋 Bye!")
            break

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Cikis!")
        sys.exit(0)
