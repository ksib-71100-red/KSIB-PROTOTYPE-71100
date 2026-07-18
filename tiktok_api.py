#!/usr/bin/env python3
# KSIB TİKTOK USER İNFO GRABBER - Session ID ile API
import requests, json, sys, os, time
from colorama import init, Fore, Style
init(autoreset=True)

SIFRE = "admiral71100daphne"

def giris():
    os.system('cls' if os.name == 'nt' else 'clear')
    for i in range(3):
        if input(Fore.YELLOW + "\nSifre: ") == SIFRE:
            return True
        print(Fore.RED + f"Hatali ({2-i})")
    sys.exit(0)

class TikTokGrabber:
    def __init__(self, session_id):
        self.session_id = session_id
        self.headers = {
            "User-Agent": "com.zhiliaoapp.musically/2023700040 (Linux; U; Android 13; tr_TR)",
            "Cookie": f"sessionid={session_id}",
            "Accept": "application/json",
            "Accept-Language": "tr-TR,tr;q=0.9",
        }
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.MAGENTA + Style.BRIGHT + """
        ╔══════════════════════════════════════╗
        ║  🎵 TİKTOK USER İNFO GRABBER       ║
        ║  📧 Email | 📞 Telefon | 👤 Bilgi   ║
        ╚══════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def get_user_info(self, username):
        """Kullanıcı bilgilerini çek"""
        print(Fore.CYAN + f"\n🔍 @{username} bilgileri cekiliyor...\n")
        
        try:
            # API 1: Kullanıcı detayı
            url = f"https://www.tiktok.com/api/user/detail/?uniqueId={username}&language=tr"
            r = requests.get(url, headers=self.headers, timeout=15)
            
            if r.status_code != 200:
                print(Fore.RED + "❌ Session ID gecersiz veya rate-limit!")
                return None
            
            data = r.json()
            user = data.get("userInfo", {})
            
            if not user:
                print(Fore.RED + "❌ Kullanici bulunamadi!")
                return None
            
            # Temel bilgiler
            user_info = {
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
                "language": user.get("language", "?"),
                "avatar": user.get("avatarMedium", ""),
            }
            
            # Gizli bilgiler için API 2
            email = "?"
            phone = "?"
            
            if user_info["sec_uid"]:
                try:
                    url2 = f"https://www.tiktok.com/api/user/detail/?secUid={user_info['sec_uid']}&language=tr"
                    r2 = requests.get(url2, headers=self.headers, timeout=10)
                    if r2.status_code == 200:
                        data2 = r2.json()
                        user2 = data2.get("userInfo", {})
                        
                        # Email
                        email = user2.get("email", "?")
                        if not email or email == "":
                            email = user2.get("emailAddress", "?")
                        
                        # Telefon
                        phone = user2.get("mobile", "?")
                        if not phone or phone == "":
                            phone = user2.get("phoneNumber", "?")
                        
                        # Bağlı hesaplar
                        user_info["bind_info"] = user2.get("bindInfo", {})
                except:
                    pass
            
            user_info["email"] = email
            user_info["phone"] = phone
            
            return user_info
            
        except Exception as e:
            print(Fore.RED + f"❌ Hata: {e}")
            return None
    
    def get_user_videos(self, sec_uid, count=10):
        """Kullanıcının videolarını çek"""
        try:
            url = f"https://www.tiktok.com/api/post/item_list/?secUid={sec_uid}&count={count}&cursor=0"
            r = requests.get(url, headers=self.headers, timeout=10)
            
            if r.status_code == 200:
                videos = r.json().get("itemList", [])
                return [{
                    "id": v.get("id", "?"),
                    "desc": v.get("desc", "")[:50],
                    "views": v.get("stats", {}).get("playCount", 0),
                    "likes": v.get("stats", {}).get("diggCount", 0),
                    "comments": v.get("stats", {}).get("commentCount", 0),
                    "shares": v.get("stats", {}).get("shareCount", 0),
                    "created": v.get("createTime", 0),
                } for v in videos]
            return []
        except:
            return []
    
    def get_email_phone(self, sec_uid):
        """Email ve telefon için özel endpoint"""
        try:
            # Gizli bilgi endpoint'i
            url = f"https://www.tiktok.com/passport/web/account/info/"
            r = requests.get(url, headers=self.headers, timeout=10)
            
            if r.status_code == 200:
                data = r.json().get("data", {})
                return {
                    "email": data.get("email", "?"),
                    "phone": data.get("mobile", "?"),
                    "username": data.get("username", "?"),
                    "create_time": data.get("createTime", 0),
                }
            return None
        except:
            return None
    
    def get_followers_list(self, sec_uid, count=20):
        """Takipçi listesini çek"""
        try:
            url = f"https://www.tiktok.com/api/user/list/?secUid={sec_uid}&type=1&count={count}"
            r = requests.get(url, headers=self.headers, timeout=10)
            
            if r.status_code == 200:
                users = r.json().get("userList", [])
                return [{
                    "username": u.get("uniqueId", "?"),
                    "nickname": u.get("nickname", "?"),
                    "followers": u.get("followerCount", 0),
                } for u in users]
            return []
        except:
            return []
    
    def print_user_card(self, info, videos, email_info):
        """Kullanıcı kartını yazdır"""
        print(Fore.MAGENTA + Style.BRIGHT + """
        ╔══════════════════════════════════════════════╗
        ║         🎵 TİKTOK KULLANICI BİLGİLERİ      ║
        ╚══════════════════════════════════════════════╝
        """ + Style.RESET_ALL)
        
        print(Fore.WHITE + f"""
        👤 Kullanici   : @{info['username']}
        📝 Isim        : {info['nickname']}
        🆔 User ID     : {info['user_id']}
        🔒 Gizli Hesap : {'Evet' if info['private'] else 'Hayir'}
        ✅ Dogrulama   : {'Var' if info['verified'] else 'Yok'}
        🌍 Bolge       : {info['region']}
        """)
        
        print(Fore.CYAN + f"""
        📊 İSTATİSTİKLER:
        👥 Takipci     : {info['followers']:,}
        🚶 Takip       : {info['following']:,}
        🎵 Video       : {info['videos']:,}
        ❤️  Like        : {info['likes']:,}
        """)
        
        print(Fore.RED + f"""
        🔒 GİZLİ BİLGİLER:
        📧 Email       : {info.get('email', email_info.get('email', '?')) if info.get('email') != '?' else email_info.get('email', 'Bulunamadi')}
        📞 Telefon     : {info.get('phone', email_info.get('phone', '?')) if info.get('phone') != '?' else email_info.get('phone', 'Bulunamadi')}
        """)
        
        if info.get('bio'):
            print(Fore.WHITE + f"""
        📝 Bio:
        {info['bio'][:200]}
        """)
        
        if videos:
            print(Fore.YELLOW + "\n  🎵 SON VİDEOLAR:")
            for i, v in enumerate(videos[:5], 1):
                views = f"{v['views']:,}" if v['views'] > 0 else "0"
                likes = f"{v['likes']:,}" if v['likes'] > 0 else "0"
                print(Fore.WHITE + f"  [{i}] 👁️ {views} | ❤️ {likes} | 💬 {v['comments']}")
                print(Fore.CYAN + f"      {v['desc'][:60]}")
        
        print(Fore.YELLOW + "\n  " + "="*50 + "\n")
    
    def save_json(self, info, videos, email_info):
        """JSON olarak kaydet"""
        data = {
            "user": info,
            "videos": videos,
            "email_info": email_info,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        filename = f"tiktok_{info['username']}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(Fore.GREEN + f"💾 Kaydedildi: {filename}")

def ana():
    giris()
    
    # Session ID al
    print(Fore.YELLOW + "\n🎵 TİKTOK SESSION ID GİRİN:")
    print(Fore.CYAN + "TikTok Web'de F12 > Application > Cookies > sessionid")
    print(Fore.CYAN + "veya TikTok'ta giris yapip kopyalayin\n")
    
    session_id = input(Fore.GREEN + "Session ID: ").strip()
    
    if not session_id or len(session_id) < 10:
        print(Fore.RED + "❌ Gecerli session ID girin!")
        return
    
    grabber = TikTokGrabber(session_id)
    grabber.bnr()
    
    while True:
        print(Fore.YELLOW + "\n🎵 MENÜ:")
        print("1. 🔍 Kullanici Bilgisi Cek (Email/Telefon)")
        print("2. 🎵 Video Listesi Cek")
        print("3. 👥 Takipci Listesi Cek")
        print("4. 🚪 Cikis")
        
        sec = input(Fore.GREEN + "\n> ").strip()
        
        if sec == "1":
            username = input(Fore.GREEN + "\nKullanici adi (@ olmadan): ").strip()
            if username:
                info = grabber.get_user_info(username)
                if info:
                    videos = grabber.get_user_videos(info["sec_uid"], 5)
                    email_info = grabber.get_email_phone(info["sec_uid"])
                    grabber.print_user_card(info, videos, email_info)
                    
                    # Kaydet
                    if input(Fore.GREEN + "JSON kaydet? (E): ").upper() == "E":
                        grabber.save_json(info, videos, email_info)
        
        elif sec == "2":
            username = input(Fore.GREEN + "\nKullanici adi: ").strip()
            if username:
                info = grabber.get_user_info(username)
                if info:
                    videos = grabber.get_user_videos(info["sec_uid"], 10)
                    if videos:
                        print(Fore.YELLOW + f"\n🎵 {len(videos)} VIDEO:")
                        for i, v in enumerate(videos, 1):
                            print(Fore.WHITE + f"\n  [{i}] {v['desc'][:50]}")
                            print(Fore.CYAN + f"  👁️ {v['views']:,} | ❤️ {v['likes']:,} | 💬 {v['comments']:,}")
        
        elif sec == "3":
            username = input(Fore.GREEN + "\nKullanici adi: ").strip()
            if username:
                info = grabber.get_user_info(username)
                if info:
                    followers = grabber.get_followers_list(info["sec_uid"], 20)
                    if followers:
                        print(Fore.YELLOW + f"\n👥 {len(followers)} TAKİPCİ:")
                        for i, f in enumerate(followers, 1):
                            print(Fore.WHITE + f"  [{i}] @{f['username']} ({f['followers']:,} takipci)")
        
        elif sec == "4":
            print(Fore.GREEN + "\n👋 Bye!")
            break
        
        input(Fore.YELLOW + "\nEnter...")

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Cikis!")
        sys.exit(0)
