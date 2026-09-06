#!/usr/bin/env python3
# KSIB ULTRA MEGA SCANNER - iSH SIRALI (5 DAKİKA)
# pip install requests

import socket, ssl, requests, json, time, re, sys
from datetime import datetime
import urllib3
urllib3.disable_warnings()

# ============================================================
# RENKLER
# ============================================================
R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; B = "\033[94m"
M = "\033[95m"; C = "\033[96m"; N = "\033[0m"; BOLD = "\033[1m"

# ============================================================
# SCANNER (SIRALI)
# ============================================================
class Scanner:
    def __init__(self, target):
        self.target = target
        self.start = time.time()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
            "Connection": "keep-alive"
        })
        self.session.timeout = 1.5  # KISA TIMEOUT

        self.results = {
            "target": target,
            "ports": [],
            "ssl": {},
            "headers": {},
            "dirs": [],
            "subdomains": [],
            "vulns": [],
            "emails": [],
            "waf": None,
            "cloud": None,
            "tech": []
        }

        self.dirs = [
            "/admin", "/login", "/wp-admin", "/phpmyadmin", "/.git", "/.env",
            "/robots.txt", "/sitemap.xml", "/favicon.ico", "/backup", "/test",
            "/wp-content", "/wp-includes", "/server-status", "/cgi-bin",
            "/phpinfo.php", "/info.php", "/config.php", "/index.php", "/index.html"
        ]

        self.subdomains = [
            "www", "mail", "ftp", "dev", "api", "admin", "cdn", "static",
            "blog", "shop", "docs", "support", "demo", "backup"
        ]

        self.waf_sigs = {
            "Cloudflare": ["cf-ray", "__cfduid", "cloudflare"],
            "AWS WAF": ["x-amzn-requestid", "awswaf"],
            "Sucuri": ["sucuri", "x-sucuri-id"]
        }

        self.cloud_sigs = {
            "AWS": ["x-amz", "cloudfront"],
            "Cloudflare": ["cf-", "cloudflare"],
            "Google": ["x-gcs", "google-cloud"]
        }

        self.vuln_patterns = {
            "SQL": r"(sql|mysql|postgresql|oracle|database error|syntax error)",
            "XSS": r"(<script|alert\(|prompt\(|onerror=)",
            "LFI": r"(etc/passwd|windows/win.ini|\.\./)",
            "RCE": r"(system\(|exec\(|eval\()",
            "GIT": r"(git/HEAD|refs/heads/master)",
            "ENV": r"(DB_HOST|DB_NAME|DB_USER|DB_PASS|APP_KEY|SECRET)"
        }

        self.tech_patterns = {
            "WordPress": r"(wp-content|wp-includes|wp-json)",
            "Laravel": r"(laravel|csrf-token|_token)",
            "Django": r"(csrfmiddlewaretoken|django)",
            "React": r"(react|_reactRootContainer)",
            "Angular": r"(angular|ng-app)",
            "Vue": r"(vue|v-bind|v-for)",
            "Bootstrap": r"(bootstrap|data-bs-)",
            "jQuery": r"(jquery|\$\(document\))",
            "Nginx": r"(nginx|server: nginx)",
            "Apache": r"(apache|server: apache)"
        }

        self.total = len(self.dirs) + len(self.subdomains) + 20
        self.done = 0

    def print_progress(self):
        pct = int((self.done / self.total) * 100) if self.total else 0
        bar = "#" * int(pct/4) + "-" * (25 - int(pct/4))
        eta = "..." if self.done == 0 else f"{int((self.total - self.done) * (time.time()-self.start) / max(1, self.done))}s"
        print(f"\r[PROG] {bar} {pct}% | {self.done}/{self.total} | ETA: {eta}", end="")
        if pct == 100: print()

    def log(self, msg, status="info"):
        icons = {"info":"[*]", "success":"[+]", "error":"[-]", "warning":"[!]", "found":"[>]", "critical":"[!]"}
        print(f"{icons.get(status, '[*]')} {msg}")

    # ======================== DNS ========================
    def dns_scan(self):
        self.log("DNS bilgileri aliniyor...", "scan")
        try:
            ip = socket.gethostbyname(self.target)
            self.results["dns"] = {"ip": ip}
            self.log(f"IP: {ip}", "success")
            try:
                host = socket.gethostbyaddr(ip)[0]
                self.results["dns"]["hostname"] = host
                self.log(f"Hostname: {host}", "success")
            except: pass
        except Exception as e:
            self.log(f"DNS hatasi: {e}", "error")
        self.done += 1; self.print_progress()

    # ======================== PORT ========================
    def port_scan(self):
        self.log("Portlar taranıyor (15 port)...", "scan")
        ports = [21,22,23,25,80,110,139,143,443,445,993,995,3306,3389,8080]
        for p in ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.6)
                if s.connect_ex((self.target, p)) == 0:
                    self.results["ports"].append(p)
                    self.log(f"Port {p} ACIK", "found")
                s.close()
            except: pass
            self.done += 1; self.print_progress()

    # ======================== SSL ========================
    def ssl_scan(self):
        self.log("SSL kontrol ediliyor...", "scan")
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=self.target) as s:
                s.settimeout(3)
                s.connect((self.target, 443))
                cipher = s.cipher()[0]
                self.results["ssl"] = {"active": True, "cipher": cipher}
                self.log(f"SSL Aktif - {cipher}", "success")
        except:
            self.results["ssl"] = {"active": False}
            self.log("SSL yok", "warning")
        self.done += 1; self.print_progress()

    # ======================== HEADER ========================
    def header_scan(self):
        self.log("Header'lar aliniyor...", "scan")
        try:
            r = self.session.get(f"https://{self.target}", timeout=2, verify=False)
            headers = dict(r.headers)
            self.results["headers"] = headers
            for k, v in list(headers.items())[:6]:
                self.log(f"{k}: {v[:50]}", "found")
            if "Server" in headers:
                self.results["tech"].append(f"Server: {headers['Server']}")
            # WAF & Cloud
            combined = str(headers).lower()
            for waf, sigs in self.waf_sigs.items():
                if any(s in combined for s in sigs):
                    self.results["waf"] = waf
                    self.log(f"WAF: {waf}", "warning")
            for cloud, sigs in self.cloud_sigs.items():
                if any(s in combined for s in sigs):
                    self.results["cloud"] = cloud
                    self.log(f"Cloud: {cloud}", "found")
        except:
            try:
                r = self.session.get(f"http://{self.target}", timeout=2, verify=False)
                self.results["headers"] = dict(r.headers)
                self.log("HTTP header'lar alindi", "success")
            except:
                self.log("Header alinamadi", "error")
        self.done += 1; self.print_progress()

    # ======================== TEKNOLOJİ ========================
    def tech_scan(self):
        self.log("Teknolojiler tespit ediliyor...", "scan")
        try:
            r = self.session.get(f"https://{self.target}", timeout=2, verify=False)
            content = r.text
            for name, pattern in self.tech_patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    self.results["tech"].append(name)
                    self.log(f"Teknoloji: {name}", "found")
        except:
            pass
        self.done += 1; self.print_progress()

    # ======================== DİZİN ========================
    def dir_scan(self):
        self.log(f"Dizinler taranıyor ({len(self.dirs)})...", "scan")
        for d in self.dirs:
            found = False
            for proto in ["https", "http"]:
                try:
                    url = f"{proto}://{self.target}{d}"
                    r = self.session.get(url, timeout=1.5, verify=False, allow_redirects=False)
                    if r.status_code in [200, 301, 302, 403, 401, 405]:
                        self.results["dirs"].append({"path": d, "status": r.status_code})
                        self.log(f"{d} -> {r.status_code}", "found")
                        # Vuln kontrol
                        combined = (r.text + str(r.headers)).lower()
                        for vuln, pattern in self.vuln_patterns.items():
                            if re.search(pattern, combined, re.IGNORECASE):
                                self.results["vulns"].append({"url": url, "type": vuln})
                                self.log(f"{vuln} TESPIT! ({url})", "critical")
                        # Email
                        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r.text)
                        for e in emails[:3]:
                            if e not in self.results["emails"]:
                                self.results["emails"].append(e)
                                self.log(f"Email: {e}", "found")
                        found = True
                        break
                except:
                    continue
            self.done += 1
            self.print_progress()

    # ======================== SUBDOMAIN ========================
    def sub_scan(self):
        self.log(f"Subdomain'ler taranıyor ({len(self.subdomains)})...", "scan")
        for sub in self.subdomains:
            try:
                domain = f"{sub}.{self.target}"
                socket.setdefaulttimeout(1)
                socket.gethostbyname(domain)
                self.results["subdomains"].append(domain)
                self.log(f"Subdomain: {domain}", "found")
            except:
                pass
            self.done += 1
            self.print_progress()

    # ======================== RAPOR ========================
    def summary(self):
        elapsed = int(time.time() - self.start)
        print("\n" + "="*60)
        print(f"{BOLD}{C} TARAMA OZETI{N}")
        print("="*60)
        print(f"{Y}Süre:{N} {elapsed}s")
        print(f"{Y}Port:{N} {len(self.results['ports'])}")
        print(f"{Y}Dizin:{N} {len(self.results['dirs'])}")
        print(f"{Y}Subdomain:{N} {len(self.results['subdomains'])}")
        print(f"{Y}Vuln:{N} {len(self.results['vulns'])}")
        print(f"{Y}Email:{N} {len(self.results['emails'])}")
        print(f"{Y}WAF:{N} {self.results['waf'] or 'Yok'}")
        print(f"{Y}Cloud:{N} {self.results['cloud'] or 'Yok'}")
        print(f"{Y}Tech:{N} {', '.join(self.results['tech'][:5])}")
        print("="*60)
        if self.results['dirs']:
            print(f"\n{G}Dizinler:{N}")
            for d in self.results['dirs'][:10]:
                print(f"  [+] {d['path']} -> {d['status']}")
        if self.results['vulns']:
            print(f"\n{R}Vuln:{N}")
            for v in self.results['vulns'][:5]:
                print(f"  [!] {v['type']} -> {v['url']}")

    def save(self):
        fname = f"scan_{self.target}_{int(time.time())}.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
        self.log(f"Rapor: {fname}", "success")

    # ======================== RUN ========================
    def run(self):
        print(f"{BOLD}{M} SCANNER BASLADI (SIRALI){N}\n")
        self.dns_scan()
        self.port_scan()
        self.ssl_scan()
        self.header_scan()
        self.tech_scan()
        self.dir_scan()
        self.sub_scan()
        self.done = self.total
        self.print_progress()
        self.summary()
        if input("\nRaporu kaydet? (E/H): ").upper() == "E":
            self.save()


# ============================================================
# MAIN
# ============================================================
def main():
    print(f"{BOLD}╔═══════════════════════════════════════╗")
    print(f"║ {C}SCANNER iSH (SIRALI){BOLD}            ║")
    print(f"║ {Y}5 DAKIKADA BITER{BOLD}                ║")
    print("╚═══════════════════════════════════════╝\n")
    target = input("Hedef: ").strip() or "silvacheck.com"
    Scanner(target).run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCikis.")
    except Exception as e:
        print(f"\n{R}Hata: {e}{N}")
