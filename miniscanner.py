#!/usr/bin/env python3
# KSIB ULTRA MEGA SCANNER - iSH OPTİMİZE (5 DAKİKA)
# pip install requests beautifulsoup4

import socket, ssl, requests, json, sys, os, time, re, threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin
import urllib3
urllib3.disable_warnings()

# ============================================================
# RENKLER
# ============================================================
R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; B = "\033[94m"
M = "\033[95m"; C = "\033[96m"; W = "\033[97m"; N = "\033[0m"; BOLD = "\033[1m"

# ============================================================
# SCANNER
# ============================================================
class UltraMegaScanner:
    def __init__(self, target):
        self.target = target
        self.start_time = time.time()
        self.lock = threading.Lock()

        self.results = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "status": "Başlatıldı",
            "dns": {},
            "ports": [],
            "ssl": {},
            "headers": {},
            "cookies": [],
            "technologies": [],
            "directories": [],
            "subdomains": [],
            "vulnerabilities": [],
            "emails": [],
            "links": [],
            "forms": [],
            "waf": None,
            "cloud": None
        }

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
            "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        })
        self.session.timeout = 3

        # ============ KISALTILMIŞ WORDLIST'LER ============
        self.dirs = [
            "/admin", "/login", "/wp-admin", "/phpmyadmin", "/.git", "/.env", "/api",
            "/robots.txt", "/sitemap.xml", "/favicon.ico", "/backup", "/test", "/dev",
            "/wp-content", "/wp-includes", "/server-status", "/cgi-bin",
            "/user", "/profile", "/dashboard", "/shop", "/cart", "/checkout",
            "/phpinfo.php", "/info.php", "/config.php", "/index.php", "/index.html",
            "/.htaccess", "/web.config", "/composer.json", "/package.json"
        ]

        self.subdomains = [
            "www", "mail", "ftp", "dev", "test", "stage", "api", "admin", "cdn",
            "static", "blog", "shop", "docs", "support", "demo", "backup",
            "beta", "alpha", "preprod", "uat", "qa", "vpn", "secure", "portal",
            "gateway", "edge", "internal", "db", "mysql", "postgres", "mongodb",
            "redis", "elastic", "monitor", "grafana", "jenkins", "git", "svn",
            "auth", "oauth", "sso", "login"
        ]

        # Vuln pattern'ler (aynı)
        self.vuln_patterns = self._load_vuln_patterns()
        self.tech_patterns = self._load_tech_patterns()
        self.waf_signatures = self._load_waf_signatures()
        self.cloud_signatures = self._load_cloud_signatures()

        self.total_tasks = len(self.dirs) + len(self.subdomains) + 20
        self.completed_tasks = 0

        self._compile_regexes()

    # ======================== WORDLIST'LER ========================
    def _load_vuln_patterns(self):
        return {
            "SQL Injection": {
                "patterns": [r"(sql|mysql|postgresql|oracle|mssql|database error|syntax error)"],
                "severity": "Critical"
            },
            "XSS": {
                "patterns": [r"(<script|alert\(|prompt\(|onerror=|onload=)"],
                "severity": "High"
            },
            "LFI/RFI": {
                "patterns": [r"(etc/passwd|windows/win.ini|\.\./|include\()"],
                "severity": "Critical"
            },
            "RCE": {
                "patterns": [r"(system\(|exec\(|shell_exec\(|eval\()"],
                "severity": "Critical"
            },
            ".git Exposed": {
                "patterns": [r"(git/HEAD|refs/heads/master)"],
                "severity": "High"
            },
            ".env Exposed": {
                "patterns": [r"(DB_HOST|DB_NAME|DB_USER|DB_PASS|APP_KEY|SECRET)"],
                "severity": "Critical"
            },
            "Directory Listing": {
                "patterns": [r"(index of /|parent directory)"],
                "severity": "Medium"
            }
        }

    def _load_tech_patterns(self):
        return {
            "WordPress": r"(wp-content|wp-includes|wp-json)",
            "Laravel": r"(laravel|csrf-token|_token)",
            "Django": r"(csrfmiddlewaretoken|django)",
            "React": r"(react|_reactRootContainer)",
            "Angular": r"(angular|ng-app)",
            "Vue.js": r"(vue|v-bind|v-for)",
            "Bootstrap": r"(bootstrap|data-bs-)",
            "jQuery": r"(jquery|\$\(document\))",
            "Cloudflare": r"(cloudflare|cf-ray|__cfduid)",
            "Nginx": r"(nginx|server: nginx)",
            "Apache": r"(apache|server: apache)"
        }

    def _load_waf_signatures(self):
        return {
            "Cloudflare": ["cf-ray", "__cfduid", "Cloudflare"],
            "AWS WAF": ["x-amzn-RequestId", "AWSWAF"],
            "Sucuri": ["sucuri", "x-sucuri-id"],
            "ModSecurity": ["ModSecurity", "OWASP"]
        }

    def _load_cloud_signatures(self):
        return {
            "AWS": ["x-amz", "aws", "cloudfront"],
            "Google Cloud": ["x-gcs", "google-cloud"],
            "Azure": ["x-ms", "azure"],
            "Cloudflare": ["cf-", "cloudflare"],
            "Akamai": ["akamai", "x-ak"]
        }

    def _compile_regexes(self):
        for vuln_name, vuln_data in self.vuln_patterns.items():
            vuln_data["compiled"] = [re.compile(p, re.IGNORECASE) for p in vuln_data["patterns"]]
        self.compiled_tech = {name: re.compile(pattern, re.IGNORECASE) for name, pattern in self.tech_patterns.items()}
        self.email_re = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.link_re = re.compile(r'href=[\'"]?([^\'" >]+)')
        self.form_re = re.compile(r'<form', re.IGNORECASE)

    # ======================== PRINT / PROGRESS ========================
    def safe_print(self, msg, status="info"):
        icons = {"info": "[*]", "success": "[+]", "error": "[-]", "warning": "[!]", "scan": "[*]", "found": "[>]", "critical": "[!]"}
        with self.lock:
            print(f"{icons.get(status, '[*]')} {msg}")

    def print_progress(self):
        with self.lock:
            elapsed = int(time.time() - self.start_time)
            total = self.total_tasks
            done = self.completed_tasks
            pct = min(100, int((done / total) * 100)) if total > 0 else 0
            if done > 0 and elapsed > 0:
                eta = f"{int((total - done) * (elapsed / done))}s"
            else:
                eta = "..."
            bar = "#" * int(pct / 4) + "-" * (25 - int(pct / 4))
            print(f"\r[PROG] {bar} {pct}% | {done}/{total} | ETA: {eta}", end="")
            if pct == 100:
                print()

    # ======================== DNS ========================
    def dns_info(self):
        self.safe_print("DNS bilgileri aliniyor...", "scan")
        try:
            ip = socket.gethostbyname(self.target)
            self.results["dns"]["ip"] = ip
            self.safe_print(f"IP: {ip}", "success")
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                self.results["dns"]["hostname"] = hostname
                self.safe_print(f"Hostname: {hostname}", "success")
            except:
                pass
            try:
                import dns.resolver
                records = {}
                for rtype in ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]:
                    try:
                        answers = dns.resolver.resolve(self.target, rtype, lifetime=2)
                        records[rtype] = [str(r) for r in answers]
                    except:
                        pass
                self.results["dns"]["records"] = records
                for rtype, values in records.items():
                    self.safe_print(f"{rtype}: {', '.join(values[:3])}", "found")
            except:
                pass
        except Exception as e:
            self.safe_print(f"DNS hatasi: {e}", "error")
        with self.lock:
            self.completed_tasks += 1
        self.print_progress()

    # ======================== PORT TARAMA (20 PORT) ========================
    def port_scan(self):
        self.safe_print("Portlar taranıyor (20 port)...", "scan")
        ports = [21,22,23,25,53,80,110,139,143,443,445,993,995,3306,3389,5432,5900,6379,8080,8443]
        open_ports = []

        def scan_port(p):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.8)
                if s.connect_ex((self.target, p)) == 0:
                    s.close()
                    return p
                s.close()
            except:
                pass
            return None

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(scan_port, p) for p in ports]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    open_ports.append(result)
                    self.safe_print(f"Port {result} ACIK", "found")

        self.results["ports"] = open_ports
        with self.lock:
            self.completed_tasks += 1
        self.print_progress()

    # ======================== SSL ========================
    def ssl_analysis(self):
        self.safe_print("SSL sertifikasi analiz ediliyor...", "scan")
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=self.target) as s:
                s.settimeout(5)
                s.connect((self.target, 443))
                cert = s.getpeercert()
                cipher = s.cipher()
                self.results["ssl"] = {
                    "active": True,
                    "cipher": cipher[0] if cipher else '',
                    "protocol": s.version(),
                    "not_after": cert.get('notAfter', '')
                }
                self.safe_print(f"SSL Aktif - {cipher[0] if cipher else '?'}", "success")
        except:
            self.results["ssl"] = {"active": False}
            self.safe_print("SSL yok", "warning")
        with self.lock:
            self.completed_tasks += 1
        self.print_progress()

    # ======================== HEADER ========================
    def header_analysis(self):
        self.safe_print("Header'lar analiz ediliyor...", "scan")
        for protocol in ["https", "http"]:
            try:
                r = self.session.get(f"{protocol}://{self.target}", timeout=3, verify=False)
                headers = dict(r.headers)
                self.results["headers"] = headers
                for key, value in list(headers.items())[:8]:
                    self.safe_print(f"{key}: {value[:50]}", "found")
                if "Server" in headers:
                    self.safe_print(f"Server: {headers['Server']}", "found")
                cookies = r.cookies.get_dict()
                if cookies:
                    self.results["cookies"] = cookies
                combined = str(headers).lower() + (r.text[:5000]).lower()
                for waf, sigs in self.waf_signatures.items():
                    for sig in sigs:
                        if sig.lower() in combined:
                            self.results["waf"] = waf
                            self.safe_print(f"WAF: {waf}", "warning")
                for cloud, sigs in self.cloud_signatures.items():
                    for sig in sigs:
                        if sig.lower() in combined:
                            self.results["cloud"] = cloud
                            self.safe_print(f"Cloud: {cloud}", "found")
                break
            except:
                continue
        with self.lock:
            self.completed_tasks += 1
        self.print_progress()

    # ======================== TEKNOLOJİ ========================
    def tech_detect(self):
        self.safe_print("Teknolojiler tespit ediliyor...", "scan")
        techs = set()
        try:
            r = self.session.get(f"https://{self.target}", timeout=3, verify=False)
            content = r.text
            if "Server" in r.headers:
                techs.add(f"Server: {r.headers['Server']}")
            for name, compiled in self.compiled_tech.items():
                if compiled.search(content) or compiled.search(str(r.headers)):
                    techs.add(name)
                    self.safe_print(f"Teknoloji: {name}", "found")
            self.results["technologies"] = list(techs)
        except Exception as e:
            self.safe_print(f"Tech detect hatasi: {e}", "warning")
        with self.lock:
            self.completed_tasks += 1
        self.print_progress()

    # ======================== DİZİN TARAMA ========================
    def dir_scan(self):
        self.safe_print(f"Dizinler taranıyor ({len(self.dirs)} adet)...", "scan")

        def scan_dir(path):
            for protocol in ["https", "http"]:
                try:
                    url = f"{protocol}://{self.target}{path}"
                    r = self.session.get(url, timeout=2, verify=False, allow_redirects=False)
                    if r.status_code in [200, 301, 302, 403, 401, 405]:
                        with self.lock:
                            self.results["directories"].append({"path": path, "status": r.status_code})
                            self.safe_print(f"{path} -> {r.status_code}", "found")
                            self.check_vulnerability(url, r.text, r.headers)
                            # Extract info
                            for email in self.email_re.findall(r.text)[:5]:
                                if email not in self.results["emails"]:
                                    self.results["emails"].append(email)
                                    self.safe_print(f"Email: {email}", "found")
                            for link in self.link_re.findall(r.text)[:5]:
                                if link not in self.results["links"]:
                                    self.results["links"].append(link)
                            if self.form_re.search(r.text):
                                self.results["forms"].append(url)
                                self.safe_print(f"Form: {url}", "found")
                        break
                except:
                    continue
            with self.lock:
                self.completed_tasks += 1
                self.print_progress()

        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(scan_dir, self.dirs)

        self.safe_print(f"{len(self.results['directories'])} dizin bulundu", "success")

    # ======================== SUBDOMAIN ========================
    def subdomain_scan(self):
        self.safe_print(f"Subdomain'ler taranıyor ({len(self.subdomains)} adet)...", "scan")
        found = []

        def scan_sub(sub):
            try:
                domain = f"{sub}.{self.target}"
                socket.setdefaulttimeout(1.5)
                socket.gethostbyname(domain)
                with self.lock:
                    found.append(domain)
                    self.safe_print(f"Subdomain: {domain}", "found")
            except:
                pass
            with self.lock:
                self.completed_tasks += 1
                self.print_progress()

        with ThreadPoolExecutor(max_workers=4) as executor:
            executor.map(scan_sub, self.subdomains)

        self.results["subdomains"] = found
        self.safe_print(f"{len(found)} subdomain bulundu", "success")

    # ======================== VULN KONTROL ========================
    def check_vulnerability(self, url, content, headers):
        combined = (content + str(headers)).lower()
        for vuln_name, vuln_data in self.vuln_patterns.items():
            for compiled in vuln_data["compiled"]:
                if compiled.search(combined):
                    with self.lock:
                        self.results["vulnerabilities"].append({
                            "url": url,
                            "type": vuln_name,
                            "severity": vuln_data["severity"]
                        })
                        self.safe_print(f"{vuln_name} TESPIT EDILDI! ({url})", "critical")
                    break

    # ======================== RAPOR ========================
    def print_summary(self):
        elapsed = int(time.time() - self.start_time)
        print("\n" + "="*60)
        print(f"{BOLD}{C} TARAMA OZETI{N}")
        print("="*60)
        print(f"{Y}Süre:{N} {elapsed} saniye")
        print(f"{Y}Hedef:{N} {self.target}")
        print(f"{Y}Acik Port:{N} {len(self.results['ports'])}")
        print(f"{Y}Dizin:{N} {len(self.results['directories'])}")
        print(f"{Y}Guvenlik Acigi:{N} {len(self.results['vulnerabilities'])}")
        print(f"{Y}Subdomain:{N} {len(self.results['subdomains'])}")
        print(f"{Y}Teknoloji:{N} {len(self.results['technologies'])}")
        print(f"{Y}Email:{N} {len(self.results['emails'])}")
        print("="*60)

        critical = [v for v in self.results['vulnerabilities'] if v['severity'] == 'Critical']
        if critical:
            print(f"\n{R}KRITIK GUVENLIK ACIKLARI:{N}")
            for v in critical:
                print(f"  [!] {v['type']} -> {v['url']}")

        if self.results['emails']:
            print(f"\n{C}EMAILLER:{N}")
            for email in self.results['emails'][:5]:
                print(f"  [>] {email}")

        interesting = [d for d in self.results['directories'] if d['status'] in [200, 403]]
        if interesting:
            print(f"\n{G}ONEMLI DIZINLER:{N}")
            for d in interesting[:10]:
                print(f"  [+] {d['path']} -> {d['status']}")
        print("="*60)

    def save_report(self):
        filename = f"scan_{self.target}_{int(time.time())}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
        self.safe_print(f"Rapor kaydedildi: {filename}", "success")

    # ======================== MAIN SCAN ========================
    def full_scan(self):
        print(f"\n{BOLD}{M} ULTRA MEGA SCANNER (iSH OPTIMIZE){N}")
        print(f"{B}Target: {self.target}{N}")
        print(f"{B}Baslangic: {datetime.now().strftime('%H:%M:%S')}{N}\n")

        self.print_progress()
        self.dns_info()
        self.port_scan()
        self.ssl_analysis()
        self.header_analysis()
        self.tech_detect()
        self.dir_scan()
        self.subdomain_scan()

        self.results["status"] = "Tamamlandi"
        with self.lock:
            self.completed_tasks = self.total_tasks
        self.print_progress()

        self.print_summary()
        if input("\nRaporu kaydet? (E/H): ").upper() == "E":
            self.save_report()


# ============================================================
# MAIN
# ============================================================
def main():
    print(f"""{BOLD}
╔═══════════════════════════════════════════════════════════╗
║  {C} ULTRA MEGA SCANNER (iSH OPTIMIZE){C}                    ║
║  {Y}5 DAKIKADA TAMAMLANIR{Y}                                  ║
╚═══════════════════════════════════════════════════════════╝
{N}""")

    target = input("Hedef (domain/IP): ").strip()
    if not target:
        target = "silvacheck.com"

    scanner = UltraMegaScanner(target)
    scanner.full_scan()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCikis yapiliyor...")
    except Exception as e:
        print(f"\n{R}Hata: {e}{N}")
