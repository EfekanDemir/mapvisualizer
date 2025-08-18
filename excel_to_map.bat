@echo off
chcp 65001 >nul
cls

:: =============================================================================
:: Excel'den İnteraktif Harita Oluşturucu - Windows Batch Dosyası
:: =============================================================================

echo.
echo ===============================================================================
echo 🗺️  EXCEL'DEN İNTERAKTİF HARİTA OLUŞTURUCU
echo ===============================================================================
echo.

:: Python kontrolü
echo 🔍 Python kontrolü yapılıyor...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python bulunamadı!
    echo.
    echo Python yüklemek için:
    echo 1. https://python.org adresine gidin
    echo 2. Python'ın en son sürümünü indirin
    echo 3. Yüklerken "Add Python to PATH" seçeneğini işaretleyin
    echo.
    pause
    exit /b 1
)
echo ✅ Python bulundu
echo.

:: pip kontrolü
echo 🔍 pip kontrolü yapılıyor...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip bulunamadı!
    echo pip'i yüklemek için Python'ı tekrar kurun
    pause
    exit /b 1
)
echo ✅ pip bulundu
echo.

:: Gereksinimler dosyası kontrolü
if not exist "requirements.txt" (
    echo ❌ requirements.txt dosyası bulunamadı!
    echo Bu dosya aynı klasörde olmalı.
    pause
    exit /b 1
)

:: Ana Python betiği kontrolü
if not exist "excel_to_map.py" (
    echo ❌ excel_to_map.py dosyası bulunamadı!
    echo Bu dosya aynı klasörde olmalı.
    pause
    exit /b 1
)

:: Paket kurulumu kontrolü
echo 🔍 Gerekli paketler kontrol ediliyor...
python -c "import pandas, folium, numpy, openpyxl" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Bazı paketler eksik. Kuruluyor...
    echo.
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Paket kurulumu başarısız!
        echo.
        echo Çözüm önerileri:
        echo 1. İnternet bağlantınızı kontrol edin
        echo 2. Yönetici olarak çalıştırın
        echo 3. Manuel kurulum: pip install pandas folium numpy openpyxl
        echo.
        pause
        exit /b 1
    )
    echo ✅ Paketler başarıyla kuruldu
) else (
    echo ✅ Tüm gerekli paketler mevcut
)
echo.

:: Excel dosyası kontrolü
echo 🔍 Excel dosyaları aranıyor...
set excel_count=0
for %%f in (*.xlsx) do (
    set /a excel_count+=1
)

if %excel_count%==0 (
    echo ❌ Bu klasörde .xlsx dosyası bulunamadı!
    echo.
    echo Lütfen:
    echo 1. Excel dosyalarınızı bu klasöre kopyalayın
    echo 2. Dosyaların .xlsx uzantılı olduğundan emin olun
    echo 3. Gerekli sütunların mevcut olduğunu kontrol edin:
    echo    - latitude  ^(zorunlu^)
    echo    - longitude ^(zorunlu^)
    echo    - title     ^(zorunlu^)
    echo    - rank      ^(opsiyonel^)
    echo    - url       ^(opsiyonel^)
    echo.
    pause
    exit /b 1
)

echo ✅ %excel_count% adet Excel dosyası bulundu
echo.

:: Ana program çalıştırma
echo 🚀 Harita oluşturucu başlatılıyor...
echo.
echo ===============================================================================
python ultra_modern_maps_visualizer.py
set exit_code=%errorlevel%

echo.
echo ===============================================================================

if %exit_code%==0 (
    echo ✅ İşlem başarıyla tamamlandı!
    echo.
    echo 📂 interactive_map.html dosyası oluşturuldu
    echo 🌐 Harita otomatik olarak tarayıcınızda açıldı
    echo.
    echo 💡 İpucu: HTML dosyasını herhangi bir tarayıcıyla açabilirsiniz
    echo 🎯 Özellikler: Modern Google Maps API, 3D görünüm, yoğunluk görselleştirmesi
) else (
    echo ❌ İşlem sırasında hata oluştu!
    echo.
    echo Hata giderme:
    echo 1. Excel dosyanızın doğru formatta olduğundan emin olun
    echo 2. Gerekli sütunların mevcut olduğunu kontrol edin
    echo 3. Koordinat verilerinin sayısal olduğunu kontrol edin
    echo 4. Google Maps API anahtarının geçerli olduğunu kontrol edin
)

echo.
echo Program sonlandırılıyor...
pause