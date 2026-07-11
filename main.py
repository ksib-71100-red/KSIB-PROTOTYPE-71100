import requests
import time
import random
import getpass

print("=== KSIB PROTOTYPE 71100 ===")
print("Mass TikTok Reporter\n")

# Şifre
sifre = getpass.getpass("Şifreyi gir: ")
if sifre != "71100admiral":
    print("Yanlış şifre !?")
    exit()

video_link = input("\nVideo linkini yapıştır: ").strip()

if "/video/" in video_link:
    video_id = video_link.split("/video/")[1].split("?")[0].split("/")[0]
else:
    video_id = video_link

adet = int(input("Kaç rapor atalım? (10-300): "))
bekleme = float(input("Bekleme süresi (0.4-1.0): ") or 0.5)

print(f"\nHedef Video ID: {video_id}")
print(f"{adet} rapor başlatılıyor...\n")

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)",
}

success = 0
for i in range(adet):
    try:
        payload = {
            "item_id": video_id,
            "reason": random.choice([1000, 2001, 3002, 4000]),
            "report_type": random.choice([1, 2, 3]),
        }

        r = requests.post(
            "https://www.tiktok.com/api/feedback/",
            headers=headers,
            json=payload,
            timeout=10
        )

        if r.status_code == 200:
            success += 1
            print(f"[{i+1}/{adet}] ✅ Başarılı")
        else:
            print(f"[{i+1}/{adet}] ❌ {r.status_code}")
    except:
        print(f"[{i+1}/{adet}] ❌ Hata")

    time.sleep(bekleme + random.uniform(0, 0.3))

print(f"\nKSIB Tamamlandı! {success}/{adet} rapor gönderildi.")
