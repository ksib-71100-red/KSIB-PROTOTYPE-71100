#!/usr/bin/env python3
# KSIB WIFI PASSWORD VIEWER v1.0
import subprocess, sys, os, re
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

class WiFiViewer:
    def __init__(self):
        self.os_type = sys.platform
    
    def bnr(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(Fore.CYAN + Style.BRIGHT + """
        ╔══════════════════════════════════════╗
        ║   📡 KSIB WIFI PASSWORD VIEWER      ║
        ║   Windows | Linux | Mac             ║
        ╚══════════════════════════════════════╝
        """ + Style.RESET_ALL)
    
    def get_windows_wifi(self):
        """Windows kayıtlı WiFi şifreleri"""
        try:
            # Tüm profilleri al
            data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles'], 
                                          shell=True, text=True, encoding='utf-8', errors='ignore')
            
            # SSID'leri çıkar
            profiles = re.findall(r':\s(.+)$', data, re.MULTILINE)
            
            if not profiles:
                print(Fore.RED + "❌ Hiç kayıtlı WiFi bulunamadı!")
                return
            
            print(Fore.CYAN + f"\n📡 {len(profiles)} KAYITLI WIFI BULUNDU:\n")
            print(Fore.YELLOW + "="*70)
            print(Fore.WHITE + f"{'SSID':<30s} {'GÜVENLİK':<15s} {'ŞİFRE':<25s}")
            print(Fore.YELLOW + "="*70)
            
            wifi_list = []
            
            for ssid in profiles:
                ssid = ssid.strip()
                if not ssid: continue
                
                try:
                    # Şifre bilgisini al
                    result = subprocess.check_output(
                        ['netsh', 'wlan', 'show', 'profile', f'name={ssid}', 'key=clear'],
                        shell=True, text=True, encoding='utf-8', errors='ignore'
                    )
                    
                    # Güvenlik tipi
                    security_match = re.search(r'Authentication\s+:\s(.+)', result)
                    security = security_match.group(1).strip() if security_match else "Bilinmiyor"
                    
                    # Şifre
                    password_match = re.search(r'Key Content\s+:\s(.+)', result)
                    password = password_match.group(1).strip() if password_match else "AÇIK AĞ"
                    
                    wifi_list.append({
                        'ssid': ssid,
                        'security': security,
                        'password': password
                    })
                    
                    # Renkli göster
                    if password == "AÇIK AĞ":
                        color = Fore.YELLOW
                    elif len(password) < 8:
                        color = Fore.RED
                    else:
                        color = Fore.GREEN
                    
                    print(f"{Fore.WHITE}{ssid:<30s} {Fore.CYAN}{security:<15s} {color}{password:<25s}")
                    
                except:
                    print(f"{Fore.WHITE}{ssid:<30s} {Fore.RED}HATA{'':<10s} {'Erişilemedi':<25s}")
            
            print(Fore.YELLOW + "="*70)
            
            # İstatistik
            acik = sum(1 for w in wifi_list if w['password'] == 'AÇIK AĞ')
            zayif = sum(1 for w in wifi_list if w['password'] != 'AÇIK AĞ' and len(w['password']) < 8)
            guclu = sum(1 for w in wifi_list if w['password'] != 'AÇIK AĞ' and len(w['password']) >= 8)
            
            print(Fore.CYAN + f"\n📊 İSTATİSTİK:")
            print(Fore.YELLOW + f"🔓 Açık Ağ: {acik}")
            print(Fore.RED + f"⚠️  Zayıf Şifre: {zayif}")
            print(Fore.GREEN + f"✅ Güçlü Şifre: {guclu}")
            
            # En çok kullanılan şifre tipleri
            if wifi_list:
                print(Fore.CYAN + f"\n🔍 ŞİFRE ANALİZİ:")
                for w in wifi_list:
                    if w['password'] != 'AÇIK AĞ':
                        pwd = w['password']
                        if pwd.isdigit():
                            print(Fore.YELLOW + f"   📞 {w['ssid']}: Sadece rakam (telefon numarası olabilir)")
                        elif pwd.isalpha():
                            print(Fore.YELLOW + f"   📝 {w['ssid']}: Sadece harf (isim olabilir)")
                        elif re.match(r'^[A-Za-z]+\d+$', pwd):
                            print(Fore.YELLOW + f"   🔤 {w['ssid']}: Harf + Rakam (doğum tarihi?)")
            
            return wifi_list
            
        except Exception as e:
            print(Fore.RED + f"❌ Hata: {e}")
            return []
    
    def get_linux_wifi(self):
        """Linux kayıtlı WiFi şifreleri"""
        try:
            import glob
            
            print(Fore.CYAN + "\n📡 KAYITLI WIFI AĞLARI:\n")
            print(Fore.YELLOW + "="*70)
            print(Fore.WHITE + f"{'SSID':<30s} {'ŞİFRE':<35s}")
            print(Fore.YELLOW + "="*70)
            
            wifi_list = []
            
            # NetworkManager bağlantıları
            paths = [
                '/etc/NetworkManager/system-connections/*',
                '/etc/wpa_supplicant/wpa_supplicant.conf'
            ]
            
            for path in paths:
                for file in glob.glob(path):
                    try:
                        with open(file, 'r') as f:
                            content = f.read()
                            
                            ssid_match = re.search(r'ssid="?(.+?)"?\n', content)
                            psk_match = re.search(r'psk="?(.+?)"?\n', content)
                            
                            if ssid_match:
                                ssid = ssid_match.group(1).strip()
                                password = psk_match.group(1).strip() if psk_match else "AÇIK AĞ"
                                
                                wifi_list.append({'ssid': ssid, 'password': password})
                                
                                color = Fore.GREEN if password != "AÇIK AĞ" else Fore.YELLOW
                                print(f"{Fore.WHITE}{ssid:<30s} {color}{password:<35s}")
                    except:
                        continue
            
            print(Fore.YELLOW + "="*70)
            return wifi_list
            
        except Exception as e:
            print(Fore.RED + f"❌ Hata: {e}")
            return []
    
    def get_mac_wifi(self):
        """Mac kayıtlı WiFi şifreleri"""
        try:
            # Airport komutu
            result = subprocess.check_output(
                ['security', 'find-generic-password', '-ga', 'WIFI'],
                text=True, stderr=subprocess.STDOUT
            )
            print(result)
        except:
            print(Fore.RED + "❌ Mac'te WiFi şifresi okunamadı!")
    
    def export_results(self, wifi_list, format='txt'):
        """Sonuçları dışa aktar"""
        if not wifi_list: return
        
        filename = f"wifi_passwords_{time.strftime('%Y%m%d_%H%M%S')}.{format}"
        
        if format == 'txt':
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("="*50 + "\n")
                f.write("WIFI PASSWORD LIST\n")
                f.write("="*50 + "\n\n")
                for w in wifi_list:
                    f.write(f"SSID: {w['ssid']}\n")
                    f.write(f"Password: {w['password']}\n")
                    f.write("-"*30 + "\n")
        
        elif format == 'csv':
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("SSID,Security,Password\n")
                for w in wifi_list:
                    f.write(f"{w.get('ssid','')},{w.get('security','')},{w.get('password','')}\n")
        
        print(Fore.GREEN + f"\n💾 Kaydedildi: {filename}")

def ana():
    giris()
    wv = WiFiViewer()
    wv.bnr()
    
    print(Fore.YELLOW + "\nİşletim Sistemi: " + Fore.CYAN + sys.platform)
    
    if sys.platform == 'win32':
        wifi_list = wv.get_windows_wifi()
    elif sys.platform == 'linux':
        wifi_list = wv.get_linux_wifi()
    elif sys.platform == 'darwin':
        wifi_list = wv.get_mac_wifi()
    else:
        print(Fore.RED + "❌ Desteklenmeyen işletim sistemi!")
        return
    
    if wifi_list:
        print(Fore.YELLOW + "\n💾 Dışa aktar:")
        print(Fore.CYAN + "1. TXT olarak kaydet")
        print(Fore.CYAN + "2. CSV olarak kaydet")
        print(Fore.CYAN + "3. Kaydetme")
        
        sec = input(Fore.GREEN + "Seçim: ")
        if sec == "1":
            wv.export_results(wifi_list, 'txt')
        elif sec == "2":
            wv.export_results(wifi_list, 'csv')
    
    input(Fore.YELLOW + "\nÇıkmak için Enter...")

if __name__ == "__main__":
    import time
    try:
        ana()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Çıkış!")
        sys.exit(0)
