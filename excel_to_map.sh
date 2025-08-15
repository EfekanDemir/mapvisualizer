#!/bin/bash

# =============================================================================
# Excel'den İnteraktif Harita Oluşturucu - Linux/macOS Script
# =============================================================================

# Renkli çıktı için ANSI kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Emojiler için Unicode desteği
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

clear

echo
echo "==============================================================================="
echo "🗺️  EXCEL'DEN İNTERAKTİF HARİTA OLUŞTURUCU"
echo "==============================================================================="
echo

# Python kontrolü
echo "🔍 Python kontrolü yapılıyor..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}❌ Python bulunamadı!${NC}"
        echo
        echo "Python yüklemek için:"
        echo "Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
        echo "CentOS/RHEL:   sudo yum install python3 python3-pip"
        echo "macOS:         brew install python3"
        echo "             veya https://python.org adresinden indirin"
        echo
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi
echo "✅ Python bulundu"
echo

# pip kontrolü
echo "🔍 pip kontrolü yapılıyor..."
if ! $PYTHON_CMD -m pip --version &> /dev/null; then
    echo -e "${RED}❌ pip bulunamadı!${NC}"
    echo
    echo "pip yüklemek için:"
    echo "Ubuntu/Debian: sudo apt install python3-pip"
    echo "CentOS/RHEL:   sudo yum install python3-pip"
    echo "macOS:         curl https://bootstrap.pypa.io/get-pip.py | python3"
    echo
    exit 1
fi
echo "✅ pip bulundu"
echo

# Dosya kontrolları
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ requirements.txt dosyası bulunamadı!${NC}"
    echo "Bu dosya aynı klasörde olmalı."
    echo
    exit 1
fi

if [ ! -f "excel_to_map.py" ]; then
    echo -e "${RED}❌ excel_to_map.py dosyası bulunamadı!${NC}"
    echo "Bu dosya aynı klasörde olmalı."
    echo
    exit 1
fi

# Gerekli paketlerin kontrolü
echo "🔍 Gerekli paketler kontrol ediliyor..."
if ! $PYTHON_CMD -c "import pandas, folium, numpy, openpyxl" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Bazı paketler eksik. Kuruluyor...${NC}"
    echo
    
    # Sanal ortam oluşturmayı dene
    if $PYTHON_CMD -m venv venv &> /dev/null; then
        echo "📦 Sanal ortam oluşturuldu"
        source venv/bin/activate
        pip install -r requirements.txt
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Paket kurulumu başarısız!${NC}"
            echo
            echo "Çözüm önerileri:"
            echo "1. İnternet bağlantınızı kontrol edin"
            echo "2. Sistem paketlerini kullanın:"
            echo "   Ubuntu/Debian: sudo apt install python3-pandas python3-numpy"
            echo "3. Manuel kurulum: pip3 install pandas folium numpy openpyxl"
            echo
            exit 1
        fi
        echo "✅ Paketler sanal ortama kuruldu"
    else
        # Sistem geneli kurulum dene
        $PYTHON_CMD -m pip install --user -r requirements.txt
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ Paket kurulumu başarısız!${NC}"
            echo
            echo "Çözüm önerileri:"
            echo "1. Sudo ile deneyin: sudo pip3 install -r requirements.txt"
            echo "2. Sistem paket yöneticisini kullanın"
            echo "3. Manuel kurulum yapın"
            echo
            exit 1
        fi
        echo "✅ Paketler kullanıcı alanına kuruldu"
    fi
else
    echo "✅ Tüm gerekli paketler mevcut"
fi
echo

# Excel dosyası kontrolü
echo "🔍 Excel dosyaları aranıyor..."
excel_files=(*.xlsx)
excel_count=${#excel_files[@]}

# Gerçek dosya sayısını kontrol et (glob expansion kontrolü)
if [ "${excel_files[0]}" = "*.xlsx" ]; then
    excel_count=0
fi

if [ $excel_count -eq 0 ]; then
    echo -e "${RED}❌ Bu klasörde .xlsx dosyası bulunamadı!${NC}"
    echo
    echo "Lütfen:"
    echo "1. Excel dosyalarınızı bu klasöre kopyalayın"
    echo "2. Dosyaların .xlsx uzantılı olduğundan emin olun"
    echo "3. Gerekli sütunların mevcut olduğunu kontrol edin:"
    echo "   - latitude  (zorunlu)"
    echo "   - longitude (zorunlu)"
    echo "   - title     (zorunlu)"
    echo "   - rank      (opsiyonel)"
    echo "   - url       (opsiyonel)"
    echo
    exit 1
fi

echo "✅ $excel_count adet Excel dosyası bulundu"
echo

# Python scriptini executable yap
chmod +x excel_to_map.py 2>/dev/null

# Ana program çalıştırma
echo "🚀 Harita oluşturucu başlatılıyor..."
echo
echo "==============================================================================="

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    python excel_to_map.py
    exit_code=$?
    deactivate
else
    $PYTHON_CMD excel_to_map.py
    exit_code=$?
fi

echo
echo "==============================================================================="

if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✅ İşlem başarıyla tamamlandı!${NC}"
    echo
    echo "📂 Bu klasörde .html uzantılı harita dosyanız oluşturuldu"
    echo "🌐 Harita otomatik olarak tarayıcınızda açıldı"
    echo
    echo "💡 İpucu: HTML dosyasını herhangi bir tarayıcıyla açabilirsiniz"
else
    echo -e "${RED}❌ İşlem sırasında hata oluştu!${NC}"
    echo
    echo "Hata giderme:"
    echo "1. Excel dosyanızın doğru formatta olduğundan emin olun"
    echo "2. Gerekli sütunların mevcut olduğunu kontrol edin"
    echo "3. Koordinat verilerinin sayısal olduğunu kontrol edin"
fi

echo
read -p "Devam etmek için Enter tuşuna basın..."